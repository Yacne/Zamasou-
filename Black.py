import socket
import requests
import platform
import subprocess
from bs4 import BeautifulSoup
import json

ZAMASOU_IP = "127.0.0.1"
ZAMASOU_PORT = 2024

def get_ip_info():
    try:
        response = requests.get("http://ipinfo.io/json")
        data = response.json()
        ip_address = data.get("ip")
        return ip_address
    except Exception as e:
        print(f"Error occurred: {e}")
        return None

def get_device_name():
    try:
        device_name = platform.node()
        if device_name == "localhost" or not device_name:
            device_name = socket.gethostname()

        if "localhost" in device_name or not device_name:
            try:
                model = subprocess.run(['getprop', 'ro.product.model'], capture_output=True, text=True).stdout.strip()
                manufacturer = subprocess.run(['getprop', 'ro.product.manufacturer'], capture_output=True, text=True).stdout.strip()
                search_query = f"{manufacturer} {model}"
                device_name = fetch_device_name_from_google(search_query)
            except Exception as e:
                print(f"Error occurred while fetching device name using subprocess: {e}")
                device_name = "Unknown Device"
        return device_name
    except Exception as e:
        print(f"Error occurred while fetching device name: {e}")
        return "Unknown Device"

def fetch_device_name_from_google(query):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}
        search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        response = requests.get(search_url, headers=headers)

        soup = BeautifulSoup(response.text, 'html.parser')
        first_result = soup.find('h3')

        if first_result:
            device_name = first_result.text.split(' - ')[0]
            return device_name
        else:
            return query
    except Exception as e:
        print(f"Error occurred while searching on Google: {e}")
        return query

def send_data(ip, port, data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(json.dumps(data).encode())
            print("Data sent successfully!")
    except Exception as e:
        print(f"Error occurred while sending data: {e}")

def main():
    ip = get_ip_info()
    device_name = get_device_name()

    data = {
        "ip_address": ip,
        "device_name": device_name
    }

    send_data(ZAMASOU_IP, ZAMASOU_PORT, data)

if __name__ == "__main__":
    main()
