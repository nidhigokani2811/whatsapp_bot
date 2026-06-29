FROM python:3.12-slim

# Prevent Python from writing .pyc files and enable stdout/stderr buffering
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy and install python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and files
COPY app /app/app
COPY migrations /app/migrations
COPY alembic.ini /app/
COPY entrypoint.sh /app/

# Make the entrypoint executable
RUN chmod +x /app/entrypoint.sh

# Expose FastAPI server port
EXPOSE 8000

# Set entrypoint script
ENTRYPOINT ["/app/entrypoint.sh"]
