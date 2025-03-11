import json
import logging
import pandas as pd
from config import OPERATIONS_PATH, USER_SETTINGS_PATH
from src.utils import get_currency_rates, get_data_range, get_stock_prices, group_expenses, group_income

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


def load_transactions(file_path: str) -> pd.DataFrame:
    """
    Загружает данные о транзакциях из Excel-файла.

    :param file_path: Путь к файлу с транзакциями
    :return: DataFrame с транзакциями
    """
    try:
        data = pd.read_excel(file_path)
        logger.info("Данные успешно загружены из файла: %s", file_path)
        return data
    except FileNotFoundError:
        logger.error("Файл не найден: %s", file_path)
        raise
    except pd.errors.EmptyDataError:
        logger.error("Файл пуст: %s", file_path)
        raise
    except Exception as e:
        logger.error("Ошибка при чтении файла %s: %s", file_path, e)
        raise


def filter_transactions_by_date(data: pd.DataFrame, start_date, end_date) -> pd.DataFrame:
    """
    Фильтрует транзакции по указанному диапазону дат.

    :param data: DataFrame с транзакциями
    :param start_date: Начальная дата
    :param end_date: Конечная дата
    :return: Отфильтрованный DataFrame
    """
    try:
        data["Дата операции"] = pd.to_datetime(data["Дата операции"], format='mixed', errors='coerce')
        if data["Дата операции"].isnull().any():
            logger.warning("Некоторые значения в колонке 'Дата операции' не удалось преобразовать")
        filtered_data = data.dropna(subset=["Дата операции"])
        logger.debug("Колонка 'Дата операции' успешно преобразована")
        return filtered_data
    except Exception as e:
        logger.error("Ошибка при фильтрации данных по дате: %s", e)
        raise


def load_user_settings(file_path: str) -> dict:
    """
    Загружает настройки пользователя из JSON-файла.

    :param file_path: Путь к файлу с настройками
    :return: Словарь с настройками пользователя
    """
    try:
        with open(file_path) as f:
            settings = json.load(f)
        logger.debug("Настройки пользователя успешно загружены")
        return settings
    except (FileNotFoundError, json.JSONDecodeError) as e:
        logger.error("Ошибка при чтении файла настроек %s: %s", file_path, e)
        raise


def analyze_data(date_str: str, data_range: str = "M") -> dict:
    """
    Главная функция для анализа данных.

    :param date_str: Строка даты в формате 'DD.MM.YYYY' или 'DD.MM.YYYY HH:MM:SS'
    :param data_range: Период ('M' - месяц, 'W' - неделя, 'Y' - год, 'ALL' - весь период)
    :return: Словарь с результатами анализа
    """
    logger.info("Начало анализа данных")

    try:
        # Получение диапазона дат
        start_date, end_date = get_data_range(date_str, data_range)
        logger.debug("Диапазон дат: %s - %s", start_date, end_date)

        # Загрузка данных о транзакциях
        transactions = load_transactions(OPERATIONS_PATH)

        # Фильтрация данных по дате
        filtered_data = filter_transactions_by_date(transactions, start_date, end_date)
        if filtered_data.empty:
            logger.warning("Нет данных за указанный период")
            return {}

        # Анализ расходов
        expenses_summary = group_expenses(filtered_data)
        total_expenses = filtered_data[filtered_data["Сумма операции"] < 0]["Сумма операции"].sum()
        logger.info("Общая сумма расходов: %s", total_expenses)

        # Анализ поступлений
        income_summary = group_income(filtered_data)
        total_income = filtered_data[filtered_data["Сумма операции"] > 0]["Сумма операции"].sum()
        logger.info("Общая сумма поступлений: %s", total_income)

        # Загрузка настроек пользователя
        user_settings = load_user_settings(USER_SETTINGS_PATH)

        # Проверка наличия ключей в настройках
        if "user_currencies" not in user_settings or "user_stocks" not in user_settings:
            logger.error("В настройках пользователя отсутствуют необходимые ключи")
            raise KeyError("Отсутствуют ключи 'user_currencies' или 'user_stocks' в настройках")

        # Получение валютных курсов и цен акций
        currency_rates = get_currency_rates(user_settings["user_currencies"])
        stock_prices = get_stock_prices(user_settings["user_stocks"])
        logger.info("Курсы валют и цены акций успешно получены")

        # Формирование итогового ответа
        result = {
            "Расходы": {"Общая сумма": total_expenses, "Основные": expenses_summary.to_dict(orient="records")},
            "Поступления": {"Общая сумма": total_income, "Основные": income_summary.to_dict(orient="records")},
            "Курс валют": currency_rates,
            "Цены акций": stock_prices,
        }

        logger.info("Анализ данных завершен")
        return result

    except Exception as e:
        logger.error("Ошибка при выполнении анализа данных: %s", e)
        raise
