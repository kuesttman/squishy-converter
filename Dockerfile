FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive \
    PIP_NO_CACHE_DIR=1 \
    CONFIG_PATH=/config/config.json

# Create app user
RUN groupadd -r squishy && \
    useradd -r -g squishy -d /app -s /bin/bash squishy

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    gnupg \
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://repo.jellyfin.org/jellyfin_team.gpg.key | gpg --dearmor -o /etc/apt/keyrings/jellyfin.gpg \
    && echo "deb [arch=$( dpkg --print-architecture ) signed-by=/etc/apt/keyrings/jellyfin.gpg] https://repo.jellyfin.org/debian bookworm main" | tee /etc/apt/sources.list.d/jellyfin.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
    jellyfin-ffmpeg6 \
    openssl \
    locales \
    && ln -s /usr/lib/jellyfin-ffmpeg/ffmpeg /usr/local/bin/ffmpeg \
    && ln -s /usr/lib/jellyfin-ffmpeg/ffprobe /usr/local/bin/ffprobe \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Generate locale
RUN echo "pt_BR.UTF-8 UTF-8" > /etc/locale.gen && \
    locale-gen

# Create necessary directories
RUN mkdir -p /app && \
    chown -R squishy:squishy /app

# Set working directory
WORKDIR /app

# Copy project files
COPY . /app/
RUN chown -R squishy:squishy /app

# Copy entrypoint script
# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN sed -i 's/\r$//' /entrypoint.sh && \
    chmod +x /entrypoint.sh

# Install Python dependencies as root (globally)
RUN pip install --upgrade pip && \
    pip install -e .

# Compile translations
# RUN pybabel compile -d squishy/translations

# Expose port
EXPOSE 5101

# Command to run (entrypoint will switch to squishy user)
ENTRYPOINT ["/entrypoint.sh"]
