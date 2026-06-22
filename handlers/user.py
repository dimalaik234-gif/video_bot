"""Хендлеры для обычных пользователей: команды, превью и скачивание."""
import os

from aiogram import Bot, F, Router
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command, CommandStart
from aiogram.types import CallbackQuery, FSInputFile, Message

import database as db
import downloader as dl
import keyboards as kb
from config import ADMIN_IDS, MAX_FILE_SIZE, PLAYLIST_LIMIT, REQUIRED_CHANNEL
from locales import t
from utils import (
    LinkCache,
    build_caption,
    build_info_text,
    esc,
    find_urls,
    human_size,
    progress_bar,
)

router = Router()
cache = LinkCache()


# ─── вспомогательное ─────────────────────────────────────────────────────────
async def get_lang(user_id) -> str:
    u = await db.get_user(user_id)
    return (u or {}).get("language", "ru")


async def safe_delete(msg):
    try:
        await msg.delete()
    except Exception:
        pass


async def check_sub(bot: Bot, user_id) -> bool:
    if not REQUIRED_CHANNEL or user_id in ADMIN_IDS:
        return True
    try:
        m = await bot.get_chat_member(REQUIRED_CHANNEL, user_id)
        return m.status in {
            ChatMemberStatus.MEMBER,
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.CREATOR,
        }
    except Exception:
        return False


# ─── команды ─────────────────────────────────────────────────────────────────
@router.message(CommandStart())
async def cmd_start(message: Message):
    lang = await get_lang(message.from_user.id)
    await message.answer(t("start", lang, name=esc(message.from_user.first_name or "")))


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(t("help", await get_lang(message.from_user.id)))


@router.message(Command("settings"))
async def cmd_settings(message: Message):
    lang = await get_lang(message.from_user.id)
    u = await db.get_user(message.from_user.id) or {}
    await message.answer(
        t("settings", lang, lang=lang, quality=u.get("quality", "best"), fmt=u.get("fmt", "video")),
        reply_markup=kb.settings_kb(lang),
    )


@router.message(Command("lang"))
async def cmd_lang(message: Message):
    lang = await get_lang(message.from_user.id)
    await message.answer(t("choose_lang", lang), reply_markup=kb.lang_kb())


@router.message(Command("stats"))
async def cmd_stats(message: Message):
    lang = await get_lang(message.from_user.id)
    count = await db.user_dl_count(message.from_user.id)
    u = await db.get_user(message.from_user.id) or {}
    joined = (u.get("joined_at") or "")[:10]
    await message.answer(t("my_stats", lang, count=count, joined=joined))


@router.message(Command("history"))
async def cmd_history(message: Message):
    lang = await get_lang(message.from_user.id)
    rows = await db.user_history(message.from_user.id, 10)
    if not rows:
        await message.answer(t("history_empty", lang))
        return
    lines = [t("history_title", lang)]
    for r in rows:
        title = esc((r["title"] or "—")[:45])
        lines.append(f"• <b>{title}</b> — {esc(r['site'])} ({esc(r['fmt'])}) — {r['created_at'][:10]}")
    await message.answer("\n".join(lines))


# ─── настройки (callbacks) ───────────────────────────────────────────────────
@router.callback_query(F.data == "set|lang")
async def open_lang(c: CallbackQuery):
    lang = await get_lang(c.from_user.id)
    await c.message.edit_text(t("choose_lang", lang), reply_markup=kb.lang_kb())
    await c.answer()


@router.callback_query(F.data == "set|quality")
async def open_quality(c: CallbackQuery):
    lang = await get_lang(c.from_user.id)
    await c.message.edit_text(t("choose_quality", lang), reply_markup=kb.quality_kb(lang))
    await c.answer()


@router.callback_query(F.data == "set|fmt")
async def open_fmt(c: CallbackQuery):
    lang = await get_lang(c.from_user.id)
    await c.message.edit_text(t("choose_fmt", lang), reply_markup=kb.fmt_kb(lang))
    await c.answer()


@router.callback_query(F.data == "set|back")
async def back_to_settings(c: CallbackQuery):
    lang = await get_lang(c.from_user.id)
    u = await db.get_user(c.from_user.id) or {}
    await c.message.edit_text(
        t("settings", lang, lang=lang, quality=u.get("quality", "best"), fmt=u.get("fmt", "video")),
        reply_markup=kb.settings_kb(lang),
    )
    await c.answer()


