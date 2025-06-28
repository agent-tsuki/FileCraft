# ---------- Base stage (for dependency installation) ----------
FROM python:3.12-slim AS base

# Set working directory
WORKDIR /app

# Prevent interactive prompts during package install
ENV DEBIAN_FRONTEND=noninteractive

# System dependencies for building some Python packages
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install pipenv or poetry if needed, otherwise stick to pip
# Install pip upgrade + pip-tools (optional)
RUN pip install --upgrade pip

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# ---------- Final stage ----------
FROM base AS dev

# Copy source code
COPY . .

# Copy .env file (optional, if you want to bake it in)
# COPY .env .  # Better handled in docker-compose

# Expose FastAPI port
EXPOSE 8080

# Default command: use uvicorn with reload for development
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--reload"]
