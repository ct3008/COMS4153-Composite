# microservice_client.py
import requests

class MicroserviceClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get(self, endpoint: str, params=None):
        response = requests.get(f"{self.base_url}/{endpoint}", params=params)
        response.raise_for_status()
        return response.json()

    def post(self, endpoint: str, data: dict):
        response = requests.post(f"{self.base_url}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()

    def put(self, endpoint: str, data: dict):
        response = requests.put(f"{self.base_url}/{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    
    def delete(self, endpoint: str):
        url = f"{self.base_url}/{endpoint}"
        response = requests.delete(url)
        response.raise_for_status()  # Raises an error for unsuccessful requests
        return response.json()
    
    
	
