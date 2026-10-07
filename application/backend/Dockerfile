# syntax=docker/dockerfile:1
# ---- Stage 1: builder — install dependencies into a virtualenv ----
FROM python:3.12-slim AS builder
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
# Build a self-contained virtualenv so the runtime image stays minimal.
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade "pip>=25.2" "setuptools>=78.1.1" "wheel>=0.45" && \
    pip install --no-cache-dir -r requirements.txt && \
    # The runtime does not need pip/setuptools/wheel — remove them so their
    # vendored dependencies cannot be flagged by the image vulnerability scanner.
    pip uninstall -y pip setuptools wheel 2>/dev/null || true

# ---- Stage 2: runtime — copy only the venv + app, run as non-root ----
FROM python:3.12-slim AS runtime
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PATH="/opt/venv/bin:$PATH"
# Remove the base image's system pip/setuptools (their vendored packages carry
# the HIGH CVEs Trivy flags) and create an unprivileged user. The app runs via
# uvicorn + alembic from the copied venv and needs neither pip nor setuptools.
RUN python -m pip uninstall -y pip setuptools wheel 2>/dev/null || true && \
    rm -rf /usr/local/lib/python3.12/site-packages/pip* \
           /usr/local/lib/python3.12/site-packages/setuptools* \
           /usr/local/lib/python3.12/site-packages/pkg_resources \
           /usr/local/lib/python3.12/site-packages/_distutils_hack \
           /usr/local/bin/pip* && \
    useradd --create-home --uid 10001 appuser
COPY --from=builder /opt/venv /opt/venv
COPY alembic.ini ./
COPY alembic ./alembic
COPY app ./app
USER 10001
EXPOSE 8000
# Run migrations then start the API server.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
