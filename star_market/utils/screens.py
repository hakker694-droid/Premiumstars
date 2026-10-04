"""Screen helper: edit the existing message when possible instead of sending new ones."""
from __future__ import annotations

from aiogram.exceptions import TelegramBadRequest
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message


async def show_screen(
    event: Message | CallbackQuery,
    text: str,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    if isinstance(event, Message):
        await event.answer(text, reply_markup=reply_markup)
        return

    message = event.message
    if isinstance(message, Message):
        try:
            await message.edit_text(text, reply_markup=reply_markup)
        except TelegramBadRequest as exc:
            if "message is not modified" not in str(exc).lower():
                # e.g. the original message has no text (photo) -> send a new one
                await message.answer(text, reply_markup=reply_markup)
    else:
        await event.bot.send_message(event.from_user.id, text, reply_markup=reply_markup)
    await event.answer()
