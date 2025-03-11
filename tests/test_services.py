import pytest
from datetime import datetime
from unittest.mock import patch
from src.services import get_beneficial_cashback_categories


# Фикстура для создания тестовых данных
@pytest.fixture
def transactions():
    return [
        {"date": "2023-10-01", "amount": -1500, "category": "Еда"},
        {"date": "2023-10-05", "amount": -2000, "category": "Транспорт"},
        {"date": "2023-10-10", "amount": -3000, "category": "Наличные"},
        {"date": "2023-10-12", "amount": -1000, "category": "Развлечения"},
        {"date": "2023-09-15", "amount": -500, "category": "Еда"},  # Транзакция за другой месяц
        {"date": "invalid_date", "amount": -100, "category": "Некорректная дата"},  # Некорректная дата
    ]


@patch("src.services.logger")
def test_get_beneficial_cashback_categories_correct_data(mock_logger, transactions):
    """Тест на корректные данные."""
    result = get_beneficial_cashback_categories(transactions, 2023, 10)

    expected_result = {
        "Еда": 15,  # 1% от 1500
        "Транспорт": 20,  # 1% от 2000
        "Наличные": 30,  # 1% от 3000
        "Развлечения": 10,  # 1% от 1000
    }
    assert result == expected_result  # Проверяем результат

    # Проверка логов
    mock_logger.info.assert_any_call("Начинается анализ категорий кешбэка за 2023-10")
    mock_logger.info.assert_any_call("Найдено 4 транзакций за указанный период")
    mock_logger.info.assert_any_call("Сумма cashback: {'Еда': 15, 'Транспорт': 20, 'Наличные': 30, 'Развлечения': 10}")
    mock_logger.warning.assert_called_with("Некорректная дата в транзакции: {'date': 'invalid_date', 'amount': -100, 'category': 'Некорректная дата'}")


@patch("src.services.logger")
def test_get_beneficial_cashback_categories_no_transactions(mock_logger):
    """Тест на отсутствие транзакций."""
    result = get_beneficial_cashback_categories([], 2023, 10)

    expected_result = {}
    assert result == expected_result  # Проверяем результат

    # Проверка логов
    mock_logger.info.assert_any_call("Начинается анализ категорий кешбэка за 2023-10")
    mock_logger.info.assert_any_call("Найдено 0 транзакций за указанный период")
    mock_logger.info.assert_any_call("Сумма cashback: {}")


@patch("src.services.logger")
def test_get_beneficial_cashback_categories_invalid_data(mock_logger):
    """Тест на некорректные данные."""
    transactions = [
        {"date": "invalid_date", "amount": -100, "category": "Некорректная дата"},
        {"date": "2023-10-01", "amount": -1500, "category": "Еда"},
    ]
    result = get_beneficial_cashback_categories(transactions, 2023, 10)

    expected_result = {"Еда": 15}  # Только корректная транзакция
    assert result == expected_result  # Проверяем результат

    # Проверка логов
    mock_logger.warning.assert_called_with("Некорректная дата в транзакции: {'date': 'invalid_date', 'amount': -100, 'category': 'Некорректная дата'}")


@patch("src.services.logger")
def test_get_beneficial_cashback_categories_out_of_range(mock_logger, transactions):
    """Тест на транзакции вне указанного периода."""
    result = get_beneficial_cashback_categories(transactions, 2023, 9)

    expected_result = {"Еда": 5}  # 1% от 500 (транзакция за сентябрь)
    assert result == expected_result  # Проверяем результат

    # Проверка логов
    mock_logger.info.assert_any_call("Начинается анализ категорий кешбэка за 2023-09")
    mock_logger.info.assert_any_call("Найдено 1 транзакций за указанный период")
    mock_logger.info.assert_any_call("Сумма cashback: {'Еда': 5}")
    mock_logger.warning.assert_called_with("Некорректная дата в транзакции: {'date': 'invalid_date', 'amount': -100, 'category': 'Некорректная дата'}")


if __name__ == "__main__":
    pytest.main()
