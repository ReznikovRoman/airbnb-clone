# Builder
# Base image
FROM python:3.8.0 as builder

# Set working directory
WORKDIR /app

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
        gcc \
        musl-dev \
        curl \
        libc-dev \
        postgresql-client \
        postgresql-contrib \
        netcat \
        && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install project dependencies
COPY ./requirements.txt /app/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt


# Final

# Base image
FROM python:3.8.0-slim

# Create directory for the app user
RUN mkdir -p /home/app

# Create all appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
        netcat \
        && \
    apt-get clean
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

# Copy project
COPY . $APP_HOME

# Run entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]
