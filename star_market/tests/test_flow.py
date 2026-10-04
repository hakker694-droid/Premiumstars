"""Offline end-to-end check: feed real updates through the dispatcher with a fake Telegram session."""
import importlib
from datetime import datetime

import pytest
from aiogram import Bot
from aiogram.client.session.base import BaseSession
from aiogram.methods import AnswerCallbackQuery, EditMessageText, SendMessage
from aiogram.types import Chat, Message, Update
from aiogram.types import User as TgUser

import bot as bot_module
from handlers import errors, pending, profile, start, support
from config import Settings
from database.database import Database
from database.repositories import UserRepository


class FakeSession(BaseSession):
    def __init__(self):
        super().__init__()
        self.calls = []

    async def close(self):
        pass

    async def stream_content(self, *a, **kw):  # pragma: no cover
        yield b""

    async def make_request(self, bot, method, timeout=None):
        self.calls.append(method)
        if isinstance(method, (SendMessage, EditMessageText)):
            return Message(message_id=99, date=datetime.now(), chat=Chat(id=5, type="private"), text=getattr(method, "text", ""))
        return True


@pytest.fixture
async def env(tmp_path):
    settings = Settings(bot_token="123456:" + "A" * 35, throttle_interval=0)
    db = Database(f"sqlite+aiosqlite:///{tmp_path}/f.db")
    await db.create_all()
    session = FakeSession()
    bot = Bot(token=settings.bot_token, session=session)
    # aiogram routers can attach to only one Dispatcher; reload for a fresh set per test
    for module in (errors, start, profile, support, pending):
        importlib.reload(module)
    dp = bot_module.build_dispatcher(settings, db)
    yield bot, dp, session, db
    await db.dispose()


def message_update(text, uid=5, uid_update=1):
    return {
        "update_id": uid_update,
        "message": {
            "message_id": 1, "date": 0, "text": text,
            "chat": {"id": uid, "type": "private"},
            "from": {"id": uid, "is_bot": False, "first_name": "Ali", "username": "ali"},
            **({"entities": [{"type": "bot_command", "offset": 0, "length": len(text.split()[0])}]} if text.startswith("/") else {}),
        },
    }


def callback_update(data, uid=5, uid_update=2):
    return {
        "update_id": uid_update,
        "callback_query": {
            "id": "cb1", "chat_instance": "x", "data": data,
            "from": {"id": uid, "is_bot": False, "first_name": "Ali", "username": "ali"},
            "message": {"message_id": 10, "date": 0, "chat": {"id": uid, "type": "private"}, "text": "menu",
                        "from": {"id": 1, "is_bot": True, "first_name": "Bot"}},
        },
    }


async def feed(dp, bot, raw):
    await dp.feed_update(bot, Update.model_validate(raw, context={"bot": bot}))


async def test_start_creates_user_and_shows_menu(env):
    bot, dp, session, db = env
    await feed(dp, bot, message_update("/start"))
    sent = [c for c in session.calls if isinstance(c, SendMessage)]
    assert sent and "STAR MARKET" in sent[0].text
    assert sent[0].reply_markup is not None
    async with db.session_factory() as s:
        assert await UserRepository(s).get_by_tg_id(5) is not None


async def test_referral_start_param(env):
    bot, dp, session, db = env
    await feed(dp, bot, message_update("/start", uid=7, uid_update=1))
    await feed(dp, bot, message_update("/start ref_7", uid=8, uid_update=2))
    async with db.session_factory() as s:
        repo = UserRepository(s)
        invited = await repo.get_by_tg_id(8)
        referrer = await repo.get_by_tg_id(7)
        assert invited.referred_by_id == referrer.id


async def test_profile_and_pending_and_home(env):
    bot, dp, session, db = env
    await feed(dp, bot, message_update("/start"))
    session.calls.clear()
    await feed(dp, bot, callback_update("m:profile"))
    edits = [c for c in session.calls if isinstance(c, EditMessageText)]
    assert edits and "Profilim" in edits[0].text and "0 UZS" in edits[0].text

    session.calls.clear()
    await feed(dp, bot, callback_update("m:stars", uid_update=3))
    edits = [c for c in session.calls if isinstance(c, EditMessageText)]
    assert edits and "ishga tushirilmagan" in edits[0].text

    session.calls.clear()
    await feed(dp, bot, callback_update("m:home", uid_update=4))
    edits = [c for c in session.calls if isinstance(c, EditMessageText)]
    assert edits and "STAR MARKET" in edits[0].text


async def test_blocked_user_is_stopped(env):
    bot, dp, session, db = env
    await feed(dp, bot, message_update("/start"))
    async with db.session_factory() as s:
        u = await UserRepository(s).get_by_tg_id(5)
        u.is_blocked = True
        await s.commit()
    session.calls.clear()
    await feed(dp, bot, message_update("/start", uid_update=9))
    sent = [c for c in session.calls if isinstance(c, SendMessage)]
    assert len(sent) == 1 and "bloklangan" in sent[0].text
