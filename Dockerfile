# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем код внутрь контейнера
COPY . .

RUN pip install -r requirements.txt

# Устанавливаем команду по умолчанию
CMD ["python", "app.py"]
