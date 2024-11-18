# Трекер новостей и цен акций Газпрома

Скрипт собирает и обрабатывает новости о "Газпроме" с сайта РИА Новости, извлекает подробную информацию о новостях и получает текущие цены акций Газпрома с MOEX API. Все данные сохраняются в CSV-файлы для дальнейшего анализа.

## Возможности

1. **Сбор и обработка новостей**
   - Получение новостей, соответствующих запросу (`Газпром`).
   - Извлечение заголовков, ссылок и дат публикации статей.
   - Сохранение данных в CSV-файл.

2. **Извлечение содержимого новостей**
   - Переход по ссылкам и загрузка полного содержимого статей.
   - Сохранение подробной информации в отдельный CSV-файл.

3. **Получение цен акций**
   - Получение текущей цены акций Газпрома через MOEX API.
   - Запись цен акций с отметками времени в CSV-файл.

## Установка

1. Клонируйте репозиторий или скопируйте скрипт в рабочую директорию:
   ```bash
   git clone https://github.com/your-repo/Project-MLStock.git
   ```
2. Установите необходимые зависимости:
   ```bash
   pip install requests beautifulsoup4
   ```
### Использование
Запустите скрипт с помощью Python:
   ```bash
   python parser.py
   ```
   Скрипт выполняет следующие действия:

1. Получает новости с сайта РИА Новости.
2. Извлекает актуальную цену акций Газпрома с MOEX API.
3. Сохраняет данные в CSV-файлы:
   - gazprom_news.csv: Краткая информация о новостях (заголовки, ссылки и даты).
   - gazprom_news_details.csv: Детализированное содержимое каждой статьи.
   - gazprom_stock_prices.csv: Запись цен акций с временными метками.
     
### Настройки

**Константы:**
- BASE_URL: Базовый URL для загрузки новостей с РИА Новости.
- QUERY: Поисковый запрос для статей (по умолчанию Газпром).
- NEWS_CSV_FILE: Путь для сохранения краткой информации о новостях.
- DETAILS_FILE: Путь для сохранения детализированного содержимого статей.
- TICKER: Тикер для получения данных о ценах акций (по умолчанию GAZP).
- STOCK_CSV_FILE: Путь для сохранения данных о ценах акций.

Вы можете изменить эти константы в начале скрипта.

### Форматы CSV-файлов

gazprom_news.csv:
- Колонки: Новость, Ссылка, Дата.

gazprom_news_details.csv:
-Колонки: Новость, Ссылка, Дата, Содержимое.

gazprom_stock_prices.csv:
- Колонки: Ticker, Price, Timestamp.
  
### Логирование

Скрипт использует модуль logging для ведения подробных логов. В логах содержится информация о:

- Прогрессе загрузки и обработки новостей.
- Процессе получения цен акций.
- Ошибках, возникших во время выполнения.

### Ограничения

- Скрипт зависит от структуры сайта РИА Новости. Если структура изменится, потребуется обновление кода.
- Ограничения на запросы к MOEX API и его доступность могут повлиять на получение цен акций.
