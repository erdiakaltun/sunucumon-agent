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
        r = requests.post(API_URL, json=data, timeout=10)
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
            requests.post("https://api.sunucumon.com/metrics", json=payload, headers=headers)
        except:
            pass

        time.sleep(interval)

if __name__ == "__main__":
    main()


