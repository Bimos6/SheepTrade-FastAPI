from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from app.repositories.user_repo import UserRepository
from app.core.security import get_password_hash, verify_password

class AuthService:
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
    
    async def register(self, username: str, password: str):
        user = await self.repo.get_by_username(username)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким именем уже существует"
            )

        hashed_password = get_password_hash(password)
        new_user = await self.repo.create(username, hashed_password)
        return new_user

    async def  authenticate(self, username: str, password: str):
        user = await self.repo.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user