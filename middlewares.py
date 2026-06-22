"""
Middlewares:
  RegisterMiddleware — регистрирует пользователя в БД и блокирует забаненных.
  ThrottleMiddleware — антифлуд (минимальная пауза между действиями).
"""
import time

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message

import database as db
from config import THROTTLE_RATE
from locales import t


class RegisterMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if user and not user.is_bot:
            await db.add_user(user.id, user.username or "", user.first_name or "")
            if await db.is_banned(user.id):
                lang = "ru"
                try:
                    u = await db.get_user(user.id)
                    lang = (u or {}).get("language", "ru")
                except Exception:
                    pass
                if isinstance(event, Message):
                    await event.answer(t("banned", lang))
                elif isinstance(event, CallbackQuery):
                    await event.answer(t("banned", lang), show_alert=True)
                return  # прерываем обработку
        return await handler(event, data)


class ThrottleMiddleware(BaseMiddleware):
    def __init__(self, rate: float = THROTTLE_RATE):
        self.rate = rate
        self._last = {}

    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        if user:
            now = time.monotonic()
            prev = self._last.get(user.id, 0.0)
            if now - prev < self.rate:
                if isinstance(event, CallbackQuery):
                    await event.answer("⏳ Помедленнее…")
                return  # глушим слишком частые запросы
            self._last[user.id] = now
        return await handler(event, data)
