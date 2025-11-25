FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.0

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

COPY app ./app
COPY celeryconfig.py ./

ENV PYTHONUNBUFFERED=1

EXPOSE 8002

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8002"]
