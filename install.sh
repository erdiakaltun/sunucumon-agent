#!/bin/bash

AGENT_ID="$1"

if [ -z "$AGENT_ID" ]; then
    echo "❌ Kurulum başarısız: Lütfen agent ID parametresini girin."
    echo "Örnek: curl -s https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/install.sh | bash -s -- AGENT123"
    exit 1
fi

echo "🚀 Agent kurulumu başlatılıyor..."

if ! command -v python3 &>/dev/null; then
    echo "⏳ Python3 kuruluyor..."
    apt update && apt install -y python3 python3-pip
fi

mkdir -p /opt/sunucumon/
cd /opt/sunucumon/

wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/agent.py -O agent.py
wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/utils.py -O utils.py
wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/requirements.txt -O requirements.txt

pip3 install -r requirements.txt --quiet

echo "AGENT_ID=$AGENT_ID" > .env

nohup python3 agent.py > agent.log 2>&1 &

echo "✅ Kurulum tamamlandı. Agent arka planda çalışıyor."
