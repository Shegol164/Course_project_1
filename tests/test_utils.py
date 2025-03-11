import pytest
from datetime import datetime, timedelta
from unittest.mock import patch, Mock
import pandas as pd
import requests
from src.utils import (
    get_data_range,
    get_currency_rates,
    get_stock_prices,
    group_expenses,
    group_income,
)


# Тесты для функции get_data_range
def test_get_data_range_month():
    """Тест на корректный ввод данных для месяца."""
    start_date, end_date = get_data_range("01.10.2023", "M")
    assert start_date == datetime(2023, 10, 1, 0, 0, 0)
    assert end_date == datetime(2023, 10, 31, 23, 59, 59)


def test_get_data_range_week():
    """Тест на корректный ввод данных для недели."""
    start_date, end_date = get_data_range("01.10.2023", "W")
    assert start_date == datetime(2023, 9, 25, 0, 0, 0)  # Понедельник
    assert end_date == datetime(2023, 10, 1, 23, 59, 59)  # Воскресенье


def test_get_data_range_year():
    """Тест на корректный ввод данных для года."""
    start_date, end_date = get_data_range("01.10.2023", "Y")
    assert start_date == datetime(2023, 1, 1, 0, 0, 0)
    assert end_date == datetime(2023, 12, 31, 23, 59, 59)


def test_get_data_range_all():
    """Тест на корректный ввод данных для всего периода."""
    start_date, end_date = get_data_range("01.10.2023", "ALL")
    assert start_date == datetime(2021, 1, 1, 16, 44, 0)
    assert end_date == datetime(2023, 10, 1, 0, 0, 0)


def test_get_data_range_invalid_date():
    """Тест на некорректный формат даты."""
    with pytest.raises(ValueError):
        get_data_range("invalid_date", "M")


def test_get_data_range_invalid_period():
    """Тест на недопустимый период."""
    with pytest.raises(ValueError):
        get_data_range("01.10.2023", "INVALID")


# Тесты для функции get_currency_rates
@patch("requests.get")
def test_get_currency_rates_success(mock_get):
    """Тест на корректный запрос курсов валют."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "result": "success",
        "conversion_rates": {"USD": 1.0, "EUR": 0.85},
    }
    mock_get.return_value = mock_response

    result = get_currency_rates(["USD"])
    assert result == {"USD": {"USD": 1.0, "EUR": 0.85}}


@patch("requests.get")
def test_get_currency_rates_api_error(mock_get):
    """Тест на ошибку API."""
    mock_response = Mock()
    mock_response.json.return_value = {"result": "error", "error-type": "API error"}
    mock_get.return_value = mock_response

    result = get_currency_rates(["USD"])
    assert result == {"USD": {}}


# Тесты для функции get_stock_prices
@patch("requests.get")
def test_get_stock_prices_success(mock_get):
    """Тест на корректный запрос цен акций."""
    mock_response = Mock()
    mock_response.json.return_value = {"data": [{"close": 150.0}]}
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL"])
    assert result == {"AAPL": 150.0}


@patch("requests.get")
def test_get_stock_prices_api_error(mock_get):
    """Тест на ошибку API."""
    mock_response = Mock()
    mock_response.json.return_value = {"error": "API error"}
    mock_get.return_value = mock_response

    result = get_stock_prices(["AAPL"])
    assert result == {"AAPL": None}


# Тесты для функции group_expenses
def test_group_expenses():
    """Тест на группировку расходов."""
    data = pd.DataFrame({
        "Категория": ["Еда", "Транспорт", "Еда"],
        "Сумма операции": [-1000, -2000, -1500],
    })
    result = group_expenses(data)
    expected = pd.DataFrame({
        "Категория": ["Еда", "Транспорт", "Остальное"],
        "Сумма операции": [-2500, -2000, 0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_group_expenses_no_data():
    """Тест на отсутствие данных."""
    data = pd.DataFrame(columns=["Категория", "Сумма операции"])
    result = group_expenses(data)
    assert result.empty


def test_group_expenses_missing_columns():
    """Тест на отсутствие необходимых колонок."""
    data = pd.DataFrame({"Категория": ["Еда"]})
    with pytest.raises(ValueError):
        group_expenses(data)


# Тесты для функции group_income
def test_group_income():
    """Тест на группировку поступлений."""
    data = pd.DataFrame({
        "Категория": ["Зарплата", "Дивиденды", "Зарплата"],
        "Сумма операции": [10000, 5000, 12000],
    })
    result = group_income(data)
    expected = pd.DataFrame({
        "Категория": ["Зарплата", "Дивиденды", "Остальное"],
        "Сумма операции": [22000, 5000, 0],
    })
    pd.testing.assert_frame_equal(result, expected)


def test_group_income_no_data():
    """Тест на отсутствие данных."""
    data = pd.DataFrame(columns=["Категория", "Сумма операции"])
    result = group_income(data)
    assert result.empty


def test_group_income_missing_columns():
    """Тест на отсутствие необходимых колонок."""
    data = pd.DataFrame({"Категория": ["Зарплата"]})
    with pytest.raises(ValueError):
        group_income(data)


if __name__ == "__main__":
    pytest.main()