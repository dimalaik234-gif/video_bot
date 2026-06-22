# Образ с ffmpeg «из коробки» — нужен для склейки video+audio и конвертации MP3.
# bothost.ru умеет собирать проект по Dockerfile (см. README).
FROM python:3.12-slim

# ffmpeg + базовые утилиты
RUN apt-get update \
    && apt-get install -y --no-install-recommends ffmpeg ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Бот работает через long polling, порт не нужен
CMD ["python", "main.py"]
