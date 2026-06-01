#!/bin/bash
set -e

echo "=========================================="
echo "   HIREMIND SYSTEM NATIVE DEPLOYER        "
echo "=========================================="

# 1. Install all system dependencies on the host
echo "[1/6] Installing system-level dependencies on host..."
sudo apt-get update
sudo apt-get install -y \
    build-essential \
    python3-dev \
    python3-venv \
    python3-pip \
    libpango-1.0-0 \
    libharfbuzz0b \
    libpangoft2-1.0-0 \
    libffi-dev \
    shared-mime-info \
    git \
    libcairo2 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libmagic1

# 2. Setup Virtual Environment
echo "[2/6] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# 3. Install Python requirements
echo "[3/6] Installing Python packages (this will take a couple of minutes)..."
mkdir -p $(pwd)/.pip_tmp
export TMPDIR=$(pwd)/.pip_tmp
pip install --upgrade pip
pip install --no-cache-dir -r requirements.txt
rm -rf $(pwd)/.pip_tmp

# 4. Download spaCy models
echo "[4/6] Downloading spaCy NLP models..."
python -m spacy download en_core_web_md
python -m spacy download en_core_web_sm

# 5. Create Systemd Service to run backend continuously in the background
echo "[5/6] Creating Systemd service for auto-restart and boot-persistence..."
sudo bash -c "cat > /etc/systemd/system/hiremind.service <<EOF
[Unit]
Description=HireMind FastAPI Backend Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=$(pwd)
EnvironmentFile=$(pwd)/.env
ExecStart=$(pwd)/venv/bin/uvicorn backend.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF"

# 6. Start and enable the service
echo "[6/6] Starting HireMind service..."
sudo systemctl daemon-reload
sudo systemctl start hiremind
sudo systemctl enable hiremind

echo "========================================================="
echo " SUCCESS! The backend is running directly on port 8000!"
echo "---------------------------------------------------------"
echo " View live backend logs:  sudo journalctl -u hiremind -f"
echo " Restart backend service:  sudo systemctl restart hiremind"
echo " Stop backend service:     sudo systemctl stop hiremind"
echo "========================================================="
