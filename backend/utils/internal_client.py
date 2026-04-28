import requests

INTERNAL_KEY = "Recallix-Core-8892"

def internal_post(url, json_data):
    """Sends a POST request to the C++ infrastructure with the required internal key."""
    headers = {"X-Internal-Key": INTERNAL_KEY}
    return requests.post(url, json=json_data, headers=headers)

def internal_get(url):
    """Sends a GET request to the C++ infrastructure with the required internal key."""
    headers = {"X-Internal-Key": INTERNAL_KEY}
    return requests.get(url, headers=headers)
