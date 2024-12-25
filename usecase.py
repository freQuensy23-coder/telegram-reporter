from datetime import datetime, timedelta

import loguru

from models import User


async def process_message(user_id: int, username: str, message: str, chat_id: int):
    # get user
    user = User.get_or_none(User.telegram_id == user_id, User.chat_id == chat_id)
    if not user:
        user = User.create(
            telegram_id=user_id,
            username=username,
            chat_id=chat_id,
            last_report_date_time=datetime.now(),
        )
    user.last_report_date_time = datetime.now()
    user.save()


async def daily_report() -> dict[int, str]:
    msgs_to_send = {}
    chat_ids: list[int] = User.select(User.chat_id).distinct()
    for chat_id in chat_ids:
        loguru.logger.debug(f"Processing chat {chat_id}")
        users_without_report_yesterday = await get_users_without_report_yesterday(
            chat_id
        )
        if len(users_without_report_yesterday) == 0:
            continue
        msgs_to_send[chat_id] = "Users without report yesterday: "
        for user in users_without_report_yesterday:
            loguru.logger.debug(
                f"User {user.telegram_id} has not sent message yesterday"
            )
            msgs_to_send[chat_id] += f"{user.username} "
    return msgs_to_send


async def get_users_without_report_yesterday(chat_id: int) -> list[User]:
    twenty_four_hours_ago = datetime.now() - timedelta(days=1)
    yesterday = datetime(
        twenty_four_hours_ago.year,
        twenty_four_hours_ago.month,
        twenty_four_hours_ago.day,
    )
    result: list[User] = User.select(User.telegram_id, User.username).where(
        User.chat_id == chat_id,
        User.last_report_date_time.to_timestamp() < yesterday.timestamp(),
    )
    return result
