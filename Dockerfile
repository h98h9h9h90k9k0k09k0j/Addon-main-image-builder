# Build the image with either depending on the architecture
# ghcr.io/home-assistant/aarch64-base-debian:bookworm
# ghcr.io/home-assistant/amd64-base-debian:bookworm

FROM ghcr.io/home-assistant/aarch64-base-debian:bookworm

# Install Python and necessary build dependencies
RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3.11-dev \
    libffi-dev \
    libssl-dev \
    libopencv-dev \
    python3.11-venv \
    git \
    dos2unix \
    curl \
    ffmpeg && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy only the requirements file to leverage Docker cache
COPY requirements.txt /app/requirements.txt

# Create a virtual environment in the /opt/venv directory
RUN python3 -m venv /opt/venv 

# Set the environment variable to ensure commands and scripts run in the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages in the virtual environment
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy data for add-on
COPY . /app

# Use bash for running commands
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Expose necessary ports
EXPOSE 3030 5000 50051 8080 1935 8554 1234 9000


# Command to run the Home Assistant add-on
# CMD ["bash", "run.sh"]
