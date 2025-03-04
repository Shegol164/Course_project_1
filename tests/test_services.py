import json
import logging
from unittest.mock import patch

import pytest

from src.services import get_beneficial_cashback_categories

# Включаем логирование для тестов
logging.basicConfig(level=logging.INFO)


@pytest.fixture
def transactions():
    return [
        {"date": "2023-10-01", "amount": -1500, "category": "Еда"},
        {"date": "2023-10-05", "amount": -2000, "category": "Транспорт"},
        {"date": "2023-10-10", "amount": -3000, "category": "Наличные"},
        {"date": "2023-10-12", "amount": -1000, "category": "Развлечения"},
        {"date": "2023-09-15", "amount": -500, "category": "Еда"},
    ]


@patch("logging.getLogger")
def test_get_beneficial_cashback_categories(mock_logger, transactions):
    """Тестируем получение выгодных категорий кешбэка."""
    result = get_beneficial_cashback_categories(transactions, 2023, 10)

    expected_result = {
        "Еда": 15,  # 1% от 1500
        "Транспорт": 20,  # 1% от 2000
        "Наличные": 30,  # 1% от 3000
        "Развлечения": 10,  # 1% от 1000
    }
    assert json.loads(result) == expected_result  # Проверяем результат


@patch("logging.getLogger")
def test_no_transactions(mock_logger):
    """Тестируем случай, когда нет транзакций за указанный месяц."""
    result = get_beneficial_cashback_categories([], 2023, 10)

    expected_result = {}
    assert json.loads(result) == expected_result  # Проверяем результат


@patch("logging.getLogger")
def test_only_unwanted_transactions(mock_logger, transactions):
    """Тестируем случай, когда все транзакции вне указанного месяца."""
    result = get_beneficial_cashback_categories(transactions, 2023, 9)

    expected_result = {"Еда": 5}
    assert json.loads(result) == expected_result  # Проверяем результат


if __name__ == "__main__":
    pytest.main()