import logging
from datetime import datetime, timedelta
from functools import lru_cache
import pandas as pd
import requests
from config import API_KEY_EXCHANGE, API_KEY_MARKETSTACK  # Импортируем API-ключи из конфигурации

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def get_data_range(date_str: str, data_range: str) -> tuple[datetime, datetime]:
    """
    Возвращает диапазон дат в зависимости от указанного периода.

    :param date_str: Строка даты в формате 'DD.MM.YYYY' или 'DD.MM.YYYY HH:MM:SS'
    :param data_range: Период ('M' - месяц, 'W' - неделя, 'Y' - год, 'ALL' - весь период)
    :return: Кортеж (start_date, end_date)
    """
    if len(date_str) == 10:  # формат 'DD.MM.YYYY'
        date_str += " 00:00:00"
        logger.debug(f"Преобразована строка даты: {date_str}")

    try:
        parsed_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
        logger.debug(f"Разобранная дата: {parsed_date}")
    except ValueError as e:
        logger.error(f"Некорректный формат даты: {date_str}")
        raise ValueError("Некорректный формат даты") from e

    if data_range == "M":
        start_date = parsed_date.replace(day=1, hour=0, minute=0, second=0)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        logger.debug(f"Месячный период: {start_date} - {end_date}")

    elif data_range == "W":
        start_date = parsed_date - timedelta(days=parsed_date.weekday())  # Понедельник
        end_date = start_date + timedelta(days=6)  # Воскресенье
        end_date = end_date.replace(hour=23, minute=59, second=59)
        logger.debug(f"Недельный период: {start_date} - {end_date}")

    elif data_range == "Y":
        start_date = parsed_date.replace(month=1, day=1, hour=0, minute=0, second=0)
        end_date = parsed_date.replace(month=12, day=31, hour=23, minute=59, second=59)
        logger.debug(f"Годовой диапазон: {start_date} - {end_date}")

    elif data_range == "ALL":
        start_date = datetime(2021, 1, 1, 16, 44, 0)
        end_date = parsed_date
        logger.debug(f"Период даты и времени: {start_date} - {end_date}")

    else:
        logger.error("Недопустимый период")
        raise ValueError("Недопустимый период")

    return start_date, end_date


@lru_cache(maxsize=32)
def get_currency_rates(currencies: tuple[str, ...]) -> dict[str, dict[str, float]]:
    """
    Получает курсы валют.

    :param currencies: Кортеж валют
    :return: Словарь с курсами валют
    """
    rates = {}
    for currency in currencies:
        logger.debug(f"Запрос курсов для валюты: {currency}")
        try:
            response = requests.get(
                f"https://v6.exchangerate-api.com/v6/{API_KEY_EXCHANGE}/latest/{currency}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("result") == "success":
                rates[currency] = data.get("conversion_rates", {})
                logger.info(f"Успешно получены курсы для {currency}: {rates[currency]}")
            else:
                logger.error(f"Ошибка в ответе API для {currency}: {data.get('error-type', 'Неизвестная ошибка')}")
                rates[currency] = {}
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении курса для {currency}: {e}")
            rates[currency] = {}
    return rates


@lru_cache(maxsize=32)
def get_stock_prices(stocks: tuple[str, ...]) -> dict[str, float]:
    """
    Получает цены акций.

    :param stocks: Кортеж акций
    :return: Словарь с ценами акций
    """
    prices = {}
    for stock in stocks:
        logger.debug(f"Запрос цены для акции: {stock}")
        try:
            response = requests.get(
                f"https://api.marketstack.com/v1/eod?access_key={API_KEY_MARKETSTACK}&symbols={stock}",
                timeout=10,
            )
            response.raise_for_status()
            data = response.json()
            if data.get("data"):
                prices[stock] = data["data"][0].get("close")
                logger.info(f"Успешно получена цена для {stock}: {prices[stock]}")
            else:
                logger.error(f"Ошибка в ответе API для {stock}: {data.get('error', 'Неизвестная ошибка')}")
                prices[stock] = None
        except requests.RequestException as e:
            logger.error(f"Ошибка при получении цены для {stock}: {e}")
            prices[stock] = None
    return prices


def group_expenses(filtered_data: pd.DataFrame) -> pd.DataFrame:
    """
    Группирует расходы по категориям и возвращает основные категории.

    :param filtered_data: Отфильтрованные данные
    :return: DataFrame с группированными расходами
    """
    logger.debug("Начало группировки расходов")
    if filtered_data.empty:
        logger.warning("Нет данных для группировки расходов")
        return pd.DataFrame(columns=["Категория", "Сумма операции"])

    if "Категория" not in filtered_data.columns or "Сумма операции" not in filtered_data.columns:
        logger.error("Отсутствуют необходимые столбцы в данных")
        raise ValueError("Отсутствуют необходимые столбцы в данных")

    expenses_by_category = (
        filtered_data[filtered_data["Сумма операции"] < 0].groupby("Категория")["Сумма операции"].sum().reset_index()
    )
    expenses_by_category["Сумма операции"] = expenses_by_category["Сумма операции"].round(0)
    top_expenses = expenses_by_category.nlargest(7, "Сумма операции")
    other_expenses_sum = expenses_by_category.loc[
        ~expenses_by_category["Категория"].isin(top_expenses["Категория"]), "Сумма операции"
    ].sum()

    other_expenses = pd.DataFrame({"Категория": ["Остальное"], "Сумма операции": [other_expenses_sum]})
    combined_expenses = pd.concat([top_expenses, other_expenses], ignore_index=True)

    logger.info("Группировка расходов завершена")
    return combined_expenses


def group_income(filtered_data: pd.DataFrame) -> pd.DataFrame:
    """
    Группирует поступления по категориям и возвращает основные категории.

    :param filtered_data: Отфильтрованные данные
    :return: DataFrame с группированными поступлениями
    """
    logger.debug("Начало группировки поступлений")
    if filtered_data.empty:
        logger.warning("Нет данных для группировки поступлений")
        return pd.DataFrame(columns=["Категория", "Сумма операции"])

    if "Категория" not in filtered_data.columns or "Сумма операции" not in filtered_data.columns:
        logger.error("Отсутствуют необходимые столбцы в данных")
        raise ValueError("Отсутствуют необходимые столбцы в данных")

    income_by_category = (
        filtered_data[filtered_data["Сумма операции"] > 0].groupby("Категория")["Сумма операции"].sum().reset_index()
    )
    income_by_category["Сумма операции"] = income_by_category["Сумма операции"].round(0)
    top_income = income_by_category.nlargest(7, "Сумма операции")
    other_income_sum = income_by_category.loc[
        ~income_by_category["Категория"].isin(top_income["Категория"]), "Сумма операции"
    ].sum()
    other_income = pd.DataFrame({"Категория": ["Остальное"], "Сумма операции": [other_income_sum]})
    combined_income = pd.concat([top_income, other_income], ignore_index=True)

    logger.info("Группировка поступлений завершена")
    return combined_income
