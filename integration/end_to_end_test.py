import requests

url = "YOUR_API_GATEWAY_URL"

response = requests.post(url, json={
    "query": "What are the admission requirements?"
})

print(response.json())