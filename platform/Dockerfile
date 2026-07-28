FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y \
  default-libmysqlclient-dev \
  gcc \
  pkg-config \
  && rm -rf /var/lib/apt/lists/*

RUN pip install poetry==1.8.5

RUN poetry config virtualenvs.create false

# --- Production stage ---
FROM base AS prod
WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --only main --no-interaction --no-ansi && \
    apt-get purge -y gcc pkg-config && \
    rm -rf /var/lib/apt/lists/*

COPY reworkd_platform/ ./reworkd_platform/

CMD ["python", "-m", "reworkd_platform"]

# --- Development stage ---
FROM base AS dev
WORKDIR /app

COPY pyproject.toml poetry.lock* ./
RUN poetry install --no-interaction --no-ansi

COPY . .

CMD ["python", "-m", "reworkd_platform"]
