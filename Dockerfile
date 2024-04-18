# Use the Debian based development container as a base
FROM mcr.microsoft.com/devcontainers/base:debian

# Set environment variables for non-interactive shell operations
ENV \
    DEBIAN_FRONTEND=noninteractive \
    DEVCONTAINER=1

# Use bash for running shell commands with pipefail option for error handling
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install system dependencies required for the devcontainer and the Home Assistant add-on
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        dbus \
        network-manager \
        libpulse0 \
        xz-utils \
        python3 \
        python3-pip \
        python3-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy any necessary scripts and configurations from the devcontainer setup
COPY ./common/rootfs /
COPY ./common/rootfs_supervisor /
COPY ./common/install /tmp/common/install

# Run any necessary initialization scripts from the devcontainer setup
RUN bash /tmp/common/devcontainer_init \
    && bash /tmp/common/common_install_packages

# Create a virtual environment to isolate the Python setup for the add-on
RUN python3 -m venv /opt/venv

# Set the environment variable to ensure commands and scripts run in the virtual environment
ENV PATH="/opt/venv/bin:$PATH"

# Install Python packages required for the Home Assistant add-on
RUN pip install --no-cache-dir pyyaml websockets

# Modify user permissions to allow the vscode user to use Docker
RUN usermod -aG docker vscode

# Copy the Home Assistant add-on code into the container
COPY addon.py /
COPY config.yaml /

# Set the working directory to the root. This is where the add-on will be executed
WORKDIR /

# Command to start the add-on
CMD ["python3", "-u", "addon.py"]
