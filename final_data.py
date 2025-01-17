import pandas as pd

# Загрузка данных
df1 = pd.read_csv('final_data_gazprom.csv')  # Первый датасет с новостями
df2 = pd.read_csv('gazprom_stock_prices_final.csv')  # Второй датасет с финансовыми данными

# Преобразуем столбцы с датами в формат datetime
df1['pubdate'] = pd.to_datetime(df1['pubdate'])
df2['Date'] = pd.to_datetime(df2['Date'])

# Преобразуем pubdate в формат даты (без времени) в первом датасете
df1['pubdate_date'] = df1['pubdate'].dt.date

# Объединяем датасеты по дате (при этом для df2 дата будет без времени)
merged_df = pd.merge(df1, df2, left_on='pubdate_date', right_on='Date', how='left')

# Заполнение пропусков предыдущими значениями (forward fill)
merged_df.fillna(method='ffill', inplace=True)

# Результат
print(merged_df.head())
