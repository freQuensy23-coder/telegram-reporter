from usecase import daily_report, get_users_without_report_yesterday
import asyncio
import pytest
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

from models import User


@pytest.mark.asyncio
async def test_get_users_without_report_yesterday():
    # Подготовка тестовых данных
    yesterday = datetime.now() - timedelta(days=1)
    today = datetime.now()

    # Создаем тестовых пользователей
    user1 = MagicMock(spec=User)
    user1.telegram_id = 123
    user1.username = "user1"
    user1.last_report_date_time = yesterday

    user2 = MagicMock(spec=User)
    user2.telegram_id = 456
    user2.username = "user2"
    user2.last_report_date_time = today

    user3 = MagicMock(spec=User)
    user3.telegram_id = 789
    user3.username = "user3"
    user3.last_report_date_time = yesterday - timedelta(days=1)

    test_chat_id = 100

    # Мокаем запрос к базе данных
    with patch("usecase.User.select") as mock_select:
        # Настраиваем мок для возврата пользователей без отчета вчера
        mock_select.return_value.where.return_value = [user3]

        # Вызываем тестируемую функцию
        users = await get_users_without_report_yesterday(test_chat_id)

        # Проверяем результаты
        assert len(users) == 1
        assert users[0].telegram_id == 789
        assert users[0].username == "user3"

        # Проверяем, что select был вызван с правильными параметрами
        mock_select.assert_called_once_with(User.telegram_id, User.username)
        mock_select.return_value.where.assert_called_once()


@pytest.mark.asyncio
async def test_daily_report():
    # Подготовка тестовых данных
    test_chat_ids = [100, 200]

    # Создаем тестовых пользователей для первого чата
    user1 = MagicMock(spec=User)
    user1.telegram_id = 123
    user1.username = "user1"

    user2 = MagicMock(spec=User)
    user2.telegram_id = 456
    user2.username = "user2"

    # Создаем тестового пользователя для второго чата
    user3 = MagicMock(spec=User)
    user3.telegram_id = 789
    user3.username = "user3"

    # Мокаем запросы к базе данных
    with (
        patch("usecase.User.select") as mock_select,
        patch("usecase.get_users_without_report_yesterday") as mock_get_users,
    ):

        # Настраиваем мок для возврата списка чатов
        mock_select.return_value.distinct.return_value = test_chat_ids

        # Настраиваем мок для возврата пользователей без отчетов
        async def mock_get_users_side_effect(chat_id):
            if chat_id == 100:
                return [user1, user2]
            elif chat_id == 200:
                return [user3]
            return []

        mock_get_users.side_effect = mock_get_users_side_effect

        # Вызываем тестируемую функцию
        result = await daily_report()

        # Проверяем результаты
        assert len(result) == 2
        assert result[100] == "Users without report yesterday: user1 user2 "
        assert result[200] == "Users without report yesterday: user3 "

        # Проверяем, что методы вызывались правильно
        mock_select.assert_called_once_with(User.chat_id)
        mock_select.return_value.distinct.assert_called_once()

        # Проверяем, что get_users_without_report_yesterday вызывался для каждого чата
        assert mock_get_users.call_count == 2
        mock_get_users.assert_any_call(100)
        mock_get_users.assert_any_call(200)


@pytest.mark.asyncio
async def test_get_users_without_report_yesterday_all_reported():
    # Подготовка тестовых данных
    yesterday = datetime.now() - timedelta(days=1)

    # Создаем тестовых пользователей, все отправили отчет вчера
    user1 = MagicMock(spec=User)
    user1.telegram_id = 123
    user1.username = "user1"
    user1.last_report_date_time = yesterday

    user2 = MagicMock(spec=User)
    user2.telegram_id = 456
    user2.username = "user2"
    user2.last_report_date_time = yesterday

    test_chat_id = 100

    # Мокаем запрос к базе данных
    with patch("usecase.User.select") as mock_select:
        # Возвращаем пустой список, т.к. все отправили отчет
        mock_select.return_value.where.return_value = []

        # Вызываем тестируемую функцию
        users = await get_users_without_report_yesterday(test_chat_id)

        # Проверяем что список пользователей пуст
        assert len(users) == 0

        # Проверяем что запрос был выполнен с правильными параметрами
        mock_select.assert_called_once_with(User.telegram_id, User.username)
        mock_select.return_value.where.assert_called_once()
