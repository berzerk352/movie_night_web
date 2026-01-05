# Multi-stage build for smaller image size
# Stage 1: Build dependencies
FROM python:3.12-alpine AS builder

# Install build dependencies
RUN apk add --no-cache \
    gcc \
    musl-dev \
    postgresql-dev \
    libffi-dev

WORKDIR /app

# Copy dependency files
COPY pyproject.toml ./

# Install uv for faster dependency installation
RUN pip install --no-cache-dir uv

# Install dependencies using uv
RUN uv pip install --system --no-cache -r pyproject.toml

# Stage 2: Runtime image
FROM python:3.12-alpine

# Install only runtime dependencies
RUN apk add --no-cache \
    libpq \
    libffi

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Create a non-root user to run the application
# Create credentials directory for mounting
RUN adduser -D -u 1000 appuser && \
    mkdir -p /app/credentials && \
    chown -R appuser:appuser /app

USER appuser

# Expose port
EXPOSE 5000

# Set environment variables for memory optimization
ENV FLASK_APP=app.py \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONHASHSEED=random \
    MALLOC_TRIM_THRESHOLD_=100000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)" || exit 1

# Run the application with gunicorn for production
# Reduced workers from 4 to 2, added memory-efficient settings
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--threads", "2", "--worker-class", "gthread", "--timeout", "120", "--max-requests", "1000", "--max-requests-jitter", "100", "app:app"]
