FROM python:3.12

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .

RUN pip install uv
RUN uv sync

COPY *.py .
COPY tests/ tests/

# Create volume for persistent data
VOLUME /app/data

# Set environment variables
ENV TELEGRAM_BOT_TOKEN=""
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["uv", "run", "main.py"]