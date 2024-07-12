# Используем официальный образ Python
FROM python:3.11-slim

# Установим зависимости для работы с Postgres
RUN apt-get update && apt-get install -y libpq-dev gcc

# Устанавливаем зависимости для Python
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Копируем код приложения
COPY . .

# Указываем порт, который будет использовать приложение
EXPOSE 5001

# Команда для запуска приложения
CMD ["python", "server.py"]
