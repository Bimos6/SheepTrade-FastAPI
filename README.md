# 🐑 SheepTrade

Игровая платформа для коллекционирования и торговли овцами. Пользователи делают ставки, выбивают овец разной редкости, хранят их в Амбаре и продают по динамической рыночной цене.

---

## 🛠 Стек технологий
```
Backend:
- Python 3.12
- FastAPI (асинхронный веб-фреймворк)
- PostgreSQL 16 (основная БД)
- Redis 7 (кэш, rate limiting, WebSocket Pub/Sub)
- SQLAlchemy 2.0 (async ORM)
- Alembic (миграции)
- Gunicorn + Uvicorn (WSGI/ASGI сервер)
- JWT + Argon2 (аутентификация)
- SlowAPI (rate limiting)

Frontend:
- React 18 (через CDN, SPA в одном файле)
- Tailwind CSS (стилизация)
- Axios (HTTP-клиент)
- WebSocket (real-time лента ставок)

Инфраструктура:
- Docker
- Docker Compose
```
---

## 📋 Требования

- Docker и Docker Compose
- Python 3.12+ (только если хотите запустить бэкенд без Docker)
- Современный браузер (Chrome, Firefox, Edge)

---

## 🚀 Быстрый запуск

### 1. Клонирование репозитория
```bash
git clone https://github.com/YOUR_USERNAME/sheeptrade.git
cd sheeptrade
```
### 2. Запуск бэкенда (Docker)
```bash
cd backend
```
# Создаём .env из шаблона
```bash
cp .env.example .env
```
# Собираем и запускаем контейнеры (PostgreSQL, Redis, API)
```bash
docker compose up --build -d
```
# Применяем миграции БД
```bash
docker compose exec api alembic upgrade head
```
# Заполняем справочник овец (10 видов)
```bash
docker compose exec api python -m app.db.seed
```

После запуска API доступен по адресу:
```
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Health check: http://127.0.0.1:8000/health
```
### 3. Запуск фронтенда
Фронтенд представляет собой SPA на React (через CDN), не требует сборки.
```bash
cd ../frontend
python3 -m http.server 5500
```
Откройте в браузере: http://127.0.0.1:5500

> ⚠️ Если используете VS Code, можно открыть frontend/index.html через расширение Live Server — порт будет 5500.

---

## 📁 Структура проекта

<pre>
sheeptrade/
│
├── backend/                  # Серверная часть (Python / FastAPI)
│   ├── app/                  # Исходный код приложения
│   │   ├── api/              # Эндпоинты (маршруты HTTP и WebSocket)
│   │   ├── core/             # Конфигурация, безопасность (JWT), лимиты, WS-менеджер
│   │   ├── db/               # Подключение к БД, миграции, скрипт заполнения (seed)
│   │   ├── models/           # SQLAlchemy модели таблиц (User, Sheep, Inventory, Bet)
│   │   ├── repositories/     # Слой работы с базой данных (CRUD-запросы)
│   │   ├── schemas/          # Pydantic-схемы (валидация входящих/исходящих данных)
│   │   └── services/         # Бизнес-логика (математика ставок, авторизация)
│   ├── alembic/              # Файлы миграций базы данных
│   ├── Dockerfile            # Инструкция для сборки контейнера API
│   └── docker-compose.yml    # Оркестрация (API + PostgreSQL + Redis)
│
└── frontend/                 # Клиентская часть (React)
    ├── img/                  # Графика (фон фермы, спрайты овец)
    └── index.html            # Основной файл SPA (React + Tailwind + Axios)
</pre>

---

## 🔌 API Эндпоинты
```
### Аутентификация
- POST /api/v1/auth/register — Регистрация (JSON: {username, password})
- POST /api/v1/auth/login — Логин (Form Data: username, password) -> JWT
- GET /api/v1/auth/me — Профиль текущего пользователя (требует JWT)
```
### Игра
```
- POST /api/v1/game/bet — Сделать ставку (JSON: {amount}) -> выпавшая овца
- POST /api/v1/game/sell/{inventory_id} — Продать овцу из амбара
- GET /api/v1/game/inventory — Список овец в амбаре
- GET /api/v1/game/sheep-types — Справочник всех видов овец
- GET /api/v1/game/history — Последние 15 ставок
```

### WebSocket
- ws://127.0.0.1:8000/api/v1/ws — Real-time лента ставок (Redis Pub/Sub)

---

## 🎮 Особенности реализации

### Математика ставок
- Базовая логика: у каждой овцы есть base_chance в БД (админ может менять).
- Буст от ставки: коэффициент усиления (BOOST_SCALES) хранится в app/core/game_config.py — не в БД. Чем выше ставка, тем больше шанс на редкую овцу.
- Нормализация: сумма шансов всегда = 100%, редкие овцы забирают шансы у обычных.

### Безопасность
- JWT (Bearer token) + Argon2 хеширование паролей.
- Rate Limiting: 5 ставок в минуту на IP (SlowAPI + Redis).
- Транзакции: все операции с балансом и инвентарём — в ACID-транзакциях с блокировкой строки (SELECT ... FOR UPDATE).
- TrustedHostMiddleware + строгий CORS.

### WebSocket и Redis Pub/Sub
Приложение запускается в 4 Gunicorn-воркерах. Чтобы события от одного воркера доходили до клиентов другого, используется Redis Pub/Sub канал sheeptrade_ws. Каждый воркер подписан на канал и пересылает сообщения своим WebSocket-клиентам.

### Фронтенд
- Анимация овец: requestAnimationFrame + CSS-спрайты (скоро: спрайт-листы из Pixellab).
- Real-time лента: WebSocket с автоматическим реконнектом.
- Красивый UI: Glassmorphism, неоновые свечения по редкости, плавные анимации.


---
