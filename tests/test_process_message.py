from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest

from models import User
from usecase import process_message


@pytest.mark.asyncio
async def test_process_message_new_user():
    test_user_id = 123
    test_username = "test_user"
    test_message = "This is a test message #done"
    test_chat_id = 100

    # Мокаем запрос к базе данных
    with (
        patch("usecase.User.get_or_none") as mock_get,
        patch("usecase.User.create") as mock_create,
    ):

        # Пользователь не найден
        mock_get.return_value = None

        # Создаем нового пользователя
        new_user = MagicMock(spec=User)
        mock_create.return_value = new_user

        # Вызываем тестируемую функцию
        await process_message(test_user_id, test_username, test_message, test_chat_id)

        # Проверяем что был вызван поиск пользователя
        mock_get.assert_called_once()

        # Проверяем что был соз��ан новый пользователь с правильными параметрами
        mock_create.assert_called_once()
        args = mock_create.call_args[1]
        assert args["telegram_id"] == test_user_id
        assert args["username"] == test_username
        assert args["chat_id"] == test_chat_id
        assert isinstance(args["last_report_date_time"], datetime)


@pytest.mark.asyncio
async def test_process_message_existing_user():
    test_user_id = 123
    test_username = "test_user"
    test_message = "This is a test message #done"
    test_chat_id = 100

    # Создаем существующего пользователя
    existing_user = MagicMock(spec=User)
    old_time = datetime.now() - timedelta(hours=1)
    existing_user.last_report_date_time = old_time

    # Мокаем запрос к базе данных
    with patch("usecase.User.get_or_none") as mock_get:
        # Возвращаем существующего пользователя
        mock_get.return_value = existing_user

        # Вызываем тестируемую функцию
        await process_message(test_user_id, test_username, test_message, test_chat_id)

        # Проверяем что был вызван поиск пользователя
        mock_get.assert_called_once()

        # Проверяем что время последнего отчета было обновлено
        assert existing_user.last_report_date_time > old_time

        # Проверяем что изменения были сохранены
        existing_user.save.assert_called_once()
