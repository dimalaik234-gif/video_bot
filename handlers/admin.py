"""Хендлеры админ-панели."""
import asyncio

from aiogram import Bot, F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

import database as db
import keyboards as kb
from config import ADMIN_IDS
from utils import esc, human_size

router = Router()


class AdminSG(StatesGroup):
    broadcast = State()


def is_admin(user_id) -> bool:
    return user_id in ADMIN_IDS


@router.message(Command("admin"))
async def admin_panel(message: Message):
    if not is_admin(message.from_user.id):
        return
    await message.answer("🛠 <b>Админ-панель</b>", reply_markup=kb.admin_kb())


@router.callback_query(F.data == "adm|stats")
async def adm_stats(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer()
        return
    s = await db.get_stats()
    top = "\n".join(
        f"  {i + 1}. {esc(site)} — {cnt}" for i, (site, cnt) in enumerate(s["top_sites"])
    ) or "  —"
    text = (
        "📊 <b>Статистика бота</b>\n\n"
        f"👥 Пользователей: <b>{s['users']}</b>\n"
        f"🚫 Забанено: <b>{s['banned']}</b>\n"
        f"📥 Всего загрузок: <b>{s['total_dl']}</b>\n"
        f"📅 Сегодня: <b>{s['dl_today']}</b>\n"
        f"💾 Объём данных: <b>{human_size(s['total_size'])}</b>\n\n"
        f"🌐 <b>Топ источников:</b>\n{top}"
    )
    try:
        await c.message.edit_text(text, reply_markup=kb.admin_kb())
    except Exception:
        await c.message.answer(text, reply_markup=kb.admin_kb())
    await c.answer()


@router.callback_query(F.data == "adm|broadcast")
async def adm_broadcast_start(c: CallbackQuery, state: FSMContext):
    if not is_admin(c.from_user.id):
        await c.answer()
        return
    await state.set_state(AdminSG.broadcast)
    await c.message.answer(
        "✉️ Пришли сообщение для рассылки (текст / фото / видео).\n"
        "Оно будет скопировано всем пользователям.\n"
        "Отмена — /cancel"
    )
    await c.answer()


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    if await state.get_state():
        await state.clear()
        await message.answer("❌ Отменено.")


@router.message(StateFilter(AdminSG.broadcast))
async def do_broadcast(message: Message, state: FSMContext, bot: Bot):
    if not is_admin(message.from_user.id):
        await state.clear()
        return
    await state.clear()
    ids = await db.all_user_ids()
    sent = failed = 0
    note = await message.answer(f"📤 Рассылка началась… (0/{len(ids)})")
    for i, uid in enumerate(ids, 1):
        try:
            await message.copy_to(uid)
            sent += 1
        except Exception:
            failed += 1
        if i % 25 == 0:
            try:
                await note.edit_text(f"📤 {i}/{len(ids)}…")
            except Exception:
                pass
        await asyncio.sleep(0.05)  # бережём лимиты Telegram (~20-30 msg/sec)
    await note.edit_text(
        f"✅ Рассылка завершена.\nОтправлено: <b>{sent}</b>\nОшибок: <b>{failed}</b>"
    )


@router.message(Command("ban"))
async def cmd_ban(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].lstrip("-").isdigit():
        await message.answer("Использование: <code>/ban &lt;user_id&gt;</code>")
        return
    uid = int(parts[1])
    await db.set_banned(uid, True)
    await message.answer(f"🚫 Пользователь <code>{uid}</code> заблокирован.")


@router.message(Command("unban"))
async def cmd_unban(message: Message):
    if not is_admin(message.from_user.id):
        return
    parts = message.text.split()
    if len(parts) < 2 or not parts[1].lstrip("-").isdigit():
        await message.answer("Использование: <code>/unban &lt;user_id&gt;</code>")
        return
    uid = int(parts[1])
    await db.set_banned(uid, False)
    await message.answer(f"✅ Пользователь <code>{uid}</code> разблокирован.")
