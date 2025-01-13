import asyncio
import os

import aiogram
import loguru
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from loguru import logger

from reporter.models import User, db, create_tables
from reporter import usecase
from datetime import datetime, timedelta

async def send_daily_reports():
    """Send daily reports to all chats"""
    try:
        messages = await usecase.daily_report()
        for chat_id, message in messages.items():
            try:
                await bot.send_message(chat_id=chat_id, text=message)
                logger.info(f"Daily report sent to chat {chat_id}")
            except Exception as e:
                logger.error(f"Failed to send message to chat {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Error in send_daily_reports: {e}")


async def schedule_daily_report():
    last_report_date_time = datetime.fromtimestamp(1)
    while True:
        if last_report_date_time < datetime.now() - timedelta(days=1):
            await send_daily_reports()
            last_report_date_time = datetime.now()
        await asyncio.sleep(60)
    


dp = Dispatcher()
bot = Bot(token=str(os.getenv("TELEGRAM_BOT_TOKEN")))


@dp.message(F.text.len() > 32 and F.text.contains("#done"))
async def process_message(message: Message):
    if message.from_user:
        loguru.logger.info(
            f"Message received: {message.text} from {message.from_user.username}"
        )
        await usecase.process_message(
            user_id=message.from_user.id,
            username=message.from_user.username or "",
            message=message.text or "",
            chat_id=message.chat.id,
        )


async def main():
    loguru.logger.info("Creating tables")
    create_tables()
    loguru.logger.info("Scheduling daily report")
    asyncio.create_task(schedule_daily_report())
    loguru.logger.info("Starting polling")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main()) 