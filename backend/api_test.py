import requests

url = "http://127.0.0.1:5000/predict/bangalore"

response = requests.get(url)

print(response.json())