# Multi-stage Dockerfile for AI-Friendly Repo Template
# This builds both frontend and backend for cloud deployment

# ============================================
# Stage 1: Build Frontend
# ============================================
FROM node:20-alpine AS frontend-builder

WORKDIR /app

# Copy package files for dependency installation
COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY repo_src/frontend/package.json ./repo_src/frontend/

# Install pnpm
RUN npm install -g pnpm@10.9.0

# Install dependencies
RUN pnpm install --frozen-lockfile

# Copy frontend source
COPY repo_src/frontend ./repo_src/frontend
COPY turbo.json ./

# Build frontend
RUN pnpm --filter @workspace/frontend build

# ============================================
# Stage 2: Build Backend
# ============================================
FROM python:3.11-slim AS backend-builder

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    make \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY repo_src/backend/requirements.txt ./repo_src/backend/

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r repo_src/backend/requirements.txt

# ============================================
# Stage 3: Production Runtime
# ============================================
FROM python:3.11-slim

WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copy Python dependencies from builder
COPY --from=backend-builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copy backend source
COPY --chown=appuser:appuser repo_src/backend ./repo_src/backend

# Copy built frontend
COPY --from=frontend-builder --chown=appuser:appuser /app/repo_src/frontend/dist ./repo_src/frontend/dist

# Copy necessary config files
COPY --chown=appuser:appuser .env.defaults ./

# Switch to non-root user
USER appuser

# Expose ports
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Set environment variables for cloud deployment
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8000 \
    ENVIRONMENT=production

# Start the application
CMD ["uvicorn", "repo_src.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
