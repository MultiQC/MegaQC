FROM mcr.microsoft.com/devcontainers/python:1-3.11-bullseye

# Install Node.js 18
RUN curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash - \
    && sudo apt-get install -y nodejs

# Install additional system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Create vscode user if it doesn't exist and set up directories
RUN if ! id -u vscode >/dev/null 2>&1; then \
        groupadd --gid 1000 vscode \
        && useradd --uid 1000 --gid vscode --shell /bin/bash --create-home vscode; \
    fi

# Install uv as vscode user
USER vscode
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/home/vscode/.cargo/bin:$PATH"

# Install Poetry as vscode user
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/home/vscode/.local/bin:$PATH"

# Set working directory and ensure vscode user owns it
USER root
WORKDIR /workspace
RUN chown -R vscode:vscode /workspace

# Switch back to vscode user for the rest of the setup
USER vscode

# Expose ports for Flask development server
EXPOSE 5000 8000

# Keep container running
CMD ["sleep", "infinity"] 