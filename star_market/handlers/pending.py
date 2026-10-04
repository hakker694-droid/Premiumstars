"""Honest placeholders for sections that are built in later phases.

Register this router LAST. When a section gets its real handler (Phase 3+),
that router takes priority and the matching entry here is simply never reached.
"""
from __future__ import annotations

from aiogram import F, Router
from aiogram.types import CallbackQuery

from keyboards.common import MenuCB, with_nav
from utils import texts
from utils.screens import show_screen

router = Router(name="pending")


@router.callback_query(MenuCB.filter(F.section.in_(set(texts.PENDING_TITLES))))
async def pending_section(call: CallbackQuery, callback_data: MenuCB) -> None:
    title = texts.PENDING_TITLES[callback_data.section]
    await show_screen(call, texts.PENDING.format(title=title), with_nav())
