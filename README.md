# SunucuMon Agent

Linux sunucularında CPU, RAM ve disk kullanımını izleyen hafif agent.

## Kurulum

1. Web panelinden agent ID'nizi alın.
2. Root yetkisi olan bir terminalde çalıştırın:

```bash
curl -fsSL https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/install.sh | sudo bash -s -- AGENT_ID
```

Agent ID yalnızca harf, rakam, alt çizgi ve tire içerebilir. Kurulum Python bağımlılıklarını sistem Python'una değil, `/opt/sunucumon-agent/.venv` sanal ortamına yükler ve systemd servisini bu ortamdan başlatır.

## Servis

```bash
sudo systemctl status sunucumon-agent
sudo systemctl restart sunucumon-agent
```

Loglar `/var/log/sunucumon-agent.log` ve `/var/log/sunucumon-agent-error.log` dosyalarına yazılır.
