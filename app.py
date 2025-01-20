import numpy as np
import torch
from transformers import BertTokenizer, BertModel
from sklearn.preprocessing import StandardScaler
from flask import Flask, request, jsonify
import xgboost as xgb

# Загрузка модели XGBoost с использованием Booster
model = xgb.Booster()
model.load_model('./xgb_model_2.json')  # Загружаем модель XGBoost

# Загрузка трансформера для обработки текста
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
bert_model = BertModel.from_pretrained('bert-base-uncased').to(device)

# Функция для извлечения эмбеддингов из BERT
def get_bert_embeddings(texts, batch_size=16):
    inputs = tokenizer(texts, return_tensors='pt', padding=True, truncation=True, max_length=512)
    input_ids = inputs['input_ids'].to(device)
    attention_mask = inputs['attention_mask'].to(device)
 
    with torch.no_grad():
        outputs = bert_model(input_ids, attention_mask=attention_mask)
        embeddings = outputs.last_hidden_state.mean(dim=1)  # Используем среднее значение всех токенов

    return embeddings.cpu().numpy()

# Инициализация Flask приложения
app = Flask(__name__)

from xgboost import DMatrix

@app.route('/predict', methods=['POST'])
def predict():
    # Получаем данные из POST-запроса
    data = request.get_json()

    tokenized_news = data['tokenized_news']
    open_price = data['Open']
    high_price = data['High']
    low_price = data['Low']
    volume = data['Volume']
    
    # Преобразование текста в эмбеддинги с помощью BERT
    text_embeddings = get_bert_embeddings([tokenized_news])

    # Преобразование числовых признаков
    numeric_features = np.array([[open_price, high_price, low_price, volume]])

    # Масштабирование числовых признаков
    scaler = StandardScaler()
    numeric_features_scaled = scaler.fit_transform(numeric_features)

    # Объединение эмбеддингов и числовых признаков
    features = np.concatenate((text_embeddings, numeric_features_scaled), axis=1)

    # Преобразование в DMatrix
    dmatrix_features = DMatrix(features)

    # Прогнозирование
    prediction = model.predict(dmatrix_features)

    # Преобразование результата в тип float перед отправкой
    return jsonify({'predicted_close_price': float(prediction[0])})


if __name__ == '__main__':
    app.run(debug=True)
