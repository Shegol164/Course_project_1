import logging
from datetime import datetime, timedelta

import pandas as pd
import requests

# Настройка логирования
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s")


def get_data_range(date_str, data_range):
    # Преобразуйте входную строку на случай, если время отсутствует
    if len(date_str) == 10:  # формат 'DD.MM.YYYY'
        date_str += " 00:00:00"
        logging.debug(f"Преобразована строка даты: {date_str}")

    # Теперь можно безопасно разбирать строку
    parsed_date = datetime.strptime(date_str, "%d.%m.%Y %H:%M:%S")
    logging.debug(f"Разобранная дата: {parsed_date}")

    if data_range == "M":
        start_date = parsed_date.replace(hour=0, minute=0, second=0)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(seconds=1)
        end_date = end_date.replace(hour=23, minute=59, second=59)
        logging.debug(f"Месячный период: {start_date} - {end_date}")

    elif data_range == "W":
        start_date = parsed_date - timedelta(days=parsed_date.weekday())  # Понедельник
        end_date = start_date + timedelta(days=6)  # Воскресенье
        end_date = end_date.replace(hour=23, minute=59, second=59)
        logging.debug(f"Недельный период: {start_date} - {end_date}")

    elif data_range == "Y":
        start_date = parsed_date.replace(month=1, day=1, hour=0, minute=0, second=0)
        end_date = parsed_date.replace(month=12, day=31, hour=23, minute=59, second=59)
        logging.debug(f"Годовой диапазон: {start_date} - {end_date}")

    elif data_range == "ALL":
        # Логика для ALL
        start_date = datetime(2021, 1, 1, 16, 44, 0)
        end_date = parsed_date
        logging.debug(f"Период даты и времени: {start_date} - {end_date}")

    else:
        logging.error("Недопустимый период")
        raise ValueError("Invalid period")

    return start_date, end_date


def get_currency_rates(currencies):
    rates = {}
    for currency in currencies:
        logging.debug(f"Запрос курсов для валюты: {currency}")
        try:
            response = requests.get(
                f"https://v6.exchangerate-api.com/v6/ed5608baba940bd1aa75173b/latest/USD {currency}"
            )
            response.raise_for_status()
            rates[currency] = response.json().get("rates", {})
            logging.info(f"Успешно получены курсы для {currency}: {rates[currency]}")
        except requests.RequestException as e:
            logging.error(f"Ошибка при получении курса для {currency}: {e}")
            rates[currency] = {}
    return rates


def get_stock_prices(stocks):
    """Получает цены акций."""
    prices = {}
    for stock in stocks:
        logging.debug(f"Запрос цены для акции: {stock}")
        try:
            response = requests.get(
                f"https://api.marketstack.com/v1/eod?access_key=df3caee3a4eb8c55e2af01775ca399c8&symbols=AAPL {stock}"
            )
            response.raise_for_status()  # Проверка на ошибки HTTP
            prices[stock] = response.json().get("price", None)
            logging.info(f"Успешно получена цена для {stock}: {prices[stock]}")
        except requests.RequestException as e:
            logging.error(f"Ошибка при получении цены для {stock}: {e}")
            prices[stock] = None
    return prices


def group_expenses(filtered_data):
    """Группирует расходы по категориям и возвращает основные категории."""
    logging.debug("Начало группировки расходов")
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

    logging.info("Группировка расходов завершена")
    return combined_expenses


def group_income(filtered_data):
    """Группирует поступления по категориям и возвращает основные категории."""
    logging.debug("Начало группировки поступлений")
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

    logging.info("Группировка поступлений завершена")
    return combined_income