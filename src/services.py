import json
import logging
from collections import defaultdict
from datetime import datetime
from functools import reduce

logger = logging.getLogger(__name__)


def get_beneficial_cashback_categories(data, year, month):
    """
    Функция «Выгодные категории повышенного кешбэка»

    :param data: Список транзакций
    :param year: Год для анализа
    :param month: Месяц для анализа
    :return: JSON строка с анализом кэшбэка по категориям
    """

    logger.info("Начинается анализ категорий кешбэка за %d-%02d", year, month)

    # Функция для фильтрации транзакций по году и месяцу
    is_in_month = (
        lambda x: datetime.strptime(x["date"], "%Y-%m-%d").year == year
        and datetime.strptime(x["date"], "%Y-%m-%d").month == month
    )

    filtered_transactions = list(filter(is_in_month, data))
    logger.info("Отфильтрованные транзакции: %s", filtered_transactions)

    # Функция для аккумулирования сумм по категориям
    def accumulate(acc, transaction):
        category = transaction["category"]
        amount = abs(transaction["amount"])
        acc[category] += amount
        return acc

    category_cashback = reduce(accumulate, filtered_transactions, defaultdict(int))

    # Формируем кэшбэк (1% от суммы) и превращаем его в обычный словарь
    cashbacks = {category: round(amount * 0.01) for category, amount in category_cashback.items()}

    logger.info("Сумма cashback: %s", cashbacks)

    return json.dumps(cashbacks, ensure_ascii=False, indent=4)