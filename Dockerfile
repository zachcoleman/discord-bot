
FROM python:3.9.12-slim

RUN apt-get update

WORKDIR /app

COPY bot/ /app/bot
COPY pyproject.toml /app/pyproject.toml
COPY setup.py /app/setup.py
COPY .env /app/.env

RUN mkdir /data

RUN pip install -e .

CMD ["python", "bot/bot.py"]