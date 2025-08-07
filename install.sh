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

mkdir -p /opt/sunucumon-agent/
cd /opt/sunucumon-agent/

wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/agent.py -O agent.py
wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/utils.py -O utils.py
wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/requirements.txt -O requirements.txt

# Dosya kontrolü
for file in agent.py utils.py requirements.txt; do
    if [ ! -f "$file" ]; then
        echo "❌ Dosya indirilemedi: $file"
        exit 1
    fi
done

pip3 install -r requirements.txt --quiet

echo "AGENT_ID=$AGENT_ID" > .env

# Log dosyalarını oluştur
touch /var/log/sunucumon-agent.log /var/log/sunucumon-agent-error.log

# Systemd servis dosyası oluştur
cat <<EOF > /etc/systemd/system/sunucumon-agent.service
[Unit]
Description=Sunucumon Monitoring Agent
After=network.target

[Service]
ExecStart=/usr/bin/python3 /opt/sunucumon-agent/agent.py
WorkingDirectory=/opt/sunucumon-agent/
StandardOutput=file:/var/log/sunucumon-agent.log
StandardError=file:/var/log/sunucumon-agent-error.log
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable sunucumon-agent
systemctl start sunucumon-agent

echo "✅ Kurulum tamamlandı. Agent servisi systemd üzerinden çalışıyor."
