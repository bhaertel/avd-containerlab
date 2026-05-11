# Use a bookworm-based Python 3.14 image so devcontainer features stay on a supported distro
FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

# Install system dependencies for Containerlab and Ansible
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl sshpass gnupg2 bridge-utils iproute2

# 1. Install latest Containerlab
RUN bash -c "$(curl -sL https://get.containerlab.dev)"

# Allow the default remote user to run containerlab without manual usermod.
RUN usermod -aG clab_admins vscode

# 2. Install uv for Python package management
ENV UV_INSTALL_DIR=/usr/local/bin
RUN bash -c "curl -LsSf https://astral.sh/uv/install.sh | sh"

# 3. Install pyavd with [ansible] 
RUN uv pip install --system "pyavd[ansible]==6.1.0"

# 4. Install Arista.AVD Ansible Collection
RUN mkdir -p /usr/share/ansible/collections \
    && ansible-galaxy collection install arista.avd:==6.1.0 -p /usr/share/ansible/collections

# 5. Install Arista ARDL Downloader
RUN uv pip install --system eos-downloader

# 6. Install lab automation Python dependencies
RUN uv pip install --system nornir nornir-utils pyeapi PyYAML

# Set up workdir
WORKDIR /workspaces

CMD ["sleep", "infinity"]