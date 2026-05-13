# Use a bookworm-based Python 3.14 image so devcontainer features stay on a supported distro
FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

ENV UV_INSTALL_DIR=/usr/local/bin

# Install Containerlab and the repo's automation dependencies.
RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl sshpass gnupg2 bridge-utils iproute2 \
    && bash -c "$(curl -sL https://get.containerlab.dev)" \
    && usermod -aG clab_admins vscode \
    && bash -c "curl -LsSf https://astral.sh/uv/install.sh | sh" \
    && uv pip install --system \
        "pyavd[ansible]==6.1.0" \
        eos-downloader \
        nornir \
        nornir-utils \
        pyeapi \
        PyYAML \
    && mkdir -p /usr/share/ansible/collections \
    && ansible-galaxy collection install arista.avd:==6.1.0 -p /usr/share/ansible/collections \
    && rm -rf /var/lib/apt/lists/* /root/.cache/uv

# Set up workdir
WORKDIR /workspaces

CMD ["sleep", "infinity"]