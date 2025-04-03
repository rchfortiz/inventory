FROM python:3.13-alpine
WORKDIR /app
RUN pip install uv
COPY pyproject.toml .
RUN uv sync
COPY . .
ENV INV_PORT 8000
EXPOSE ${INV_PORT}
CMD [ "sh", "-c", "uv run fastapi run inventory --port ${INV_PORT}" ]
