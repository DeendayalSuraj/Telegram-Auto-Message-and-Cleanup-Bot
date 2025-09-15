FROM python:3.9-slim

WORKDIR /app

# Install system dependencies first (less likely to change)
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Run as non-root user for security
RUN useradd -m -u 1000 botuser
USER botuser

CMD ["python", "bot.py"]
