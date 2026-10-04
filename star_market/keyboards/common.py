"""Shared keyboards and navigation."""
from __future__ import annotations

from aiogram.filters.callback_data import CallbackData
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from utils import texts


class MenuCB(CallbackData, prefix="m"):
    """section: home | cancel | stars | premium | orders | referral | profile | help"""

    section: str


def nav_row(
    *, back_to: str | None = None, home: bool = True, cancel: bool = False
) -> list[InlineKeyboardButton]:
    row: list[InlineKeyboardButton] = []
    if back_to:
        row.append(InlineKeyboardButton(text=texts.BTN_BACK, callback_data=MenuCB(section=back_to).pack()))
    if home:
        row.append(InlineKeyboardButton(text=texts.BTN_HOME, callback_data=MenuCB(section="home").pack()))
    if cancel:
        row.append(InlineKeyboardButton(text=texts.BTN_CANCEL, callback_data=MenuCB(section="cancel").pack()))
    return row


def with_nav(
    rows: list[list[InlineKeyboardButton]] | None = None,
    *,
    back_to: str | None = None,
    home: bool = True,
    cancel: bool = False,
) -> InlineKeyboardMarkup:
    keyboard = list(rows or [])
    nav = nav_row(back_to=back_to, home=home, cancel=cancel)
    if nav:
        keyboard.append(nav)
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def _btn(text: str, section: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=MenuCB(section=section).pack())


def main_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [_btn(texts.BTN_STARS, "stars"), _btn(texts.BTN_PREMIUM, "premium")],
            [_btn(texts.BTN_ORDERS, "orders")],
            [_btn(texts.BTN_REFERRAL, "referral"), _btn(texts.BTN_PROFILE, "profile")],
            [_btn(texts.BTN_HELP, "help")],
        ]
    )
