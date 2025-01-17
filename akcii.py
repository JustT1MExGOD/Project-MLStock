import requests
import csv
from datetime import datetime

# Функция для получения данных о ценах акций Газпрома с API Московской биржи
def get_gazprom_stock_data():
    url = "https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/GAZP/candles.json"
    params = {
        'interval': 24,          # Интервал в 24 часа (дневные данные)
        'from': '2019-01-01',    # Начальная дата
    }
    stock_data = []

    # Отправляем запрос к API
    response = requests.get(url, params=params)
    
    # Проверим, что мы получаем от сервера
    try:
        data = response.json()
    except ValueError:
        print("Ошибка при преобразовании ответа в JSON")
        print(response.text)  # Выводим текст ответа
        return stock_data

    # Выводим весь ответ для отладки
    print("Ответ от сервера:", data)

    # Проверяем, есть ли данные в ответе
    if 'candles' not in data or 'data' not in data['candles']:
        print("Данные не найдены или структура ответа изменена.")
        return stock_data

    # Извлекаем данные о свечах (ценах)
    candles = data['candles']['data']

    # Проходим по каждому элементу в "candles"
    for candle in candles:
        open_price = candle[0]  # Открытие
        close_price = candle[1]  # Закрытие
        high_price = candle[2]  # Максимальная цена
        low_price = candle[3]   # Минимальная цена
        volume = candle[5]      # Объем
        date_str = candle[6]    # Дата начала свечи

        # Преобразуем строку с датой в нужный формат
        date_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S').strftime('%Y-%m-%d')

        # Добавляем данные в список
        stock_data.append([date_obj, open_price, high_price, low_price, close_price, volume])

    return stock_data

# Записываем данные о ценах акций в CSV файл
def write_stock_data_to_csv(stock_data):
    with open('gazprom_stock_prices_2019.csv', 'w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Date', 'Open', 'High', 'Low', 'Close', 'Volume'])
        writer.writerows(stock_data)

# Главная программа
if __name__ == "__main__":
    print("Сбор данных о ценах акций Газпрома с 01.01.2019...")
    stock_data = get_gazprom_stock_data()

    if stock_data:
        print(f"Собрано {len(stock_data)} записей о ценах акций.")
    else:
        print("Не удалось собрать данные о ценах акций.")

    print("Запись данных о ценах акций в CSV файл...")
    write_stock_data_to_csv(stock_data)

    print("Данные успешно собраны и записаны в файл.")
