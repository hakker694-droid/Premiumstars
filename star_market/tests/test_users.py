import pytest
from aiogram.types import User as TgUser

from database.database import Database
from database.repositories import UserRepository


def tg(uid: int, username: str | None = "u") -> TgUser:
    return TgUser(id=uid, is_bot=False, first_name="Test", username=username)


@pytest.fixture
async def db(tmp_path):
    database = Database(f"sqlite+aiosqlite:///{tmp_path}/t.db")
    await database.create_all()
    yield database
    await database.dispose()


async def test_get_or_create_and_refresh(db):
    async with db.session_factory() as s:
        repo = UserRepository(s)
        user, created = await repo.get_or_create(tg(1, "old"))
        assert created and user.referral_code == "ref_1"
        await s.commit()
    async with db.session_factory() as s:
        user, created = await UserRepository(s).get_or_create(tg(1, "new"))
        assert not created and user.username == "new"


async def test_referrer_rules(db):
    async with db.session_factory() as s:
        repo = UserRepository(s)
        a, _ = await repo.get_or_create(tg(1))
        b, _ = await repo.get_or_create(tg(2))
        assert await repo.attach_referrer(a, "ref_1") is False  # self-referral
        assert await repo.attach_referrer(b, "garbage") is False
        assert await repo.attach_referrer(b, "ref_999") is False  # unknown
        assert await repo.attach_referrer(b, "ref_1") is True
        assert b.referred_by_id == a.id
        assert await repo.attach_referrer(b, "ref_2") is False  # only once
