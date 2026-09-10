# Boilerplate -- not part of any exercise. Kept deliberately minimal
# (python:3.12-slim, not full python:3.12) since most container CVEs come
# from OS packages you never use but that shipped anyway.
FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.8.3 \
    && poetry config virtualenvs.create false

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --only main --no-root

COPY . .

EXPOSE 8080
CMD ["gunicorn", "-b", "0.0.0.0:8080", "app.main:app"]
