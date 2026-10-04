"""Help / support screen."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from config import Settings
from keyboards.common import MenuCB, with_nav
from utils import texts
from utils.screens import show_screen

router = Router(name="support")


def _help_text(settings: Settings) -> str:
    contact = (
        texts.HELP_CONTACT.format(username=settings.support_username)
        if settings.support_username
        else texts.HELP_NO_CONTACT
    )
    return texts.HELP.format(contact=contact)


@router.callback_query(MenuCB.filter(F.section == "help"))
async def help_screen(call: CallbackQuery, settings: Settings) -> None:
    await show_screen(call, _help_text(settings), with_nav())


@router.message(Command("help"))
async def help_command(message: Message, settings: Settings) -> None:
    await message.answer(_help_text(settings), reply_markup=with_nav())
