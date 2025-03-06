import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional
import os
import pandas as pd
from config import REPORTS_DIR  # Импортируем путь к директории отчетов

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def log_report_to_file(filename):
    """Декоратор для записи отчета в файл."""

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            df = func(*args, **kwargs)
            logger.info("Проверка: являются ли данные датафреймом")
            if isinstance(df, pd.DataFrame):
                # Создание директории, если она не существует
                os.makedirs(os.path.dirname(filename), exist_ok=True)
                if os.path.exists(filename):
                    logger.warning(f"Файл '{filename}' уже существует. Он будет перезаписан.")
                logger.info(f"Запись отчёта в файл '{filename}'")
                df.to_json(filename, orient="records", lines=True, force_ascii=False)
            else:
                logger.error("Данные не являются датафреймом. В файл записаны не будут")
            return df

        return inner

    return wrapper


def validate_transactions(transactions: pd.DataFrame, required_columns: set) -> bool:
    """
    Проверяет наличие необходимых колонок в DataFrame.

    :param transactions: DataFrame с транзакциями
    :param required_columns: Множество необходимых колонок
    :return: True, если все колонки присутствуют, иначе False
    """
    missing_columns = required_columns - set(transactions.columns)
    if missing_columns:
        logger.error(f"Отсутствуют необходимые колонки: {missing_columns}")
        return False
    return True


def filter_transactions_by_date(transactions: pd.DataFrame, category: str, start_date, end_date) -> pd.DataFrame:
    """
    Фильтрует транзакции по категории и дате.

    :param transactions: DataFrame с транзакциями
    :param category: Категория для фильтрации
    :param start_date: Начальная дата
    :param end_date: Конечная дата
    :return: Отфильтрованный DataFrame
    """
    return transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
        & (transactions["Сумма операции"] < 0)  # Учитываем только расходы
    ]


@log_report_to_file(os.path.join(REPORTS_DIR, "spending_report.json"))
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
    """Функция для вычисления трат по категории за последние три месяца."""

    # Проверка наличия необходимых колонок
    required_columns = {"Категория", "Дата операции", "Сумма операции"}
    if not validate_transactions(transactions, required_columns):
        return {}

    # Преобразуем колонку с датами в datetime
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%Y-%m-%d", errors="coerce")

    # Проверка на наличие некорректных дат
    if transactions["Дата операции"].isnull().any():
        logger.warning("Обнаружены некорректные даты. Они будут исключены из анализа.")
        transactions = transactions.dropna(subset=["Дата операции"])

    # Установка даты
    if date is None:
        date = datetime.now()
    else:
        date = datetime.strptime(date, "%Y-%m-%d")

    # Получение даты три месяца назад
    three_months_ago = date - timedelta(days=90)

    # Фильтрация DataFrame по категории и дате
    logger.info(f"Фильтрация данных для категории '{category}' за период с {three_months_ago} по {date}")
    filtered_expenses = filter_transactions_by_date(transactions, category, three_months_ago, date)

    # Проверка на наличие отфильтрованных расходов
    if filtered_expenses.empty:
        logger.warning(f"Нет расходов для категории '{category}' за период с {three_months_ago} по {date}.")
        return {
            "category": category,
            "total_expenses": 0,
            "date_from": three_months_ago.strftime("%Y-%m-%d"),
            "date_to": date.strftime("%Y-%m-%d"),
        }

    # Подсчет общих трат
    total_expenses = filtered_expenses["Сумма операции"].sum()

    report = {
        "category": category,
        "total_expenses": total_expenses,
        "date_from": three_months_ago.strftime("%Y-%m-%d"),
        "date_to": date.strftime("%Y-%m-%d"),
    }

    logger.info(
        f"Отчет создан для категории '{category}': "
        f"найдено {len(filtered_expenses)} транзакций, общая сумма расходов: {total_expenses}"
    )
    return report
