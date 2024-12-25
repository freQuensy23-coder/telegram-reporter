import asyncio
from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from loguru import logger

import usecase
from main import bot


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


def setup_scheduler():
    """Setup scheduler with daily report job"""
    scheduler = AsyncIOScheduler()

    # Schedule job to run at 11:59 every day
    trigger = CronTrigger(hour=11, minute=59)
    scheduler.add_job(
        send_daily_reports,
        trigger=trigger,
        name="daily_report",
        misfire_grace_time=60,  # Allow job to be late by up to 60 seconds
        coalesce=True,  # Only run once if multiple executions are due
    )

    return scheduler
