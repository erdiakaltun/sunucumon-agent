# SunucuMon Agent

Linux sunucuların CPU, RAM, Disk gibi sistem verilerini izlemek için hafif agent uygulaması.

## Kurulum

1. Web panelden `agent_id` alın
2. Aşağıdaki komutu terminalde çalıştırın:

```bash
curl -s https://raw.githubusercontent.com/erdiakaltun/sunucumon-agent/main/install.sh | bash -s -- AGENT_ID

