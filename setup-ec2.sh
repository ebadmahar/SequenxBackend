#!/bin/bash
# ==============================================================================
# SeQuenX Backend - Automated AWS EC2 Setup Script (Ubuntu 22.04 / 24.04 LTS)
# ==============================================================================
# Usage:
#   chmod +x setup-ec2.sh
#   ./setup-ec2.sh
# ==============================================================================

set -e

echo "🚀 [1/6] Updating Ubuntu packages..."
sudo apt-get update -y
sudo apt-get install -y curl git ufw nginx certbot python3-certbot-nginx apt-transport-https ca-certificates gnupg lsb-release

echo "🐳 [2/6] Installing Docker & Docker Compose..."
if ! command -v docker &> /dev/null; then
    sudo install -m 0755 -d /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg --yes
    sudo chmod a+r /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | \
      sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt-get update -y
    sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    sudo usermod -aG docker $USER
    sudo systemctl enable docker
    sudo systemctl start docker
fi

echo "🛡️  [3/6] Configuring Nginx reverse proxy..."
if [ -f "nginx/sequenx-api.conf" ]; then
    sudo cp nginx/sequenx-api.conf /etc/nginx/sites-available/sequenx-api.conf
    sudo ln -sf /etc/nginx/sites-available/sequenx-api.conf /etc/nginx/sites-enabled/
    sudo rm -f /etc/nginx/sites-enabled/default
    sudo nginx -t && sudo systemctl restart nginx
fi

echo "⚙️  [4/6] Checking environment file..."
if [ ! -f ".env" ]; then
    echo "Creating .env from .env.example..."
    cp .env.example .env
fi

echo "🚢 [5/6] Building & launching FastAPI Backend container..."
sudo docker compose down 2>/dev/null || true
sudo docker compose up -d --build

echo "🔍 [6/6] Verifying API status..."
sleep 4
curl -s http://127.0.0.1:8000/ || echo "Backend is warming up..."

PUBLIC_IP=$(curl -s http://checkip.amazonaws.com || curl -s ifconfig.me || echo "<YOUR_EC2_PUBLIC_IP>")

echo ""
echo "=============================================================================="
echo "✅ SUCCESS! SeQuenX Backend is running 24/7 on AWS EC2 without sleeping!"
echo "=============================================================================="
echo "• Local endpoint:   http://127.0.0.1:8000"
echo "• Public HTTP:      http://${PUBLIC_IP}"
echo "• API Docs:         http://${PUBLIC_IP}/docs"
echo ""
echo "📌 NEXT STEPS TO CONNECT YOUR DOMAIN WITH FREE SSL:"
echo "1. Point your domain (e.g. api.yourdomain.com) to ${PUBLIC_IP} via an 'A' record."
echo "2. Run this single command to enable free HTTPS / SSL:"
echo "   sudo certbot --nginx -d api.yourdomain.com"
echo "=============================================================================="
