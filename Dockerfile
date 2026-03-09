FROM python:3.10-slim

ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN pip install --no-cache-dir python-telegram-bot aiohttp

COPY github_telegram_bot.py .

ENTRYPOINT ["python", "github_telegram_bot.py"]
