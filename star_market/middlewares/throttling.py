"""Simple per-user rate limiting."""
from __future__ import annotations

import time
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, TelegramObject

from utils import texts


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, interval: float = 0.6) -> None:
        self.interval = interval
        self._last: dict[int, float] = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        user = getattr(event, "from_user", None)
        if user is None:
            return await handler(event, data)

        now = time.monotonic()
        if now - self._last.get(user.id, 0.0) < self.interval:
            if isinstance(event, CallbackQuery):
                await event.answer(texts.THROTTLED)
            return None
        self._last[user.id] = now

        if len(self._last) > 10_000:  # keep memory bounded
            cutoff = now - 60
            self._last = {uid: ts for uid, ts in self._last.items() if ts > cutoff}
        return await handler(event, data)
