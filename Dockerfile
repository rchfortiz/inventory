FROM python:3.13-alpine
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv sync
COPY . .
CMD ["sh", "-c", "uv run fastapi run inventory"]
