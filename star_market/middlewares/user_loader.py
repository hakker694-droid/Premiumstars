"""Load/create the DB user, block banned users, inject `db_user` and `is_new_user`."""
from __future__ import annotations

from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from database.repositories import UserRepository
from utils import texts


class UserMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        tg_user = getattr(event, "from_user", None)
        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        user, is_new = await UserRepository(data["session"]).get_or_create(tg_user)
        if user.is_blocked:
            if isinstance(event, CallbackQuery):
                await event.answer(texts.BLOCKED, show_alert=True)
            elif isinstance(event, Message):
                await event.answer(texts.BLOCKED)
            return None

        data["db_user"] = user
        data["is_new_user"] = is_new
        return await handler(event, data)
