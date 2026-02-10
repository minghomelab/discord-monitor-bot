# -------------------------------
# Dockerfile for Discord Monitor Bot
# -------------------------------

# Use official Python 3.12 slim image (small and modern)
FROM python:3.12-slim

# Set working directory inside container
WORKDIR /app

# Copy requirements first for caching
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the bot code
COPY src/ ./src
COPY data/ ./data

# Set environment variables from Docker (will be provided via docker-compose)
ENV PYTHONUNBUFFERED=1

# Entry point: run the main bot script
CMD ["python3", "src/main.py"]
