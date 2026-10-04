"""STAR MARKET entry point."""
from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import Settings, get_settings
from database.database import Database
from handlers import errors, pending, profile, start, support
from middlewares.db_session import DbSessionMiddleware
from middlewares.throttling import ThrottlingMiddleware
from middlewares.user_loader import UserMiddleware
from utils.logging_setup import setup_logging

logger = logging.getLogger(__name__)


def build_dispatcher(settings: Settings, db: Database) -> Dispatcher:
    dp = Dispatcher(storage=MemoryStorage(), settings=settings)

    throttling = ThrottlingMiddleware(settings.throttle_interval)
    db_session = DbSessionMiddleware(db.session_factory)
    user_loader = UserMiddleware()
    for observer in (dp.message, dp.callback_query):
        # Order matters: throttle -> DB session -> user loader
        observer.outer_middleware(throttling)
        observer.outer_middleware(db_session)
        observer.outer_middleware(user_loader)

    dp.include_router(errors.router)
    dp.include_router(start.router)
    # Phase 3+: stars, premium, orders, payments, referrals routers go here
    dp.include_router(profile.router)
    dp.include_router(support.router)
    dp.include_router(pending.router)  # keep last
    return dp


async def main() -> None:
    settings = get_settings()
    setup_logging(settings.log_level, settings.log_dir)

    db = Database(settings.database_url)
    if settings.auto_create_tables:
        await db.create_all()

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = build_dispatcher(settings, db)

    try:
        me = await bot.get_me()
    except TelegramUnauthorizedError:
        logger.critical("BOT_TOKEN is invalid or revoked. Check your .env file.")
        await bot.session.close()
        await db.dispose()
        return

    await bot.set_my_commands(
        [BotCommand(command="start", description="Bosh sahifa"), BotCommand(command="help", description="Yordam")]
    )
    logger.info("STAR MARKET started as @%s", me.username)

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()
        await db.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("STAR MARKET stopped")
