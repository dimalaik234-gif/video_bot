"""
Локализация. Поддержаны русский и английский.
Использование: t("ключ", lang, name="...", ...)
"""

TEXTS = {
    "ru": {
        "start": (
            "👋 <b>Привет, {name}!</b>\n\n"
            "Я скачиваю видео и аудио по ссылке с <b>YouTube, TikTok, "
            "Instagram, VK, X (Twitter), Reddit, Pinterest, SoundCloud</b> "
            "и ещё 1000+ сайтов.\n\n"
            "📥 <b>Просто пришли ссылку</b> — и выбери формат.\n\n"
            "Команды:\n"
            "/help — помощь\n"
            "/settings — настройки\n"
            "/stats — твоя статистика\n"
            "/history — история загрузок\n"
            "/lang — язык"
        ),
        "help": (
            "ℹ️ <b>Как пользоваться</b>\n\n"
            "1. Скопируй ссылку на видео.\n"
            "2. Пришли её мне сообщением.\n"
            "3. Выбери качество или «🎵 MP3».\n"
            "4. Получи файл.\n\n"
            "<b>Что я умею:</b>\n"
            "• 📹 Видео до 4K\n"
            "• 🎵 Аудио (MP3)\n"
            "• 🖼 Обложку видео\n"
            "• 📝 Субтитры\n"
            "• 📋 Плейлисты (до 10 видео)\n"
            "• ℹ️ Подробную информацию\n\n"
            "⚠️ Telegram ограничивает размер файла <b>50 МБ</b>. "
            "Если видео больше — выбери качество ниже или «🎵 MP3»."
        ),
        "send_link": "📎 Пришли мне ссылку на видео, и я скачаю его.",
        "getting_info": "🔍 Получаю информацию о видео…",
        "err_info": "❌ Не удалось получить данные. Проверь ссылку или попробуй другую.",
        "err_download": "❌ Не получилось скачать. Возможно, видео приватное, удалено или требует входа.",
        "err_upload": "❌ Не удалось отправить файл.",
        "too_large": (
            "📦 Файл получился <b>{size}</b>, а Telegram разрешает до <b>{limit}</b>.\n"
            "Выбери качество пониже или «🎵 MP3»."
        ),
        "downloading": "⬇️ Начинаю загрузку…",
        "downloading_p": "⬇️ Загрузка\n<code>{bar}</code> {p}%\n🚀 {speed}   ⏳ {eta}",
        "converting": "⚙️ Обрабатываю файл…",
        "uploading": "📤 Отправляю файл…",
        "settings": (
            "⚙️ <b>Настройки</b>\n\n"
            "🌐 Язык: <b>{lang}</b>\n"
            "🎚 Качество по умолчанию: <b>{quality}</b>\n"
            "🎞 Формат по умолчанию: <b>{fmt}</b>"
        ),
        "choose_lang": "🌐 Выбери язык / Choose language:",
        "choose_quality": "🎚 Качество по умолчанию:",
        "choose_fmt": "🎞 Формат по умолчанию:",
        "lang_saved": "✅ Язык сохранён.",
        "quality_saved": "✅ Качество по умолчанию сохранено.",
        "fmt_saved": "✅ Формат по умолчанию сохранён.",
        "my_stats": (
            "📊 <b>Твоя статистика</b>\n\n"
            "📥 Скачано файлов: <b>{count}</b>\n"
            "📅 С нами с: <b>{joined}</b>"
        ),
        "history_empty": "📭 История пуста. Пришли ссылку, чтобы начать.",
        "history_title": "🕓 <b>Последние загрузки:</b>",
        "playlist_found": "📋 <b>Плейлист:</b> {title}\nВидео внутри: <b>{n}</b>\n\nСкачать?",
        "pl_start": "📋 Качаю плейлист: 0/{n}…",
        "pl_progress": "📋 Качаю плейлист: {i}/{n}…",
        "pl_done": "✅ Готово! Отправлено {ok} из {n}.",
        "session_expired": "⌛ Сессия истекла. Пришли ссылку заново.",
        "sub_need": "🔒 Чтобы пользоваться ботом, подпишись на канал, затем нажми «Проверить».",
        "sub_ok": "✅ Подписка подтверждена! Можешь присылать ссылки.",
        "sub_recheck": "❌ Ты ещё не подписан(а). Подпишись и попробуй снова.",
        "getting_subs": "📝 Ищу субтитры…",
        "no_subs": "😕 Субтитры для этого видео не найдены.",
        "no_thumb": "😕 Обложка недоступна.",
        "banned": "🚫 Доступ к боту ограничен.",
        # кнопки
        "btn_lang": "🌐 Язык",
        "btn_quality": "🎚 Качество",
        "btn_fmt": "🎞 Формат",
        "btn_back": "⬅️ Назад",
        "btn_join": "📢 Подписаться",
        "btn_check": "✅ Проверить",
        "btn_dl_all": "⬇️ Скачать всё (до {n})",
    },
    "en": {
        "start": (
            "👋 <b>Hi, {name}!</b>\n\n"
            "I download video and audio by link from <b>YouTube, TikTok, "
            "Instagram, VK, X (Twitter), Reddit, Pinterest, SoundCloud</b> "
            "and 1000+ more sites.\n\n"
            "📥 <b>Just send me a link</b> and choose a format.\n\n"
            "Commands:\n"
            "/help — help\n"
            "/settings — settings\n"
            "/stats — your stats\n"
            "/history — download history\n"
            "/lang — language"
        ),
        "help": (
            "ℹ️ <b>How to use</b>\n\n"
            "1. Copy a video link.\n"
            "2. Send it to me.\n"
            "3. Pick a quality or “🎵 MP3”.\n"
            "4. Get the file.\n\n"
            "<b>Features:</b>\n"
            "• 📹 Video up to 4K\n"
            "• 🎵 Audio (MP3)\n"
            "• 🖼 Thumbnail\n"
            "• 📝 Subtitles\n"
            "• 📋 Playlists (up to 10)\n"
            "• ℹ️ Detailed info\n\n"
            "⚠️ Telegram limits files to <b>50 MB</b>. "
            "If the video is bigger — pick a lower quality or “🎵 MP3”."
        ),
        "send_link": "📎 Send me a video link and I'll download it.",
        "getting_info": "🔍 Fetching video info…",
        "err_info": "❌ Couldn't fetch info. Check the link or try another.",
        "err_download": "❌ Download failed. The video may be private, removed or login-gated.",
        "err_upload": "❌ Failed to send the file.",
        "too_large": (
            "📦 The file is <b>{size}</b>, but Telegram allows up to <b>{limit}</b>.\n"
            "Pick a lower quality or “🎵 MP3”."
        ),
        "downloading": "⬇️ Starting download…",
        "downloading_p": "⬇️ Downloading\n<code>{bar}</code> {p}%\n🚀 {speed}   ⏳ {eta}",
        "converting": "⚙️ Processing the file…",
        "uploading": "📤 Uploading the file…",
        "settings": (
            "⚙️ <b>Settings</b>\n\n"
            "🌐 Language: <b>{lang}</b>\n"
            "🎚 Default quality: <b>{quality}</b>\n"
            "🎞 Default format: <b>{fmt}</b>"
        ),
        "choose_lang": "🌐 Choose language / Выбери язык:",
        "choose_quality": "🎚 Default quality:",
        "choose_fmt": "🎞 Default format:",
        "lang_saved": "✅ Language saved.",
        "quality_saved": "✅ Default quality saved.",
        "fmt_saved": "✅ Default format saved.",
        "my_stats": (
            "📊 <b>Your stats</b>\n\n"
            "📥 Files downloaded: <b>{count}</b>\n"
            "📅 With us since: <b>{joined}</b>"
        ),
        "history_empty": "📭 History is empty. Send a link to start.",
        "history_title": "🕓 <b>Recent downloads:</b>",
        "playlist_found": "📋 <b>Playlist:</b> {title}\nVideos inside: <b>{n}</b>\n\nDownload?",
        "pl_start": "📋 Downloading playlist: 0/{n}…",
        "pl_progress": "📋 Downloading playlist: {i}/{n}…",
        "pl_done": "✅ Done! Sent {ok} of {n}.",
        "session_expired": "⌛ Session expired. Please send the link again.",
        "sub_need": "🔒 To use the bot, subscribe to the channel, then tap “Check”.",
        "sub_ok": "✅ Subscription confirmed! Send your links.",
        "sub_recheck": "❌ You're not subscribed yet. Subscribe and try again.",
        "getting_subs": "📝 Looking for subtitles…",
        "no_subs": "😕 No subtitles found for this video.",
        "no_thumb": "😕 Thumbnail unavailable.",
        "banned": "🚫 Access to the bot is restricted.",
        "btn_lang": "🌐 Language",
        "btn_quality": "🎚 Quality",
        "btn_fmt": "🎞 Format",
        "btn_back": "⬅️ Back",
        "btn_join": "📢 Subscribe",
        "btn_check": "✅ Check",
        "btn_dl_all": "⬇️ Download all (up to {n})",
    },
}


def t(key: str, lang: str = "ru", **kwargs) -> str:
    d = TEXTS.get(lang) or TEXTS["ru"]
    s = d.get(key) or TEXTS["ru"].get(key) or key
    try:
        return s.format(**kwargs)
    except Exception:
        return s
