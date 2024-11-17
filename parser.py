import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os

BASE_URL = "https://ria.ru/search/"
QUERY = "Газпром"
NEWS_CSV_FILE = "gazprom_news.csv"
DETAILS_FILE = "gazprom_news_details.csv"

TICKER = "GAZP"
STOCK_CSV_FILE = "gazprom_stock_prices.csv"

def fetch_news(query, page=1):
    params = {"query": query, "page": page}
    response = requests.get(BASE_URL, params=params)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch page: {response.status_code}")
    return response.text

def parse_news(html):
    soup = BeautifulSoup(html, 'html.parser')
    news_items = []

    articles = soup.find_all('div', class_='list-item')
    for article in articles:
        title_tag = article.find('a', class_='list-item__title')
        if not title_tag:
            continue

        title = title_tag.text.strip()
        link = title_tag['href'].strip()
        date_tag = article.find('div', class_='list-item__date')
        date = date_tag.text.strip() if date_tag else "Unknown Date"

        news_items.append((title, link, date))

    return news_items

def save_to_csv(news_items, filename):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["Новость", "Ссылка", "Дата"])
        writer.writerows(news_items)

def get_moex_price(ticker):
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities/{ticker}.json"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        market_data = data['marketdata']['data']
        if market_data:
            last_price = next((item[12] for item in market_data if item[12] is not None), None)
            return last_price
        else:
            return None
    except Exception as e:
        print(f"Ошибка при запросе данных с MOEX API: {e}")
        return None

def log_price_to_csv(file_path, ticker, price, timestamp):
    file_exists = False
    try:
        with open(file_path, 'r'):
            file_exists = True
    except FileNotFoundError:
        pass

    with open(file_path, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        if not file_exists:
            writer.writerow(['Ticker', 'Price', 'Timestamp'])
        writer.writerow([ticker, price, timestamp])

def fetch_news_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        content = soup.find('div', class_='article__text') 
        if content:
            return content.text.strip()
        else:
            return "Содержимое новости не найдено."
    except Exception as e:
        return f"Ошибка при загрузке новости: {e}"

def read_links_from_csv(file_path):
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    links = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            links.append((row['Новость'], row['Ссылка'], row['Дата']))
    return links

def save_news_details(news_details, file_path):
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Новость', 'Ссылка', 'Дата', 'Содержимое'])
        writer.writerows(news_details)

def main():
    print("Скачиваем новости про Газпром...")
    try:
        html = fetch_news(QUERY)
        news = parse_news(html)
        if news:
            print(f"Найдено {len(news)} новостей. Сохраняем в CSV...")
            save_to_csv(news, NEWS_CSV_FILE)
            print(f"Новости сохранены в {NEWS_CSV_FILE}")
        else:
            print("Новости не найдены.")
    except Exception as e:
        print(f"Ошибка при загрузке новостей: {e}")

    print("\nПолучаем текущую цену акций Газпрома...")
    price = get_moex_price(TICKER)
    if price is not None:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_price_to_csv(STOCK_CSV_FILE, TICKER, price, timestamp)
        print(f"Цена акции {TICKER}: {price}, записано в файл {STOCK_CSV_FILE}")
    else:
        print(f"Не удалось получить цену акции {TICKER}.")

    print("\nЧтение ссылок из файла новостей...")
    try:
        news_links = read_links_from_csv(NEWS_CSV_FILE)
        if not news_links:
            print("Ссылки на новости отсутствуют.")
            return

        news_details = []
        print(f"Обнаружено {len(news_links)} ссылок. Начинаем извлечение содержимого...")

        for i, (title, link, date) in enumerate(news_links, start=1):
            print(f"[{i}/{len(news_links)}] Загружаем новость: {title}")
            content = fetch_news_content(link)
            news_details.append((title, link, date, content))

        print("Сохранение содержимого новостей в файл...")
        save_news_details(news_details, DETAILS_FILE)
        print(f"Детали новостей сохранены в {DETAILS_FILE}.")
    except Exception as e:
        print(f"Произошла ошибка при обработке новостей: {e}")

if __name__ == "__main__":
    main()