FROM python:3.11.11-slim

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y gcc default-libmysqlclient-dev pkg-config libpango1.0-0 libgdk-pixbuf2.0-0 libffi-dev libcairo2 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN pip uninstall channels daphne -y || true \
    && pip install --no-cache-dir -U 'channels[daphne]'

COPY . .

COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 5012

# Run as non-root user
RUN adduser --disabled-password --gecos '' appuser \
    && mkdir -p /app/staticfiles \
    && chown -R appuser:appuser /app/staticfiles /entrypoint.sh
USER appuser

CMD ["/entrypoint.sh"]