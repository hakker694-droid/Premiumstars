"""Global error handler: log, apologise to the user, alert admins (rate limited)."""
from __future__ import annotations

import logging
import time

from aiogram import Bot, Router
from aiogram.types import ErrorEvent

from config import Settings
from utils import texts

logger = logging.getLogger(__name__)
router = Router(name="errors")

_last_admin_alert = 0.0


@router.errors()
async def on_error(event: ErrorEvent, bot: Bot, settings: Settings) -> bool:
    global _last_admin_alert
    logger.error("Unhandled error while processing update", exc_info=event.exception)

    update = event.update
    try:
        if update.callback_query:
            await update.callback_query.answer(texts.ERROR, show_alert=True)
        elif update.message:
            await update.message.answer(texts.ERROR)
    except Exception:  # noqa: BLE001
        logger.debug("Could not notify user about the error", exc_info=True)

    now = time.monotonic()
    if now - _last_admin_alert > 60:
        _last_admin_alert = now
        for admin_id in settings.admin_id_list:
            try:
                await bot.send_message(
                    admin_id, f"⚠️ Bot xatoligi: {type(event.exception).__name__}. Batafsil: logs/bot.log"
                )
            except Exception:  # noqa: BLE001
                pass
    return True
