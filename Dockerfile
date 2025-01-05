FROM python:3.11-slim

WORKDIR /app

# Устанавливаем зависимости и модель spaCy
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN python -m spacy download en_core_web_md

# Копируем код приложения
COPY . .

CMD ["python", "-m", "validator_service.consumer"] 