# --- Stage 1: build dependencies ---
FROM python:3.12-slim AS builder

WORKDIR /build

RUN pip install --no-cache-dir --upgrade pip setuptools wheel

COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- Stage 2: final, lean runtime image ---
FROM python:3.12-slim

# Apply OS-level security patches without changing the base image version
RUN apt-get update && apt-get upgrade -y && rm -rf /var/lib/apt/lists/*

# Non-root user: if the container is compromised, the process doesn't run as root
RUN groupadd -r appuser && useradd -r -g appuser appuser

WORKDIR /app

# Copy only the already-installed packages from the builder stage
COPY --from=builder /root/.local /home/appuser/.local

# Remove build tooling (pip, setuptools, wheel) from the final runtime image.
# A running FastAPI app doesn't need them at runtime, and removing them also
# eliminates vendored (bundled) vulnerable copies of wheel/jaraco.context that
# ship inside setuptools itself and cannot be fixed by pinning versions in
# requirements.txt (lesson learned from a previous project's Trivy findings).
RUN find /home/appuser/.local/lib/python3.12/site-packages \
    -maxdepth 1 \( -iname "setuptools*" -o -iname "wheel*" -o -iname "pip*" \) \
    -exec rm -rf {} + \
    && rm -rf /home/appuser/.local/bin/pip* /home/appuser/.local/bin/wheel*

COPY app/ ./app/

RUN mkdir -p /app/data && chown -R appuser:appuser /app

USER appuser
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONUNBUFFERED=1

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
