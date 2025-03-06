import json
import logging
from datetime import datetime

import pandas as pd

from src.reports import spending_by_category
from src.services import get_beneficial_cashback_categories
from src.views import analyze_data

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    """Основная функция для выполнения анализа данных."""
    logger.info("Запуск программы")

    try:
        # Пример данных для анализа кешбэка
        transactions = [
            {"date": "2023-10-01", "amount": -1500, "category": "Еда"},
            {"date": "2023-10-05", "amount": -2000, "category": "Транспорт"},
            {"date": "2023-10-10", "amount": -3000, "category": "Наличные"},
            {"date": "2023-10-12", "amount": -1000, "category": "Развлечения"},
            {"date": "2023-09-15", "amount": -500, "category": "Еда"},
        ]

        # Вызов функции для анализа выгодных категорий кешбэка
        logger.info("Анализ выгодных категорий кешбэка")
        result = get_beneficial_cashback_categories(transactions, 2023, 10)
        print(json.dumps(result, ensure_ascii=False, indent=4))

        # Пример данных для анализа трат по категориям
        data = {
            "Дата операции": ["2021-12-31 16:44:00", "2022-01-01 12:00:00", "2022-01-15 18:30:00"],
            "Категория": ["Фастфуд", "Каршеринг", "Аптеки"],
            "Сумма операции": [-1500, -2000, -3000]
        }
        transactions_df = pd.DataFrame(data)

        # Сохранение данных в Excel (для тестирования)
        logger.info("Сохранение данных в Excel")
        transactions_df.to_excel(r"C:\Users\Pavel\PycharmProjects\Course_project_1\data\new_operations.xlsx", index=False)

        # Вызов функции для анализа трат по категории
        logger.info("Анализ трат по категории 'Каршеринг'")
        result = spending_by_category(transactions_df, "Каршеринг")
        print(json.dumps(result, ensure_ascii=False, indent=4))

        # Вызов функции анализа данных для веб-страницы "События"
        logger.info("Анализ данных для веб-страницы 'События'")
        result = analyze_data(date_str="31.12.2021 16:44:00", data_range="M")
        print(json.dumps(result, ensure_ascii=False, indent=4))

    except Exception as e:
        logger.error(f"Ошибка при выполнении программы: {e}")
    finally:
        logger.info("Программа завершена")


if __name__ == "__main__":
    main()
