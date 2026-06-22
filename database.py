"""
Асинхронный слой работы с базой (SQLite через aiosqlite).
Хранит пользователей, их настройки, историю загрузок и статистику.
"""
from datetime import datetime, date

import aiosqlite

from config import DATABASE_PATH


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                user_id      INTEGER PRIMARY KEY,
                username     TEXT,
                first_name   TEXT,
                language     TEXT    DEFAULT 'ru',
                quality      TEXT    DEFAULT 'best',
                fmt          TEXT    DEFAULT 'video',
                is_banned    INTEGER DEFAULT 0,
                joined_at    TEXT,
                last_active  TEXT
            )
            """
        )
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS downloads (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER,
                url         TEXT,
                title       TEXT,
                site        TEXT,
                fmt         TEXT,
                file_size   INTEGER,
                created_at  TEXT
            )
            """
        )
        await db.execute("CREATE INDEX IF NOT EXISTS idx_dl_user ON downloads(user_id)")
        await db.commit()


async def add_user(user_id, username, first_name):
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO users (user_id, username, first_name, joined_at, last_active)
            VALUES (?, ?, ?, ?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
                username    = excluded.username,
                first_name  = excluded.first_name,
                last_active = excluded.last_active
            """,
            (user_id, username, first_name, now, now),
        )
        await db.commit()


async def get_user(user_id):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute("SELECT * FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return dict(row) if row else None


async def set_field(user_id, field, value):
    if field not in ("language", "quality", "fmt"):
        raise ValueError("bad field")
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(f"UPDATE users SET {field}=? WHERE user_id=?", (value, user_id))
        await db.commit()


async def set_banned(user_id, banned: bool):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            "UPDATE users SET is_banned=? WHERE user_id=?",
            (1 if banned else 0, user_id),
        )
        await db.commit()


async def is_banned(user_id) -> bool:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT is_banned FROM users WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return bool(row[0]) if row else False


async def all_user_ids():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT user_id FROM users WHERE is_banned=0") as cur:
            return [r[0] for r in await cur.fetchall()]


async def add_download(user_id, url, title, site, fmt, file_size):
    now = datetime.utcnow().isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute(
            """
            INSERT INTO downloads (user_id, url, title, site, fmt, file_size, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (user_id, url, title, site, fmt, file_size, now),
        )
        await db.commit()


async def user_history(user_id, limit=10):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT title, site, fmt, created_at FROM downloads "
            "WHERE user_id=? ORDER BY id DESC LIMIT ?",
            (user_id, limit),
        ) as cur:
            return [dict(r) async for r in cur]


async def user_dl_count(user_id) -> int:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async with db.execute("SELECT COUNT(*) FROM downloads WHERE user_id=?", (user_id,)) as cur:
            row = await cur.fetchone()
            return row[0] if row else 0


async def get_stats() -> dict:
    async with aiosqlite.connect(DATABASE_PATH) as db:
        async def scalar(query, *args):
            async with db.execute(query, args) as cur:
                row = await cur.fetchone()
                return row[0] if row and row[0] is not None else 0

        users = await scalar("SELECT COUNT(*) FROM users")
        banned = await scalar("SELECT COUNT(*) FROM users WHERE is_banned=1")
        total_dl = await scalar("SELECT COUNT(*) FROM downloads")
        today = date.today().isoformat()
        dl_today = await scalar(
            "SELECT COUNT(*) FROM downloads WHERE substr(created_at,1,10)=?", today
        )
        total_size = await scalar("SELECT COALESCE(SUM(file_size),0) FROM downloads")

        top_sites = []
        async with db.execute(
            "SELECT site, COUNT(*) c FROM downloads "
            "WHERE site IS NOT NULL GROUP BY site ORDER BY c DESC LIMIT 5"
        ) as cur:
            top_sites = [(r[0], r[1]) async for r in cur]

        return {
            "users": users,
            "banned": banned,
            "total_dl": total_dl,
            "dl_today": dl_today,
            "total_size": total_size,
            "top_sites": top_sites,
        }
