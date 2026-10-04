"""Profile screen."""
from __future__ import annotations

from html import escape

from aiogram import F, Router
from aiogram.types import CallbackQuery

from database.models import User
from keyboards.common import MenuCB, with_nav
from utils import texts
from utils.formatting import fmt_dt, fmt_uzs
from utils.screens import show_screen

router = Router(name="profile")


@router.callback_query(MenuCB.filter(F.section == "profile"))
async def show_profile(call: CallbackQuery, db_user: User) -> None:
    text = texts.PROFILE.format(
        tg_id=db_user.tg_id,
        name=escape(db_user.full_name or "—"),
        username=f"@{escape(db_user.username)}" if db_user.username else "—",
        joined=fmt_dt(db_user.created_at),
        bonus=fmt_uzs(db_user.bonus_balance_uzs),
    )
    await show_screen(call, text, with_nav())
