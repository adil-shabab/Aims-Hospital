import requests

try:
    response = requests.get('https://api.zego.im')
    print("Connection successful:", response.status_code)
except requests.exceptions.RequestException as e:
    print("Error connecting to Zego API:", e)
