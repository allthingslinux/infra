#!/bin/bash
set -e

# Install OpenTofu
VERSION="1.6.0"
OS="linux"
ARCH="amd64"

# Download OpenTofu
wget -q https://github.com/opentofu/opentofu/releases/download/v${VERSION}/tofu_${VERSION}_${OS}_${ARCH}.zip -O /tmp/tofu.zip

# Install to /usr/local/bin
sudo unzip -o /tmp/tofu.zip -d /usr/local/bin/
sudo chmod +x /usr/local/bin/tofu

# Verify installation
tofu --version
echo "OpenTofu ${VERSION} installed successfully!"
