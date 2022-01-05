# Builder
# Base image
FROM python:3.9.0-slim as builder

# Set working directory
WORKDIR /app

# Set default environment variables
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        gcc \
        musl-dev \
        libc-dev \
        git \
        libcurl4-gnutls-dev \
        librtmp-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# Final

# Base image
FROM python:3.9.0-slim

# Create directory for the app user
RUN mkdir -p /home/app

# Create all appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        gcc \
        curl \
        netcat \
        git \
        libcurl4-gnutls-dev \
        librtmp-dev \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# Copy project
COPY . $APP_HOME
