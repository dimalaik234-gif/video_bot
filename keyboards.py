"""Inline-клавиатуры."""
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from locales import t

# Лестница качеств и их подписи
LADDER = [2160, 1440, 1080, 720, 480, 360]
LABELS = {2160: "4K", 1440: "1440p", 1080: "1080p", 720: "720p", 480: "480p", 360: "360p"}


def _available_heights(info: dict):
    heights = set()
    for f in (info.get("formats") or []):
        h = f.get("height")
        if h:
            heights.add(h)
    return heights


def format_kb(token: str, info: dict, lang: str = "ru") -> InlineKeyboardMarkup:
    """Кнопки выбора формата под превью видео."""
    b = InlineKeyboardBuilder()
    heights = _available_heights(info)
    maxh = max(heights) if heights else None
    shown = [h for h in LADDER if (maxh is None or h <= maxh)]
    if not shown:
        shown = [720, 360]

    b.button(text="🏆 Лучшее", callback_data=f"dl|{token}|best")
    for h in shown:
        b.button(text=f"📹 {LABELS[h]}", callback_data=f"dl|{token}|{h}")
    b.button(text="🎵 MP3", callback_data=f"dl|{token}|mp3")
    b.button(text="🖼 Обложка", callback_data=f"dl|{token}|thumb")
    b.button(text="📝 Субтитры", callback_data=f"dl|{token}|subs")
    b.button(text="ℹ️ Инфо", callback_data=f"dl|{token}|info")
    b.adjust(2)
    return b.as_markup()


def playlist_kb(token: str, n: int, lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("btn_dl_all", lang, n=n), callback_data=f"pl|{token}|all")
    return b.as_markup()


def settings_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text=t("btn_lang", lang), callback_data="set|lang")
    b.button(text=t("btn_quality", lang), callback_data="set|quality")
    b.button(text=t("btn_fmt", lang), callback_data="set|fmt")
    b.adjust(1)
    return b.as_markup()


def lang_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🇷🇺 Русский", callback_data="lang|ru")
    b.button(text="🇬🇧 English", callback_data="lang|en")
    b.button(text="⬅️", callback_data="set|back")
    b.adjust(2, 1)
    return b.as_markup()


def quality_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="🏆 Лучшее", callback_data="q|best")
    for h in [1080, 720, 480, 360]:
        b.button(text=LABELS[h], callback_data=f"q|{h}")
    b.button(text=t("btn_back", lang), callback_data="set|back")
    b.adjust(2)
    return b.as_markup()


def fmt_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📹 Видео", callback_data="f|video")
    b.button(text="🎵 Аудио (MP3)", callback_data="f|audio")
    b.button(text=t("btn_back", lang), callback_data="set|back")
    b.adjust(2, 1)
    return b.as_markup()


def sub_kb(channel: str, lang: str = "ru") -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    link = channel
    if channel.startswith("@"):
        link = f"https://t.me/{channel[1:]}"
    b.button(text=t("btn_join", lang), url=link)
    b.button(text=t("btn_check", lang), callback_data="sub|check")
    b.adjust(1)
    return b.as_markup()


def admin_kb() -> InlineKeyboardMarkup:
    b = InlineKeyboardBuilder()
    b.button(text="📊 Статистика", callback_data="adm|stats")
    b.button(text="✉️ Рассылка", callback_data="adm|broadcast")
    b.adjust(1)
    return b.as_markup()
