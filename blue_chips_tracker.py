import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://ria.ru/search/"

# Список компаний и их данных
COMPANIES = [
    {"name": "Сбербанк", "ticker": "SBER", "news_file": "sberbank_news.csv", "details_file": "sberbank_news_details.csv", "stock_file": "sberbank_stock_prices.csv"},
    {"name": "Лукойл", "ticker": "LKOH", "news_file": "lukoil_news.csv", "details_file": "lukoil_news_details.csv", "stock_file": "lukoil_stock_prices.csv"},
    {"name": "Яндекс", "ticker": "YNDX", "news_file": "yandex_news.csv", "details_file": "yandex_news_details.csv", "stock_file": "yandex_stock_prices.csv"},
    {"name": "Роснефть", "ticker": "ROSN", "news_file": "rosneft_news.csv", "details_file": "rosneft_news_details.csv", "stock_file": "rosneft_stock_prices.csv"},
    {"name": "ВТБ", "ticker": "VTBR", "news_file": "vtb_news.csv", "details_file": "vtb_news_details.csv", "stock_file": "vtb_stock_prices.csv"},
    {"name": "Татнефть", "ticker": "TATN", "news_file": "tatneft_news.csv", "details_file": "tatneft_news_details.csv", "stock_file": "tatneft_stock_prices.csv"},
    {"name": "Газпром", "ticker": "GAZP", "news_file": "gazprom_news.csv", "details_file": "gazprom_news_details.csv", "stock_file": "gazprom_stock_prices.csv"},
]

def fetch_news(query, page=1):
    try:
        params = {"query": query, "page": page}
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Ошибка загрузки новостей: {e}")
        raise

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
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Новость", "Ссылка", "Дата"])
            writer.writerows(news_items)
    except Exception as e:
        logging.error(f"Ошибка сохранения новостей в файл {filename}: {e}")
        raise

def fetch_news_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        content_blocks = soup.find_all('div', class_='article__text')
        if content_blocks:
            full_content = "\n\n".join(block.text.strip() for block in content_blocks)
            return full_content
        return "Содержимое новости не найдено."
    except Exception as e:
        logging.warning(f"Ошибка при загрузке новости {url}: {e}")
        return f"Ошибка при загрузке новости: {e}"

def save_news_details(news_details, file_path):
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['News', 'Link', 'Date', 'News_text'])
            writer.writerows(news_details)
    except Exception as e:
        logging.error(f"Ошибка сохранения деталей новостей в файл {file_path}: {e}")
        raise

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
        return None
    except requests.RequestException as e:
        logging.error(f"Ошибка при запросе данных с MOEX API: {e}")
        return None

def log_price_to_csv(file_path, ticker, price, timestamp):
    file_exists = os.path.exists(file_path)
    try:
        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(['Ticker', 'Price', 'Timestamp'])
            writer.writerow([ticker, price, timestamp])
    except Exception as e:
        logging.error(f"Ошибка записи цены акции в файл {file_path}: {e}")

def process_company(company):
    logging.info(f"Начинаем обработку новостей и акций для {company['name']}...")

    try:
        html = fetch_news(company['name'])
        news = parse_news(html)
        if news:
            save_to_csv(news, company['news_file'])
        else:
            logging.info(f"Новости для {company['name']} не найдены.")
    except Exception as e:
        logging.error(f"Ошибка загрузки новостей для {company['name']}: {e}")

    price = get_moex_price(company['ticker'])
    if price is not None:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_price_to_csv(company['stock_file'], company['ticker'], price, timestamp)

    try:
        news_links = [(row[0], row[1], row[2]) for row in csv.reader(open(company['news_file'], encoding='utf-8'))][1:]
        news_details = [(title, link, date, fetch_news_content(link)) for title, link, date in news_links]
        save_news_details(news_details, company['details_file'])
    except Exception as e:
        logging.error(f"Ошибка обработки ссылок для {company['name']}: {e}")

def main():
    for company in COMPANIES:
        process_company(company)

if __name__ == "__main__":
    main()