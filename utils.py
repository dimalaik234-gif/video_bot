"""Вспомогательные функции и кэш ссылок."""
import re
import secrets
from collections import OrderedDict

# Поиск ссылок в тексте сообщения
URL_RE = re.compile(r"https?://[^\s<>\"']+")


def find_urls(text: str):
    return URL_RE.findall(text or "")


def esc(s) -> str:
    """Экранирование HTML для безопасной вставки в сообщения."""
    return (
        str(s)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def human_size(num) -> str:
    try:
        num = float(num)
    except (TypeError, ValueError):
        return "—"
    if not num:
        return "—"
    for unit in ["Б", "КБ", "МБ", "ГБ", "ТБ"]:
        if abs(num) < 1024:
            return f"{num:.1f} {unit}"
        num /= 1024
    return f"{num:.1f} ПБ"


def human_duration(seconds) -> str:
    try:
        seconds = int(seconds)
    except (TypeError, ValueError):
        return "—"
    h, rem = divmod(seconds, 3600)
    m, s = divmod(rem, 60)
    if h:
        return f"{h}:{m:02d}:{s:02d}"
    return f"{m}:{s:02d}"


def human_number(n) -> str:
    try:
        n = int(n)
    except (TypeError, ValueError):
        return "—"
    if n >= 1_000_000_000:
        return f"{n / 1_000_000_000:.1f}B"
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n / 1_000:.1f}K"
    return str(n)


def human_date(yyyymmdd) -> str:
    s = str(yyyymmdd or "")
    if len(s) == 8 and s.isdigit():
        return f"{s[6:8]}.{s[4:6]}.{s[0:4]}"
    return s or "—"


def progress_bar(percent: float, width: int = 12) -> str:
    percent = max(0.0, min(100.0, float(percent)))
    filled = int(round(percent / 100 * width))
    return "█" * filled + "░" * (width - filled)


class LinkCache:
    """
    Простой LRU-кэш: хранит данные о ссылках по короткому токену,
    чтобы вместить идентификатор в callback_data (лимит 64 байта).
    """

    def __init__(self, maxsize: int = 1000):
        self.data: "OrderedDict[str, dict]" = OrderedDict()
        self.maxsize = maxsize

    def put(self, value: dict) -> str:
        token = secrets.token_urlsafe(5)
        self.data[token] = value
        self.data.move_to_end(token)
        if len(self.data) > self.maxsize:
            self.data.popitem(last=False)
        return token

    def get(self, token: str):
        v = self.data.get(token)
        if v is not None:
            self.data.move_to_end(token)
        return v


def build_caption(info: dict, lang: str = "ru") -> str:
    """Подпись-превью под видео с кнопками выбора формата."""
    title = info.get("title") or "—"
    uploader = info.get("uploader") or info.get("channel") or "—"
    duration = human_duration(info.get("duration"))
    views = human_number(info.get("view_count"))
    site = info.get("extractor_key") or info.get("extractor") or "—"
    choose = "👇 Выбери формат для скачивания:" if lang == "ru" else "👇 Choose a format:"
    return (
        f"🎬 <b>{esc(title)}</b>\n"
        f"👤 {esc(uploader)}\n"
        f"⏱ {duration}   👁 {views}   🌐 {esc(site)}\n\n"
        f"{choose}"
    )


def build_info_text(info: dict, lang: str = "ru") -> str:
    """Подробная карточка с информацией о видео."""
    rows = [f"🎬 <b>{esc(info.get('title') or '—')}</b>\n"]
    fields = [
        ("👤 Автор", info.get("uploader") or info.get("channel")),
        ("⏱ Длительность", human_duration(info.get("duration"))),
        ("👁 Просмотры", human_number(info.get("view_count"))),
        ("👍 Лайки", human_number(info.get("like_count"))),
        ("💬 Комментарии", human_number(info.get("comment_count"))),
        ("📅 Дата", human_date(info.get("upload_date"))),
        ("🌐 Источник", info.get("extractor_key")),
        ("🆔 ID", info.get("id")),
    ]
    for label, val in fields:
        if val and val != "—":
            rows.append(f"{label}: <code>{esc(val)}</code>")
    desc = info.get("description")
    if desc:
        d = " ".join(str(desc).split())
        if len(d) > 500:
            d = d[:500] + "…"
        rows.append(f"\n📝 {esc(d)}")
    return "\n".join(rows)
