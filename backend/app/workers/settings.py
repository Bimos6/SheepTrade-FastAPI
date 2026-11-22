from arq.connections import RedisSettings
from app.core.config import settings
from app.workers.tasks import update_market_price

class WorkerSettings:
    functions = [update_market_price]
    redis_settings = RedisSettings.from_dsn(settings.redis_url)

    # Запускать задачу каждую минуту (60 секунд)
    cron_jobs = [
        # Вызов функции update_market_prices каждую минуту
        # В ARQ синтаксис cron: (функция, минута, час, день, месяц, день_недели)
    ]
    
    # Простой запуск при старте и потом по интервалу
    # (Для cron-задач в ARQ используется немного другой синтаксис, 
    # но для теста мы можем просто запускать задачу вручную или по таймеру)