@router.callback_query(F.data.startswith("lang|"))
async def set_lang(c: CallbackQuery):
    lang = c.data.split("|", 1)[1]
    await db.set_field(c.from_user.id, "language", lang)
    await c.message.edit_text(t("lang_saved", lang), reply_markup=kb.settings_kb(lang))
    await c.answer("✅")


@router.callback_query(F.data.startswith("q|"))
async def set_quality(c: CallbackQuery):
    val = c.data.split("|", 1)[1]
    await db.set_field(c.from_user.id, "quality", val)
    lang = await get_lang(c.from_user.id)
    await c.message.edit_text(t("quality_saved", lang), reply_markup=kb.settings_kb(lang))
    await c.answer("✅")


@router.callback_query(F.data.startswith("f|"))
async def set_fmt(c: CallbackQuery):
    val = c.data.split("|", 1)[1]
    await db.set_field(c.from_user.id, "fmt", val)
    lang = await get_lang(c.from_user.id)
    await c.message.edit_text(t("fmt_saved", lang), reply_markup=kb.settings_kb(lang))
    await c.answer("✅")


# ─── подписка ────────────────────────────────────────────────────────────────
@router.callback_query(F.data == "sub|check")
async def sub_check(c: CallbackQuery, bot: Bot):
    lang = await get_lang(c.from_user.id)
    if await check_sub(bot, c.from_user.id):
        await c.message.edit_text(t("sub_ok", lang))
        await c.answer("✅")
    else:
        await c.answer(t("sub_recheck", lang), show_alert=True)


# ─── приём ссылок ────────────────────────────────────────────────────────────
@router.message(F.text)
async def on_text(message: Message, bot: Bot):
    if message.text.startswith("/"):
        return  # неизвестные команды игнорируем
    lang = await get_lang(message.from_user.id)
    urls = find_urls(message.text)
    if not urls:
        await message.answer(t("send_link", lang))
        return
    url = urls[0]

    if not await check_sub(bot, message.from_user.id):
        await message.answer(
            t("sub_need", lang), reply_markup=kb.sub_kb(REQUIRED_CHANNEL, lang)
        )
        return

    status = await message.answer(t("getting_info", lang))

    # Плейлист? (не трогаем одиночные ссылки вида watch?v=...&list=...)
    is_watch = "watch?v=" in url or "youtu.be/" in url
    pl = None
    if not is_watch:
        try:
            pl = await dl.get_playlist(url)
        except Exception:
            pl = None

    if pl and len(pl["urls"]) > 1:
        urls_capped = pl["urls"][:PLAYLIST_LIMIT]
        token = cache.put({"type": "playlist", "urls": urls_capped, "title": pl["title"]})
        await status.edit_text(
            t("playlist_found", lang, title=esc(pl["title"]), n=len(pl["urls"])),
            reply_markup=kb.playlist_kb(token, len(urls_capped), lang),
        )
        return

    try:
        info = await dl.extract_info(url)
    except Exception:
        info = None
    if not info:
        await status.edit_text(t("err_info", lang))
        return

    token = cache.put({"type": "single", "url": url, "info": info})
    caption = build_caption(info, lang)
    markup = kb.format_kb(token, info, lang)
    thumb = info.get("thumbnail")
    await safe_delete(status)

    if thumb:
        try:
            await message.answer_photo(photo=thumb, caption=caption, reply_markup=markup)
            return
        except Exception:
            pass
    await message.answer(caption, reply_markup=markup)


