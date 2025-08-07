import logging
import time
import requests
from requests.exceptions import RequestException

import os
import json
import psutil
from utils import get_mac, get_hostname

API_REGISTER_URL = "https://api.sunucumon.com/register"
API_METRICS_URL = "https://api.sunucumon.com/metrics"
CONFIG_FILE = "/opt/sunucumon-agent/config.json"
ENV_FILE = "/opt/sunucumon-agent/.env"

# Log dosyasını yapılandır
logging.basicConfig(
    filename='/var/log/sunucumon-agent.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def get_agent_id():
    try:
        with open(ENV_FILE) as f:
            for line in f:
                if line.startswith("AGENT_ID="):
                    return line.strip().split("=")[1]
    except Exception as e:
        logging.error(f".env dosyası okunamadı: {e}")
        return None

def save_config(data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"Config kaydedilemedi: {e}")

def get_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Config okunamadı: {e}")
            return None
    return None

def send_data_with_retry(api_url, headers, payload, max_retries=5, delay=5):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(api_url, headers=headers, json=payload, timeout=10)
            if response.status_code == 200:
                logging.info("Veri başarıyla gönderildi.")
                return response
            else:
                logging.warning(f"Sunucu hatası ({response.status_code}): {response.text}")
        except RequestException as e:
            logging.error(f"Bağlantı hatası: {e}")
        
        logging.info(f"{attempt}. deneme başarısız. {delay} saniye sonra tekrar deneniyor...")
        time.sleep(delay)
    
    logging.critical("Maksimum tekrar sayısına ulaşıldı, veri gönderilemedi.")
    return None

def register(agent_id, mac):
    data = {
        "agent_id": agent_id,
        "mac_address": mac,
        "hostname": get_hostname()
    }
    headers = {
        "Content-Type": "application/json"
    }
    response = send_data_with_retry(API_REGISTER_URL, headers, data)
    if response and response.status_code == 200:
        try:
            return response.json()
        except Exception as e:
            logging.error(f"Register API JSON parse hatası: {e}")
    return None

def main():
    config = get_config()
    if not config:
        agent_id = get_agent_id()
        if not agent_id:
            logging.critical("Agent ID bulunamadı, çıkılıyor.")
            return
        mac = get_mac()
        result = register(agent_id, mac)
        if not result or "apikey" not in result:
            logging.critical("API Key alınamadı, çıkılıyor.")
            return
        save_config(result)
        config = result

    apikey = config["apikey"]
    secret = config["secretkey"]  # İleride AES şifreleme ile değişecek
    interval = config.get("interval", 5)

    headers = {
        "Authorization": f"Bearer {apikey}",
        "Content-Type": "application/json"
    }

    while True:
        payload = {
            "cpu": psutil.cpu_percent(interval=1),
            "ram": psutil.virtual_memory().percent,
            "disk": psutil.disk_usage('/').percent,
            "hostname": get_hostname(),
            "mac": get_mac()
        }
        send_data_with_retry(API_METRICS_URL, headers, payload)
        time.sleep(interval)

if __name__ == "__main__":
    main()
