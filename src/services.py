import logging
from collections import defaultdict
from datetime import datetime
from functools import reduce

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_beneficial_cashback_categories(data, year, month):
    """
    Функция «Выгодные категории повышенного кешбэка»

    :param data: Список транзакций
    :param year: Год для анализа
    :param month: Месяц для анализа
    :return: Словарь с анализом кэшбэка по категориям
    """

    logger.info("Начинается анализ категорий кешбэка за %d-%02d", year, month)

    # Функция для фильтрации транзакций по году и месяцу
    def is_in_month(transaction):
        try:
            date = datetime.strptime(transaction["date"], "%Y-%m-%d")
            return date.year == year and date.month == month
        except (ValueError, KeyError):
            logger.warning(f"Некорректная дата в транзакции: {transaction}")
            return False

    # Фильтрация транзакций
    filtered_transactions = list(filter(is_in_month, data))
    logger.info("Найдено %d транзакций за указанный период", len(filtered_transactions))
    logger.debug("Отфильтрованные транзакции: %s", filtered_transactions)

    # Функция для аккумулирования сумм по категориям
    def accumulate(acc, transaction):
        category = transaction["category"]
        amount = abs(transaction["amount"])
        acc[category] += amount
        return acc

    # Аккумулирование сумм по категориям
    category_cashback = reduce(accumulate, filtered_transactions, defaultdict(int))

    # Расчет кешбэка (1% от суммы)
    CASHBACK_RATE = 0.01
    cashbacks = {category: round(amount * CASHBACK_RATE) for category, amount in category_cashback.items()}

    logger.info("Сумма cashback: %s", cashbacks)
    return cashbacks
