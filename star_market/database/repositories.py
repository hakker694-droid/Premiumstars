"""Data-access layer. Handlers never write SQL directly."""
from __future__ import annotations

from datetime import datetime, timezone

from aiogram.types import User as TgUser
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User


class UserRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_tg_id(self, tg_id: int) -> User | None:
        result = await self.session.execute(select(User).where(User.tg_id == tg_id))
        return result.scalar_one_or_none()

    async def get_by_referral_code(self, code: str) -> User | None:
        result = await self.session.execute(select(User).where(User.referral_code == code))
        return result.scalar_one_or_none()

    async def get_or_create(self, tg_user: TgUser) -> tuple[User, bool]:
        """Return (user, created). Keeps username/full name fresh."""
        now = datetime.now(timezone.utc)
        user = await self.get_by_tg_id(tg_user.id)
        if user is not None:
            user.username = tg_user.username
            user.full_name = tg_user.full_name
            user.last_seen_at = now
            return user, False

        user = User(
            tg_id=tg_user.id,
            username=tg_user.username,
            full_name=tg_user.full_name,
            referral_code=f"ref_{tg_user.id}",
            last_seen_at=now,
        )
        self.session.add(user)
        try:
            await self.session.flush()
        except IntegrityError:
            # Two first updates raced; the other one won.
            await self.session.rollback()
            existing = await self.get_by_tg_id(tg_user.id)
            if existing is None:
                raise
            return existing, False
        return user, True

    async def attach_referrer(self, user: User, code: str) -> bool:
        """Link a NEW user to a referrer. No self-referral, only once."""
        if user.referred_by_id is not None or not code.startswith("ref_"):
            return False
        referrer = await self.get_by_referral_code(code)
        if referrer is None or referrer.id == user.id:
            return False
        user.referred_by_id = referrer.id
        await self.session.flush()
        return True
