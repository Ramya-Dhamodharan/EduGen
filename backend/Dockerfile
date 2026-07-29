FROM python:3.12-slim

# Install uv

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Copy dependency files first

COPY pyproject.toml uv.lock ./

# Install dependencies

RUN uv sync --frozen --no-dev

# Copy project

COPY . .

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
