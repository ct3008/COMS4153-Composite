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

# JWT Secret and Expiration Time
# JWT_SECRET = "your_jwt_secret_key"
# JWT_ALGORITHM = "HS256"
# JWT_EXPIRATION_MINUTES = 30  # Token expiry time in minutes

# # OAuth2 password bearer token
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# # Function to authenticate the user using Google
# def google_login(request: Request):
#     # Assuming credentials.json is your Google OAuth2 client credentials file
#     client_secrets_file = os.path.join(os.getcwd(), 'client_secrets.json')
#     flow = InstalledAppFlow.from_client_secrets_file(
#         client_secrets_file, scopes=["https://www.googleapis.com/auth/userinfo.profile"]
#     )
#     credentials = flow.run_local_server(port=0)

#     # Get the user's info
#     session = credentials.authorize(Request())
#     user_info = session.get("https://www.googleapis.com/oauth2/v3/userinfo").json()

#     # You can use user_info to create a user record in the database, etc.

#     # After successful login, issue a JWT token for the user
#     token = create_jwt_token(user_info["sub"])
#     return {"access_token": token, "token_type": "bearer"}

# # JWT token creation
# def create_jwt_token(user_id: str):
#     expiration = datetime.utcnow() + timedelta(minutes=JWT_EXPIRATION_MINUTES)
#     to_encode = {"sub": user_id, "exp": expiration}
#     encoded_jwt = jwt.encode(to_encode, JWT_SECRET, algorithm=JWT_ALGORITHM)
#     return encoded_jwt

# # Middleware to validate JWT tokens
# async def validate_jwt_token(token: str = Depends(oauth2_scheme)):
#     try:
#         payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
#         return payload
#     except jwt.PyJWTError:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

# Apply this middleware for token validation globally or on specific routes


class CompositeResource(BaseResource):
    
    def __init__(self, config):
        super().__init__(config)
        self.data_service = ServiceFactory.get_service("CompositeResourceDataService")
        
        # Primary and fallback URLs for each microservice
        # self.recipe_url = 'http://35.243.235.4:8000'  # Yuxuan AWS URL
        self.recipe_url = 'https://sunny-truth-444203-c0.ue.r.appspot.com/'
        self.recipe_local_url = 'http://0.0.0.0:8000'  # Local URL
        
        self.nutrition_url = 'http://54.210.67.10:8002'  # Meilin AWS URL
        self.nutrition_local_url = 'http://0.0.0.0:8002'  # Local URL

        self.mealplan_url = 'http://3.82.4.51:5002'  # Phoebe/Claudia AWS URL
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

    # def make_authenticated_request(self, client, method, endpoint, user_id, data=None):
    #     """
    #     Makes a request to the specified client with a user-specific header.
    #     """
    #     headers = {"X-User-ID": str(user_id)}  # Include user ID as a custom header
    #     if method == "GET":
    #         return client.get(endpoint, headers=headers)
    #     elif method == "POST":
    #         return client.post(endpoint, json=data, headers=headers)
    #     elif method == "PUT":
    #         return client.put(endpoint, json=data, headers=headers)
    #     elif method == "DELETE":
    #         return client.delete(endpoint, headers=headers)
    #     else:
    #         raise ValueError(f"Unsupported HTTP method: {method}")

    # def get_mealplans(self):
    #     return self.make_authenticated_request(self.mealplan_client, "GET", "mealplans/")
    




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
