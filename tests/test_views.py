from datetime import datetime
from unittest.mock import patch

import pandas as pd
import pytest
import requests

from src.utils import get_data_range, get_stock_prices, group_expenses, group_income


# Тесты для функции get_data_range
@pytest.mark.parametrize(
    "date_str, data_range, expected_start, expected_end",
    [
        ("01.01.2023", "M", datetime(2023, 1, 1, 0, 0, 0), datetime(2023, 1, 31, 23, 59, 59)),
        ("01.01.2023", "W", datetime(2022, 12, 26, 0, 0, 0), datetime(2023, 1, 1, 23, 59, 59)),
        ("01.01.2023", "Y", datetime(2023, 1, 1, 0, 0, 0), datetime(2023, 12, 31, 23, 59, 59)),
        ("01.01.2023", "ALL", datetime(2021, 1, 1, 16, 44, 0), datetime(2023, 1, 1, 0, 0, 0)),
    ],
)
def test_get_data_range(date_str, data_range, expected_start, expected_end):
    """Проверка корректности вычисления диапазона дат."""
    start, end = get_data_range(date_str, data_range)
    assert start == expected_start
    assert end == expected_end


@pytest.mark.parametrize(
    "date_str, data_range, expected_error",
    [
        ("01.01.2023", "INVALID", ValueError),
        ("invalid_date", "M", ValueError),
        ("", "M", ValueError),
        (None, "M", ValueError),
    ],
)
def test_get_data_range_invalid_input(date_str, data_range, expected_error):
    """Проверка обработки некорректных входных данных."""
    with pytest.raises(expected_error):
        get_data_range(date_str, data_range)


# Тесты для функции get_stock_prices
@patch("requests.get")
def test_get_stock_prices_success(mock_get):
    """Проверка успешного получения цен акций."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {"price": 150}

    prices = get_stock_prices(["AAPL"])
    assert prices == {"AAPL": 150}


@patch("requests.get")
def test_get_stock_prices_empty_response(mock_get):
    """Проверка обработки пустого ответа от API."""
    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {}

    prices = get_stock_prices(["AAPL"])
    assert prices["AAPL"] is None


@patch("requests.get")
def test_get_stock_prices_request_exception(mock_get):
    """Проверка обработки ошибки запроса."""
    mock_get.side_effect = requests.RequestException("Network error")

    prices = get_stock_prices(["AAPL"])
    assert prices["AAPL"] is None


# Тесты для функции group_expenses
def test_group_expenses():
    """Проверка группировки расходов."""
    data = pd.DataFrame(
        {"Категория": ["Еда", "Транспорт", "Еда", "Развлечения"], "Сумма операции": [-50, -20, -30, -10]}
    )

    result = group_expenses(data)
    assert result.shape[0] == 3  # Еда, Транспорт, Развлечения
    assert "Остальное" not in result["Категория"].values  # Нет категории "Остальное", так как все категории уникальны


def test_group_expenses_empty_data():
    """Проверка обработки пустого DataFrame."""
    data = pd.DataFrame(columns=["Категория", "Сумма операции"])

    result = group_expenses(data)
    assert result.empty


# Тесты для функции group_income
def test_group_income():
    """Проверка группировки поступлений."""
    data = pd.DataFrame(
        {"Категория": ["Зарплата", "Инвестиции", "Зарплата", "Подарки"], "Сумма операции": [1000, 200, 500, 100]}
    )

    result = group_income(data)
    assert result.shape[0] == 3  # Зарплата, Инвестиции, Подарки
    assert "Остальное" not in result["Категория"].values  # Нет категории "Остальное", так как все категории уникальны
    assert result["Сумма операции"].sum() == 1800  # Проверка суммы поступлений


def test_group_income_empty_data():
    """Проверка обработки пустого DataFrame."""
    data = pd.DataFrame(columns=["Категория", "Сумма операции"])

    result = group_income(data)
    assert result.empty
