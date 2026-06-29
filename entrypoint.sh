#!/bin/sh
set -e

echo "Waiting for PostgreSQL database to be online..."
python -c "
import socket
import time
import urllib.parse
import os

db_url = os.environ.get('DATABASE_URL', '')
if db_url.startswith('postgresql+asyncpg://'):
    db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')

parsed = urllib.parse.urlparse(db_url)
host = parsed.hostname or 'db'
port = parsed.port or 5432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
for i in range(20):
    try:
        s.connect((host, port))
        print('PostgreSQL is up and listening!')
        break
    except socket.error:
        print(f'Postgres is unavailable on {host}:{port} - waiting...')
        time.sleep(2)
"

# Run migrations only in the web container startup (or if we run migrations check first)
# To avoid concurrency when scaling containers, we check if we are executing the default command
if [ "$#" -eq 0 ] || [ "$1" = "uvicorn" ]; then
    echo "Executing Alembic database migrations..."
    alembic upgrade head
fi

if [ "$#" -gt 0 ]; then
    echo "Executing custom worker/system command: $@"
    exec "$@"
else
    echo "Launching default FastAPI service..."
    exec uvicorn app.main:app --host 0.0.0.0 --port 8000
fi
