FROM python:3.11.10-slim-bullseye

RUN pip install poetry

WORKDIR /app

COPY . /app

RUN poetry install --only main

ENTRYPOINT poetry run alembic upgrade head && poetry run fastapi run app/main.py
