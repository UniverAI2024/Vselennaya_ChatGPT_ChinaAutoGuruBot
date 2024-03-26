import asyncio
import logging
from datetime import datetime, timezone, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from core.utils import close_run_dialog
from dbase.dbworker import create_db, add_columns_if_not_exist
from handlers import admin_handler, user_handler
from create_bot import dp, bot

timezone_offset = 3.0  # Pacific Standard Time (UTC+03:00)
tzinfo = timezone(timedelta(hours=timezone_offset))

logger = logging.getLogger(__name__)

# Настройка логирования в stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    filename="bot_log.log",
    filemode='a',
)


async def on_startup(_):
    logger.info('Бот вышел в онлайн')


# Запуск бота
async def main():
    logger.info("Starting bot")

    dp.include_router(admin_handler.router)
    dp.include_router(user_handler.router)
    # Запускаем бота и пропускаем все накопленные входящие
    # Да, этот метод можно вызвать даже если у вас поллинг
    await bot.delete_webhook(drop_pending_updates=True)
    scheduler = AsyncIOScheduler(time_zone="Europe/Moscow")
    scheduler.add_job(close_run_dialog, trigger='interval', minutes=60, start_date=datetime.now(tzinfo))
    # scheduler.add_job(schedule_update_day_total_token, trigger='cron', hour=0, minute=0, start_date=datetime.now(tzinfo))
    scheduler.start()
    await dp.start_polling(bot, on_startup=on_startup)


if __name__ == "__main__":
    create_db()
    add_columns_if_not_exist()
    asyncio.run(main())
