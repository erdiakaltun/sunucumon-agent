# Log dosyasını yapılandır
logging.basicConfig(
    filename='/var/log/sunucumon-agent.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

import logging
import time
import requests
from requests.exceptions import RequestException

import os
import json
import time
import requests
import psutil
from utils import get_mac, get_hostname

API_URL = "https://api.sunucumon.com/register"
CONFIG_FILE = "/opt/sunucumon/config.json"

def get_agent_id():
    try:
        with open("/opt/sunucumon/.env") as f:
            for line in f:
                if line.startswith("AGENT_ID="):
                    return line.strip().split("=")[1]
    except:
        return None

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

def get_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE) as f:
            return json.load(f)
    return None

def register(agent_id, mac):
    data = {
        "agent_id": agent_id,
        "mac_address": mac,
        "hostname": get_hostname()
    }
    try:
        r = send_data_with_retry(api_url, headers, data)

        if r.status_code == 200:
            return r.json()
    except:
        pass
    return None

def main():
    config = get_config()
    if not config:
        agent_id = get_agent_id()
        mac = get_mac()
        result = register(agent_id, mac)
        if not result or "apikey" not in result:
            print("❌ API Key alınamadı.")
            return
        save_config(result)
        config = result

    apikey = config["apikey"]
    secret = config["secretkey"]
    interval = config.get("interval", 5)

    while True:
        payload = {
            "cpu": psutil.cpu_percent(),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "hostname": get_hostname(),
            "mac": get_mac()
        }

        headers = {
            "Authorization": f"Bearer {apikey}"
        }

        try:
            send_data_with_retry(api_url, headers, data)
        except:
            pass

        time.sleep(interval)

if __name__ == "__main__":
    main()


def send_data_with_retry(api_url, headers, payload, max_retries=5, delay=5):
    for attempt in range(1, max_retries + 1):
        try:
            response = send_data_with_retry(api_url, headers, data)
            if response.status_code == 200:
                logging.info("Veri başarıyla gönderildi.")
                return True
            else:
                logging.warning(f"Sunucu hatası ({response.status_code}): {response.text}")
        except RequestException as e:
            logging.error(f"Bağlantı hatası: {e}")
        
        logging.info(f"{attempt}. deneme başarısız. {delay} saniye sonra tekrar deneniyor...")
        time.sleep(delay)
    
    logging.critical("Maksimum tekrar sayısına ulaşıldı, veri gönderilemedi.")
    return False



