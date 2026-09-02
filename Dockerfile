FROM python:3.14-slim
# installs uv executable
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . /app

WORKDIR /app
# install dependencies
RUN uv sync --frozen --no-cache

CMD ["uv", "run", "main.py"]