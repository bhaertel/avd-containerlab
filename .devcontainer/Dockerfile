# Use a bookworm-based Python 3.14 image so devcontainer features stay on a supported distro
FROM mcr.microsoft.com/devcontainers/python:3.14-bookworm

# Install system dependencies for Containerlab and Ansible
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends curl sshpass gnupg2 bridge-utils iproute2

# 1. Install latest Containerlab
RUN bash -c "$(curl -sL https://get.containerlab.dev)"

# Allow the default remote user to run containerlab without manual usermod.
RUN usermod -aG clab_admins vscode

# 2. Install pyavd with [ansible] 
RUN pip3 install "pyavd[ansible]==6.1.0"

# 3. Install Arista.AVD Ansible Collection
RUN mkdir -p /usr/share/ansible/collections \
    && ansible-galaxy collection install arista.avd:==6.1.0 -p /usr/share/ansible/collections

# 4. Install Arista ARDL Downloader
RUN pip3 install eos-downloader

# Set up workdir
WORKDIR /workspaces

CMD ["sleep", "infinity"]