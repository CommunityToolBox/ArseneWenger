FROM python:3.14-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY . ./
RUN uv sync

CMD ["uv", "run",  "arsene_wenger/bot.py"]
