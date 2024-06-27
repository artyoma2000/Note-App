# Используем официальный образ Python
FROM python:3.9-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы requirements.txt и устанавливаем зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы приложения
COPY . .

# Устанавливаем переменные окружения для Flask
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Открываем порт 5000 для Flask
EXPOSE 5000

# Команда для запуска приложения
CMD ["flask", "run", "--host=0.0.0.0"]
