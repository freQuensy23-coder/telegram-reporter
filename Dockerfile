FROM python3.12-slim

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml .
COPY *.py .
COPY tests/ tests/

# Install dependencies
RUN pip install --no-cache-dir .

# Create volume for persistent data
VOLUME /app/data

# Set environment variables
ENV TELEGRAM_BOT_TOKEN=""
ENV PYTHONUNBUFFERED=1

# Run the bot
CMD ["python", "main.py"]
