# Base image
FROM python:3.8

# Set working directory
WORKDIR /airbnb-docker

# Set default environment variables
ENV PYTHONUNBUFFERED=1
ENV LANG=C.UTF-8
ENV DEBIAN_FRONTEND=noninteractive

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        tzdata \
        python3-pip \
        python3-dev \
        python3-venv \
        git \
        gcc \
        musl-dev \
        curl \
        redis-server \
        libc-dev \
        postgresql-client \
        postgresql-contrib \
        netcat \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy entrypoint.sh
COPY entrypoint.sh .

# Run entrypoint.sh
ENTRYPOINT ["/airbnb-docker/entrypoint.sh"]
