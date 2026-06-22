"""
Конфигурация бота.
Все секреты берутся из переменных окружения (так безопаснее и удобнее для
bothost.ru — там переменные задаются в панели проекта).
Локально можно создать файл .env (см. .env.example).
"""
import os
from pathlib import Path

# Пытаемся подгрузить .env, если установлен python-dotenv (необязательно)
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# ─── Основное ────────────────────────────────────────────────────────────────
# Токен бота от @BotFather. На bothost.ru задаётся в переменных окружения.
BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()

# ID администраторов через запятую. Пример: ADMIN_IDS=12345678,87654321
ADMIN_IDS = [
    int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x.strip().lstrip("-").isdigit()
]

# Обязательная подписка на канал перед скачиванием (необязательно).
# Пусто = выключено. Пример: REQUIRED_CHANNEL=@my_channel
# Бот должен быть админом этого канала, чтобы проверять подписку.
REQUIRED_CHANNEL = os.getenv("REQUIRED_CHANNEL", "").strip()

# ─── Пути и лимиты ───────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DOWNLOAD_DIR = BASE_DIR / "downloads"
DATABASE_PATH = str(BASE_DIR / "bot.db")

# Лимит Telegram Bot API на отправку файла — 50 МБ.
# Если поднимешь локальный Telegram Bot API сервер, можно увеличить до 2 ГБ.
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", str(50 * 1024 * 1024)))

# Антифлуд: минимальная пауза между действиями одного пользователя (сек.)
THROTTLE_RATE = float(os.getenv("THROTTLE_RATE", "1.5"))

# Максимум видео из плейлиста за раз (бережём ресурсы хостинга)
PLAYLIST_LIMIT = int(os.getenv("PLAYLIST_LIMIT", "10"))

# Папку загрузок создаём заранее
DOWNLOAD_DIR.mkdir(exist_ok=True)
