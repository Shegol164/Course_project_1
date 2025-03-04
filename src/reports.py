import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

from config import file_path

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def log_report_to_file(filename):
    """Декоратор для записи отчета в файл."""

    def wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            df = func(*args, **kwargs)
            logger.info("Проверка: являются ли данные датафреймом")
            if isinstance(df, pd.DataFrame):
                logger.info("Запись отчёта в файл")
                df.to_json(filename, orient="records", lines=True, force_ascii=False)
            else:
                logger.error("Данные не являются датафреймом. В файл записаны не будут")
            return df

        return inner

    return wrapper


def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> dict:
    """Функция для вычисления трат по категории за последние три месяца."""

    if "Категория" in transactions.columns:
        category_data = transactions["Категория"]
        print(category_data)
    else:
        print("Столбец 'Категория' не найден.")
        return {}

    if date is None:
        date = datetime.now()
    else:
        date = datetime.strptime(date, "%Y-%m-%d")

    # Получение даты три месяца назад
    three_months_ago = date - timedelta(days=90)

    # Фильтрация DataFrame по категории и дате
    filtered_expenses = transactions[
        (transactions["Категория"] == category)
        & (transactions["Дата операции"] >= three_months_ago)
        & (transactions["Дата операции"] <= date)
    ]

    # Проверка на наличие отфильтрованных расходов
    if filtered_expenses.empty:
        logger.warning(f"Нет расходов для категории '{category}' за указанный период.")
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

    logger.info(f"Отчет создан для категории '{category}': {report}")
    return report