# ─── скачивание (single) ─────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("dl|"))
async def on_download(c: CallbackQuery, bot: Bot):
    lang = await get_lang(c.from_user.id)
    try:
        _, token, action = c.data.split("|", 2)
    except ValueError:
        await c.answer()
        return

    entry = cache.get(token)
    if not entry or entry.get("type") != "single":
        await c.answer(t("session_expired", lang), show_alert=True)
        return
    url, info = entry["url"], entry["info"]
    await c.answer()

    # ИНФО
    if action == "info":
        await c.message.answer(build_info_text(info, lang))
        return

    # ОБЛОЖКА
    if action == "thumb":
        thumb = info.get("thumbnail")
        if thumb:
            try:
                await c.message.answer_photo(thumb, caption="🖼 " + esc(info.get("title") or ""))
            except Exception:
                await c.message.answer(thumb)
        else:
            await c.message.answer(t("no_thumb", lang))
        return

    # СУБТИТРЫ
    if action == "subs":
        status = await c.message.answer(t("getting_subs", lang))
        try:
            files = [f for f in (await dl.download_subtitles(url)) if os.path.exists(f)]
        except Exception:
            files = []
        if not files:
            await status.edit_text(t("no_subs", lang))
            return
        await safe_delete(status)
        for f in files:
            try:
                await bot.send_document(
                    c.message.chat.id, FSInputFile(f), caption="📝 " + esc(os.path.basename(f))
                )
            finally:
                dl.cleanup(f)
        return

    # ВИДЕО / АУДИО
    audio_only = action == "mp3"
    quality = action if (action.isdigit() or action == "best") else "best"
    status = await c.message.answer(t("downloading", lang))

    async def status_cb(progress):
        if progress.get("phase") == "convert":
            txt = t("converting", lang)
        else:
            txt = t(
                "downloading_p",
                lang,
                bar=progress_bar(progress["percent"]),
                p=int(progress["percent"]),
                speed=progress["speed"] or "—",
                eta=progress["eta"] or "—",
            )
        try:
            await status.edit_text(txt)
        except Exception:
            pass

    try:
        filepath, dinfo = await dl.download_with_progress(url, quality, audio_only, status_cb)
    except Exception:
        await status.edit_text(t("err_download", lang))
        return

    if not filepath or not os.path.exists(filepath):
        await status.edit_text(t("err_download", lang))
        return

    size = os.path.getsize(filepath)
    if size > MAX_FILE_SIZE:
        dl.cleanup(filepath)
        await status.edit_text(
            t("too_large", lang, size=human_size(size), limit=human_size(MAX_FILE_SIZE))
        )
        return

    await status.edit_text(t("uploading", lang))
    title = info.get("title") or "video"
    site = info.get("extractor_key") or "—"
    duration = int(info.get("duration") or 0) or None

    try:
        if audio_only:
            await bot.send_audio(
                c.message.chat.id,
                FSInputFile(filepath),
                title=title,
                performer=info.get("uploader") or info.get("channel") or "",
                duration=duration,
                caption=f"🎵 {esc(title)}",
            )
        else:
            await bot.send_video(
                c.message.chat.id,
                FSInputFile(filepath),
                caption=f"🎬 {esc(title)}",
                duration=duration,
                width=info.get("width") or None,
                height=info.get("height") or None,
                supports_streaming=True,
            )
    except Exception:
        try:
            await bot.send_document(
                c.message.chat.id, FSInputFile(filepath), caption=f"📁 {esc(title)}"
            )
        except Exception:
            await status.edit_text(t("err_upload", lang))
            dl.cleanup(filepath)
            return

    await safe_delete(status)
    await db.add_download(
        c.from_user.id, url, title, site, ("mp3" if audio_only else quality), size
    )
    dl.cleanup(filepath)


# ─── скачивание плейлиста ────────────────────────────────────────────────────
@router.callback_query(F.data.startswith("pl|"))
async def on_playlist(c: CallbackQuery, bot: Bot):
    lang = await get_lang(c.from_user.id)
    try:
        _, token, _action = c.data.split("|", 2)
    except ValueError:
        await c.answer()
        return
    entry = cache.get(token)
    if not entry or entry.get("type") != "playlist":
        await c.answer(t("session_expired", lang), show_alert=True)
        return
    await c.answer()

    urls = entry["urls"][:PLAYLIST_LIMIT]
    status = await c.message.answer(t("pl_start", lang, n=len(urls)))
    ok = 0
    for i, u in enumerate(urls, 1):
        try:
            await status.edit_text(t("pl_progress", lang, i=i, n=len(urls)))
        except Exception:
            pass
        try:
            filepath, dinfo = await dl.download_with_progress(u, "720", False, None)
        except Exception:
            continue
        if not filepath or not os.path.exists(filepath):
            continue
        size = os.path.getsize(filepath)
        if size > MAX_FILE_SIZE:
            dl.cleanup(filepath)
            continue
        title = (dinfo.get("title") if isinstance(dinfo, dict) else None) or "video"
        site = (dinfo.get("extractor_key") if isinstance(dinfo, dict) else None) or "—"
        try:
            await bot.send_video(
                c.message.chat.id,
                FSInputFile(filepath),
                caption=f"🎬 {esc(title)}",
                supports_streaming=True,
            )
            ok += 1
            await db.add_download(c.from_user.id, u, title, site, "720", size)
        except Exception:
            try:
                await bot.send_document(c.message.chat.id, FSInputFile(filepath))
                ok += 1
            except Exception:
                pass
        finally:
            dl.cleanup(filepath)

    await status.edit_text(t("pl_done", lang, ok=ok, n=len(urls)))
