# composite_resource.py
from typing import Any, List
from framework.resources.base_resource import BaseResource
from datetime import datetime
from app.models.composite_model import Mealplan, DailyMealplan, WeeklyMealplan
from app.services.service_factory import ServiceFactory
from app.resources.microservice_client import MicroserviceClient
import requests

class CompositeResource(BaseResource):
    
    def __init__(self, config):
        super().__init__(config)
        
        # Primary and fallback URLs for each microservice
        self.recipe_url = 'http://35.243.235.4:8000'  # Yuxuan AWS URL
        self.recipe_local_url = 'http://0.0.0.0:8000'  # Local URL
        
        self.nutrition_url = 'http://54.173.155.140:8002'  # Meilin AWS URL
        self.nutrition_local_url = 'http://0.0.0.0:8002'  # Local URL

        self.mealplan_url = 'http://35.193.95.132:5002'  # Phoebe/Claudia AWS URL
        self.mealplan_local_url = 'http://0.0.0.0:5002'  # Local URL

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

    # def get_by_key(self, key: Any, collection: str):
    #     d_service = self.data_service
    #     try:
    #         key = int(key)
    #     except ValueError:
    #         key = str(key)  # Return an error code for incorrect key type
        
    #     if collection == "meal_plans":
    #         result = d_service.get_data_object(
    #             self.database, self.meal_plans, key_field=self.meal_plans_pk, key_value=key
    #         )
    #         return Mealplan(**result)
    #     elif collection == "weekly_meal_plans":
    #         result = d_service.get_data_object(
    #             self.database, self.weekly_meal_plans, key_field=self.weekly_pk, key_value=key
    #         )
    #         return WeeklyMealplan(**result)
    #     elif collection == "daily_meal_plans":
    #         result = d_service.get_data_object(
    #             self.database, self.daily_meal_plans, key_field=self.daily_pk, key_value=key
    #         )
    #         return DailyMealplan(**result)

    # def update_by_key(self, key: str, data: dict) -> Mealplan:
    #     d_service = self.data_service
    #     d_service.update_data(
    #         self.database, self.meal_plans, data, key_field=self.key_field, key_value=key
    #     )
    #     return self.get_by_key(key)

    # def delete_by_key(self, key: str) -> None:
    #     d_service = self.data_service
    #     d_service.delete_data(
    #         self.database, self.meal_plans, key_field=self.key_field, key_value=key
    #     )

    # def get_total_count(self) -> int:
    #     return self.data_service.get_total_count(self.database, self.meal_plans)
