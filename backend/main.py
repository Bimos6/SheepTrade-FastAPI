from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from sqlalchemy import text
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.core.limiter import limiter
from app.db.session import engine
from app.db.redis import redis_client
from app.api.v1.router import api_router
import app.models

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Подключение к базе данных...")
    async with engine.begin() as conn:
        await conn.execute(text("SELECT 1"))
    await redis_client.ping()
    print("Успешно подключено к Postgres и Redis!")
    yield
    await engine.dispose()  
    await redis_client.close()
    print("Соединения закрыты.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# 1. Сначала TrustedHost
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"]
)

# 2. Потом CORS (должен быть внешним слоем)
ALLOWED_ORIGINS = [
    "http://localhost:5500",
    "http://127.0.0.1:5500",  # <-- ДОБАВЛЕНО (именно этот порт у вас сейчас)
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",  # <-- ДОБАВЛЕНО
    # "https://sheeptrade.com" # Раскомментируйте в проде
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "project": settings.PROJECT_NAME
    }