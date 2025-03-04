import json

import pandas as pd
from config import file_path, file_path1

from src.utils import get_currency_rates, get_data_range, get_stock_prices, group_expenses, group_income


def analyze_data(date_str, data_range="M"):
    """Главная функция для анализа данных."""
    start_date, end_date = get_data_range(date_str, data_range)
    filtered_data = pd.read_excel(file_path)
    filtered_data["Дата операции"] = filtered_data["Дата операции"].astype(str).str.strip()

    try:
        # Преобразуем 'Дата операции' в формат даты и времени
        filtered_data["Дата операции"] = pd.to_datetime(filtered_data["Дата операции"], format="%d.%m.%Y %H:%M:%S")
    except Exception as e:
        print(f"Ошибка при преобразовании дат: {e}")

    # Фильтруем данные по дате
    filtered_data = filtered_data[
        (filtered_data["Дата операции"] >= start_date) & (filtered_data["Дата операции"] <= end_date)
    ]
    # Анализ расходов
    expenses_summary = group_expenses(filtered_data)
    total_expenses = filtered_data["Сумма операции"].sum()
    # Анализ поступлений
    income_summary = group_income(filtered_data)
    total_income = filtered_data["Сумма операции"][filtered_data["Сумма операции"] > 0].sum()
    # Получение валютных курсов и цен акций
    try:
        with open(file_path1) as f:
            user_settings = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        raise ValueError(f"Ошибка при чтении файла настроек пользователя: {e}")

    currency_rates = get_currency_rates(user_settings["user_currencies"])
    stock_prices = get_stock_prices(user_settings["user_stocks"])
    # Формирование итогового ответа
    result = {
        "Расходы": {"Общая сумма": total_expenses, "Основные": expenses_summary.to_dict(orient="records")},
        "Поступления": {"Общая сумма": total_income, "Основные": income_summary.to_dict(orient="records")},
        "Курс валют": currency_rates,
        "Цены акций": stock_prices,
    }
    return result
