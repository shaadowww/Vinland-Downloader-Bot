FROM python:3.13-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    ffmpeg \ 
    && rm -rf /var/lib/apt/lists/*

RUN pip install poetry 

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-root 

COPY . .

CMD ["python", "app.py"]