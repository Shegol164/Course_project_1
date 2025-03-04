import logging
import os
from datetime import datetime, timedelta
from unittest.mock import patch

import pandas as pd
import pytest

from src.reports import log_report_to_file, spending_by_category

# Настройка логирования
logger = logging.getLogger(__name__)


# Фикстура для генерации тестовых данных
@pytest.fixture
def transactions_data():
    data = {
        "Дата операции": [
            datetime(2023, 1, 15),
            datetime(2023, 2, 15),
            datetime(2023, 3, 15),
            datetime(2023, 4, 15),
            datetime(2023, 5, 15),
        ],
        "Категория": ["Еда", "Транспорт", "Еда", "Развлечения", "Еда"],
        "Сумма операции": [-100, -50, -200, -300, -150],
    }
    return pd.DataFrame(data)

# Тест для функции spending_by_category
def test_spending_by_category_no_data(transactions_data):
    # Проверяем расходы по категории "Недвижимость", которой нет в данных
    result = spending_by_category(transactions_data, "Недвижимость")

    assert result["category"] == "Недвижимость"
    assert result["total_expenses"] == 0
    assert "date_from" in result
    assert "date_to" in result


def test_spending_by_category_missing_category_column(transactions_data):
    transactions_data_missing_column = transactions_data.drop(columns=["Категория"])

    # Проверяем, если столбец 'Категория' отсутствует
    result = spending_by_category(transactions_data_missing_column, "Еда")

    assert result == {}

@pytest.fixture
def transactions():
    return pd.DataFrame({
        "Дата операции": [
            datetime(2023, 1, 15),
            datetime(2023, 2, 20),
            datetime(2023, 3, 5),
            datetime(2023, 4, 10),
            datetime(2023, 4, 15)
        ],
        "Категория": [
            "Еда",
            "Транспорт",
            "Еда",
            "Развлечения",
            "Еда"
        ],
        "Сумма операции": [
            100,
            50,
            200,
            300,
            150
        ]
    })

def test_spending_by_category_success(transactions):
    category = "Еда"
    result = spending_by_category(transactions, category)

    assert result["category"] == category
    assert result["date_from"] == (datetime.now() - timedelta(days=90)).strftime("%Y-%m-%d")
    assert result["date_to"] == datetime.now().strftime("%Y-%m-%d")

def test_spending_by_category_no_expenses(transactions):
    category = "Транспорт"
    with patch('src.reports.logger') as mock_logger:
        result = spending_by_category(transactions, category)

    assert result["category"] == category
    assert result["total_expenses"] == 0
    assert "Нет расходов для категории" in str(mock_logger.warning.call_args)

def test_spending_by_category_no_category(transactions):
    transactions_no_category = transactions.drop(columns=["Категория"])
    with patch('src.reports.logger') as mock_logger:
        result = spending_by_category(transactions_no_category, "Еда")

    assert result == {}

def test_spending_by_category_with_date(transactions):
    category = "Еда"
    date = "2023-04-01"
    result = spending_by_category(transactions, category, date)

    assert result["category"] == category
    assert result["total_expenses"] == 300  # 200 + 100
    assert result["date_from"] == (datetime.strptime(date, "%Y-%m-%d") - timedelta(days=90)).strftime("%Y-%m-%d")
    assert result["date_to"] == date

#Тесты для функции log_report_to_file
@pytest.fixture
def temp_filename(tmp_path):
    return tmp_path / "report.json"

# Тест на успешную запись DataFrame в файл
def test_log_report_to_file_success(temp_filename):
    @log_report_to_file(temp_filename)
    def sample_function():
        return pd.DataFrame({"column1": [1, 2], "column2": [3, 4]})

    with patch('src.reports.logger') as mock_logger:
        result = sample_function()

    # Проверяем результат выполнения функции
    assert isinstance(result, pd.DataFrame)
    assert not result.empty

    # Проверяем, что файл создан
    assert os.path.exists(temp_filename)

    # Проверяем содержимое JSON файла
    with open(temp_filename) as f:
        file_content = f.readlines()
        assert len(file_content) == 2  # Должно быть две строки

    # Проверка логов
    mock_logger.info.assert_any_call("Проверка: являются ли данные датафреймом")
    mock_logger.info.assert_any_call("Запись отчёта в файл")


# Тест на попытку записи не DataFrame
def test_log_report_to_file_not_dataframe(temp_filename):
    @log_report_to_file(temp_filename)
    def sample_function():
        return "Not a DataFrame"

    with patch('src.reports.logger') as mock_logger:
        result = sample_function()

    # Проверяем результат выполнения функции
    assert result == "Not a DataFrame"

    # Проверяем, что файл не был создан
    assert not os.path.exists(temp_filename)

    # Проверка логов
    mock_logger.info.assert_any_call("Проверка: являются ли данные датафреймом")
    mock_logger.error.assert_called_once_with("Данные не являются датафреймом. В файл записаны не будут")