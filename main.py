"""
Точка входа.
Запуск: python main.py
Перед запуском задай переменную окружения BOT_TOKEN (и при желании ADMIN_IDS).
"""
import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import database as db
import downloader as dl
from config import ADMIN_IDS, BOT_TOKEN
from handlers import get_main_router
from middlewares import RegisterMiddleware, ThrottleMiddleware

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("video-bot")


async def on_startup(bot: Bot):
    await db.init_db()
    logger.info("База данных готова")
    logger.info("ffmpeg доступен: %s", dl.FFMPEG_AVAILABLE)
    if not dl.FFMPEG_AVAILABLE:
        logger.warning(
            "ffmpeg НЕ найден! Будут доступны только готовые потоки video+audio, "
            "а MP3 будет отдаваться в исходном формате аудио. "
            "Поставь ffmpeg (см. Dockerfile) для полного функционала."
        )
    me = await bot.get_me()
    logger.info("Бот @%s запущен", me.username)
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, "✅ Бот запущен и готов к работе.")
        except Exception:
            pass


async def main():
    if not BOT_TOKEN:
        raise SystemExit(
            "❌ Не задан BOT_TOKEN.\n"
            "На bothost.ru добавь переменную окружения BOT_TOKEN в настройках проекта, "
            "либо создай файл .env по образцу .env.example."
        )

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=MemoryStorage())

    # Middlewares (порядок важен: сначала регистрация/бан, потом антифлуд)
    for observer in (dp.message, dp.callback_query):
        observer.middleware(RegisterMiddleware())
        observer.middleware(ThrottleMiddleware())

    dp.include_router(get_main_router())

    await bot.delete_webhook(drop_pending_updates=True)
    await on_startup(bot)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Остановка бота")
