# composite_resource.py
from typing import Any, List
from framework.resources.base_resource import BaseResource
from datetime import datetime
from app.models.composite_model import Mealplan, DailyMealplan, WeeklyMealplan
from app.services.service_factory import ServiceFactory
from app.resources.microservice_client import MicroserviceClient
import requests

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import google.auth
import os
import json
import jwt
from datetime import datetime, timedelta

class CompositeResource(BaseResource):
    
    def __init__(self, config):
        super().__init__(config)
        self.data_service = ServiceFactory.get_service("CompositeResourceDataService")
        
        # Primary and fallback URLs for each microservice
        # self.recipe_url = 'http://54.162.118.11:8000'  # Yuxuan AWS URL
        self.recipe_url = 'https://sunny-truth-444203-c0.ue.r.appspot.com/'
        self.recipe_local_url = 'http://0.0.0.0:8000'  # Local URL
        
        self.nutrition_url = 'http://52.55.109.109:8002'  # Meilin AWS URL
        self.nutrition_local_url = 'http://0.0.0.0:8002'  # Local URL

        self.mealplan_url = 'http://3.87.242.187:5002'  # Phoebe/Claudia AWS URL
        self.mealplan_local_url = 'http://0.0.0.0:5002'  # Local URL

        self.chosen_recipe_url = self._get_available_url(self.recipe_url, self.recipe_local_url)
        self.chosen_nutrition_url = self._get_available_url(self.nutrition_url, self.nutrition_local_url)
        self.chosen_mealplan_url = self._get_available_url(self.mealplan_url, self.mealplan_local_url)
        print("URLS: ", self.chosen_recipe_url, self.chosen_nutrition_url, self.chosen_mealplan_url)

        # Initialize clients with the available URL
        self.recipe_client = MicroserviceClient(self._get_available_url(self.recipe_url, self.recipe_local_url))
        self.nutrition_client = MicroserviceClient(self._get_available_url(self.nutrition_url, self.nutrition_local_url))
        self.mealplan_client = MicroserviceClient(self._get_available_url(self.mealplan_url, self.mealplan_local_url))

    def _get_available_url(self, primary_url, fallback_url, timeout=2):
        """Returns primary_url if available, otherwise returns fallback_url."""
        return primary_url if self.is_service_available(primary_url, timeout) else fallback_url

    def is_service_available(self, url, timeout=2):
        """Checks if a service is available at the given URL within a specified timeout."""
        try:
            response = requests.get(url, timeout=timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False
        
    def get_jwt_token(self, username: str):
        """Fetch the JWT token for a user from the database."""
        return self.data_service.get_jwt_token(username)

    def update_jwt_token(self, user_id: int, new_jwt_token: str):
        """Update the JWT token for a user in the database."""
        return self.data_service.update_jwt_token(user_id, new_jwt_token)

    # Implementing the existing CRUD functions and count retrieval as needed
    def create_by_key(self, data: dict) -> Mealplan:
        d_service = self.data_service
        d_service.insert_data(
            self.database, self.meal_plans, data
        )
        return Mealplan(**data)
    
    def get_by_key(self, key: Any, collection: str):
        client = self._get_client_for_collection(collection)
        try:
            key = int(key)
        except ValueError:
            key = str(key)  # Adjust if key type is incorrect

        result = client.get_data_object(collection, key)
        return result

    def update_by_key(self, key: Any, data: dict, collection: str):
        client = self._get_client_for_collection(collection)
        try:
            key = int(key)
        except ValueError:
            key = str(key)

        client.update_data(collection, data, key)
        return self.get_by_key(key, collection)

    def delete_by_key(self, key: Any, collection: str):
        client = self._get_client_for_collection(collection)
        try:
            key = int(key)
        except ValueError:
            key = str(key)

        client.delete_data(collection, key)

    def get_total_count(self, collection: str) -> int:
        client = self._get_client_for_collection(collection)
        return client.get_total_count(collection)
