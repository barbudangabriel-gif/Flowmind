#!/bin/bash
# Setup SSH on Hetzner server without needing to paste
# Run this locally, then execute instructions on server console

SERVER_IP="91.107.206.64"

# Step 1: Get the Codespaces public key
CODESPACE_PUB_KEY=$(cat ~/.ssh/flowmind_ed25519.pub)
echo "Your Codespaces public key:"
echo "$CODESPACE_PUB_KEY"
echo ""

# Step 2: Create command to add to authorized_keys
echo "COPY THIS ENTIRE COMMAND and run it in Hetzner console:"
echo "============================================================"
echo "mkdir -p ~/.ssh && echo '$CODESPACE_PUB_KEY' >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys && chmod 700 ~/.ssh"
echo "============================================================"
echo ""
echo "Then test with:"
echo "ssh -i ~/.ssh/flowmind_ed25519 root@$SERVER_IP 'echo SSH Works!'"
