FROM python:3.10-slim

# Set environment variables
ENV PYTHONFAULTHANDLER=1 \
    PYTHONHASHSEED=random \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.7.1

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install "poetry==$POETRY_VERSION"

# Set working directory
WORKDIR /app

# Copy only requirements first to leverage Docker cache
COPY pyproject.toml poetry.lock* ./

# Configure poetry to not use virtual environments
RUN poetry config virtualenvs.create false \
    && poetry install --no-dev

# Copy application code
COPY . .

# Set entry point
ENTRYPOINT ["python", "-m", "db_migrations.cli"]

# Default command (can be overridden)
CMD ["--help"]