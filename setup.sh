#!/bin/bash

# MCP Proxy Setup Script
# This script helps you set up the MCP Proxy server quickly

set -e

echo "======================================"
echo "MCP Proxy Server Setup"
echo "======================================"
echo ""

# Check Python version
echo "1. Checking Python version..."
python3 --version

# Install Python dependencies
echo ""
echo "2. Installing Python dependencies..."
pip install -r requirements.txt

# Setup environment file
echo ""
echo "3. Setting up environment configuration..."
if [ ! -f .env ]; then
    cp .env.example .env
    echo "Created .env file. Please edit it to set your PROXY_TOKEN"
    echo ""
    echo "Generating a random proxy token for you..."
    RANDOM_TOKEN=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    sed -i "s/your_secure_proxy_token_here/$RANDOM_TOKEN/" .env
    echo "✓ Generated random PROXY_TOKEN: $RANDOM_TOKEN"
    echo "  (You can change this in .env file)"
else
    echo "✓ .env file already exists"
fi

# Build TypeScript client
echo ""
echo "4. Building TypeScript client..."
cd client
npm install
npm run build
cd ..

echo ""
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo ""
echo "To start the server, run:"
echo "  python3 server.py"
echo ""
echo "The server will be available at:"
echo "  http://localhost:8000"
echo ""
echo "Make sure to note your PROXY_TOKEN from the .env file!"
echo ""
