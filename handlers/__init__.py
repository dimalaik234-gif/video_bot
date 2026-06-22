"""Сборка роутеров. Админский роутер идёт первым — у него приоритет
для FSM-состояний (например, режим рассылки)."""
from aiogram import Router

from . import admin, user


def get_main_router() -> Router:
    root = Router()
    root.include_router(admin.router)
    root.include_router(user.router)
    return root
