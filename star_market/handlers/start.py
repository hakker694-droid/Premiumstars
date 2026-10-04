"""/start, main menu and Home/Cancel navigation."""
from __future__ import annotations

from aiogram import F, Router
from aiogram.filters import Command, CommandObject, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from database.repositories import UserRepository
from keyboards.common import MenuCB, main_menu_kb
from utils import texts
from utils.screens import show_screen

router = Router(name="start")


@router.message(CommandStart())
async def cmd_start(
    message: Message,
    command: CommandObject,
    state: FSMContext,
    session: AsyncSession,
    db_user: User,
    is_new_user: bool,
) -> None:
    await state.clear()
    if is_new_user and command.args:
        await UserRepository(session).attach_referrer(db_user, command.args)
    await message.answer(texts.WELCOME, reply_markup=main_menu_kb())


@router.message(Command("menu", "cancel"))
async def cmd_menu(message: Message, state: FSMContext) -> None:
    await state.clear()
    await message.answer(texts.WELCOME, reply_markup=main_menu_kb())


@router.callback_query(MenuCB.filter(F.section.in_({"home", "cancel"})))
async def go_home(call: CallbackQuery, state: FSMContext) -> None:
    await state.clear()
    await show_screen(call, texts.WELCOME, main_menu_kb())
