import json
import logging
import pandas as pd
from config import file_path
from src.reports import spending_by_category
from src.services import get_beneficial_cashback_categories
from src.views import analyze_data

# Вызов функции "Функция «Выгодные категории повышенного кешбэка»

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    transactions = [
        {"date": "2023-10-01", "amount": -1500, "category": "Еда"},
        {"date": "2023-10-05", "amount": -2000, "category": "Транспорт"},
        {"date": "2023-10-10", "amount": -3000, "category": "Наличные"},
        {"date": "2023-10-12", "amount": -1000, "category": "Развлечения"},
        {"date": "2023-09-15", "amount": -500, "category": "Еда"},
    ]

    result = get_beneficial_cashback_categories(transactions, 2023, 10)
    print(result)

# Вызов функции
data = {
    "Дата операции": pd.to_datetime(["2021-12-31 16:44:00", "2021-12-31 16:42:04", "2021-12-31 16:39:04"]),
    "Сумма операции": [-160.89, -64.00, -118.12],
    "Категория": ["Супермаркеты", "Переводы", "Каршеринг"],
}
transactions_df = pd.DataFrame(data)
transactions_df.to_excel(file_path, index=False)

result = spending_by_category(transactions_df, "Переводы")
print(result)

# Вызов функции анализа данных к веб-странице События
result = analyze_data(date_str="31.12.2021 16:44:00", data_range="M")
print(json.dumps(result, ensure_ascii=False, indent=4))