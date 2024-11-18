import requests
from bs4 import BeautifulSoup
import csv
import datetime
import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://ria.ru/search/"
QUERY = "Газпром"
NEWS_CSV_FILE = "gazprom_news.csv"
DETAILS_FILE = "gazprom_news_details.csv"
TICKER = "GAZP"
STOCK_CSV_FILE = "gazprom_stock_prices.csv"

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

def read_links_from_csv(file_path):
    if not os.path.exists(file_path):
        logging.error(f"Файл {file_path} не найден.")
        raise FileNotFoundError(f"Файл {file_path} не найден.")

    links = []
    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                links.append((row['Новость'], row['Ссылка'], row['Дата']))
        return links
    except Exception as e:
        logging.error(f"Ошибка чтения файла {file_path}: {e}")
        raise

def save_news_details(news_details, file_path):
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['Новость', 'Ссылка', 'Дата', 'Содержимое'])
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

def main():
    logging.info("Начинаем загрузку новостей про Газпром...")

    try:
        html = fetch_news(QUERY)
        news = parse_news(html)
        if news:
            logging.info(f"Найдено {len(news)} новостей. Сохраняем в CSV...")
            save_to_csv(news, NEWS_CSV_FILE)
        else:
            logging.info("Новости не найдены.")
    except Exception as e:
        logging.error(f"Ошибка при загрузке новостей: {e}")

    logging.info("Получаем текущую цену акций Газпрома...")
    price = get_moex_price(TICKER)
    if price is not None:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        log_price_to_csv(STOCK_CSV_FILE, TICKER, price, timestamp)
        logging.info(f"Цена акции {TICKER}: {price}, записано в файл {STOCK_CSV_FILE}")
    else:
        logging.warning(f"Не удалось получить цену акции {TICKER}.")

    logging.info("Чтение ссылок из файла новостей...")
    try:
        news_links = read_links_from_csv(NEWS_CSV_FILE)
        if not news_links:
            logging.info("Ссылки на новости отсутствуют.")
            return

        news_details = []
        logging.info(f"Обнаружено {len(news_links)} ссылок. Начинаем извлечение содержимого...")

        for i, (title, link, date) in enumerate(news_links, start=1):
            logging.info(f"[{i}/{len(news_links)}] Загружаем новость: {title}")
            content = fetch_news_content(link)
            news_details.append((title, link, date, content))

        logging.info("Сохранение содержимого новостей в файл...")
        save_news_details(news_details, DETAILS_FILE)
    except Exception as e:
        logging.error(f"Произошла ошибка при обработке новостей: {e}")

if __name__ == "__main__":
    main()
