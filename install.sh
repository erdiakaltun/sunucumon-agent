#!/bin/bash
set -euo pipefail

AGENT_ID="${1:-}"

if [[ ${EUID} -ne 0 ]]; then
    echo "❌ Kurulum için root yetkisi gerekir. sudo ile tekrar deneyin."
    exit 1
fi

if [[ ! "${AGENT_ID}" =~ ^[A-Za-z0-9_-]+$ ]]; then
    echo "❌ Geçersiz agent ID. Yalnızca harf, rakam, alt çizgi ve tire kullanın."
    echo "Örnek: curl -fsSL https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/install.sh | sudo bash -s -- AGENT123"
    exit 1
fi

echo "🚀 Agent kurulumu başlatılıyor..."

if ! command -v python3 >/dev/null 2>&1; then
    echo "⏳ Python3 kuruluyor..."
    apt-get update
    apt-get install -y python3 python3-venv
fi

if ! python3 -m venv --help >/dev/null 2>&1; then
    echo "⏳ Python venv bileşeni kuruluyor..."
    apt-get update
    apt-get install -y python3-venv
fi

install -d -m 0755 /opt/sunucumon-agent
cd /opt/sunucumon-agent

wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/agent.py -O agent.py
wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/utils.py -O utils.py
wget -q https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/requirements.txt -O requirements.txt

for file in agent.py utils.py requirements.txt; do
    if [[ ! -s "${file}" ]]; then
        echo "❌ Dosya indirilemedi veya boş: ${file}"
        exit 1
    fi
done

python3 -m venv /opt/sunucumon-agent/.venv
/opt/sunucumon-agent/.venv/bin/python -m pip install --upgrade pip --quiet
/opt/sunucumon-agent/.venv/bin/python -m pip install -r requirements.txt --quiet

printf 'AGENT_ID=%s\n' "${AGENT_ID}" > .env
chmod 600 .env

touch /var/log/sunucumon-agent.log /var/log/sunucumon-agent-error.log

cat <<EOF > /etc/systemd/system/sunucumon-agent.service
[Unit]
Description=Sunucumon Monitoring Agent
After=network.target

[Service]
ExecStart=/opt/sunucumon-agent/.venv/bin/python /opt/sunucumon-agent/agent.py
WorkingDirectory=/opt/sunucumon-agent/
StandardOutput=file:/var/log/sunucumon-agent.log
StandardError=file:/var/log/sunucumon-agent-error.log
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable sunucumon-agent
systemctl restart sunucumon-agent

echo "✅ Kurulum tamamlandı. Agent servisi systemd üzerinden çalışıyor."
