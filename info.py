import requests
from bs4 import BeautifulSoup
import csv
import logging

# Настройки логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

BASE_URL = "https://ria.ru/search/"

# Список компаний и их файлов
COMPANIES = [
    {"name": "Газпром", "ticker": "GAZP", "news_file": "gazprom_news.csv", "details_file": "gazprom_news_details.csv", "stock_file": "gazprom_stock_prices.csv"},
]

# Функция для получения новостей по запросу с учетом пагинации
def fetch_news(query, page=1):
    try:
        params = {"query": query, "page": page}
        response = requests.get(BASE_URL, params=params)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        logging.error(f"Ошибка загрузки новостей: {e}")
        raise

# Функция для парсинга новостей с сайта РИА Новости
def parse_news(html):
    soup = BeautifulSoup(html, 'html.parser')
    news_items = []

    # Поиск всех блоков с новостями
    articles = soup.find_all('div', class_='list-item')
    for article in articles:
        title_tag = article.find('a', class_='list-item__title')
        if not title_tag:
            continue

        # Извлечение информации
        title = title_tag.text.strip()
        link = title_tag['href'].strip()
        date_tag = article.find('div', class_='list-item__date')
        date_str = date_tag.text.strip() if date_tag else "Unknown Date"

        # Добавляем новость в список
        news_items.append((title, link, date_str))

    return news_items

# Функция для сохранения новостей в CSV файл
def save_to_csv(news_items, filename):
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["Новость", "Ссылка", "Дата"])
            writer.writerows(news_items)
    except Exception as e:
        logging.error(f"Ошибка сохранения новостей в файл {filename}: {e}")
        raise

# Функция для получения содержимого новости по ссылке
def fetch_news_content(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Поиск основного текста статьи
        content_blocks = soup.find_all('div', class_='article__text')
        if content_blocks:
            full_content = "\n\n".join(block.text.strip() for block in content_blocks)
            return full_content
        return "Содержимое новости не найдено."
    except Exception as e:
        logging.warning(f"Ошибка при загрузке новости {url}: {e}")
        return f"Ошибка при загрузке новости: {e}"

# Функция для сохранения подробных данных новостей в CSV файл
def save_news_details(news_details, file_path):
    try:
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['News', 'Link', 'Date', 'News_text'])
            writer.writerows(news_details)
    except Exception as e:
        logging.error(f"Ошибка сохранения деталей новостей в файл {file_path}: {e}")
        raise

# Функция для обработки компании (сбор новостей, цен акций и их сохранение)
def process_company(company, max_news=60):
    logging.info(f"Начинаем обработку новостей и акций для {company['name']}...")

    all_news = []
    page = 1

    # Собираем новости, пока не соберем 60 новостей
    while len(all_news) < max_news:
        try:
            html = fetch_news(company['name'], page)
            news = parse_news(html)
            if news:
                all_news.extend(news)
                logging.info(f"Собрано {len(all_news)} новостей.")
            else:
                logging.info(f"Новости для {company['name']} не найдены на странице {page}.")
                break
        except Exception as e:
            logging.error(f"Ошибка загрузки новостей для {company['name']} на странице {page}: {e}")
            break

        page += 1

    # Ограничиваем сбор новостей до max_news
    all_news = all_news[:max_news]
    if all_news:
        save_to_csv(all_news, company['news_file'])
    else:
        logging.info(f"Новости для {company['name']} не найдены.")

    # Сохранение подробной информации по каждой новости
    try:
        news_links = [(row[0], row[1], row[2]) for row in csv.reader(open(company['news_file'], encoding='utf-8'))][1:]
        news_details = [(title, link, date, fetch_news_content(link)) for title, link, date in news_links]
        save_news_details(news_details, company['details_file'])
    except Exception as e:
        logging.error(f"Ошибка обработки ссылок для {company['name']}: {e}")

# Главная функция для обработки всех компаний
def main():
    for company in COMPANIES:
        process_company(company)

if __name__ == "__main__":
    main()
