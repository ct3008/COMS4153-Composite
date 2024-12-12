# composite.py
from fastapi import APIRouter, HTTPException, Request, Query
from app.resources.composite_resource import CompositeResource
from app.models.composite_model import Mealplan, DailyMealplan, WeeklyMealplan, Nutrition, Recipe, PaginatedResponse, Alternatives
from app.services.service_factory import ServiceFactory

from fastapi import HTTPException, APIRouter, Depends
from datetime import datetime, timedelta
from jose import JWTError, jwt
from pydantic import BaseModel
# res = ServiceFactory.get_service("MealplanResource")
#     daily_mealplans = res.get_daily_meal_plans_by_date(date)

router = APIRouter()
resource = CompositeResource(config={})  # Pass actual config if needed

SECRET_KEY = "your_secret_key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Simulated database
fake_user_db = {
    "ct3008": {"user_id": 1, "username": "ct3008", "password": "password"}
}


class LoginRequest(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

router = APIRouter()

# def authenticate_user(username: str, password: str):
#     user = fake_user_db.get(username)
#     if user and user["password"] == password:
#         return user
#     return None

# def create_access_token(data: dict, expires_delta: timedelta = None):
#     to_encode = data.copy()
#     if expires_delta:
#         expire = datetime.utcnow() + expires_delta
#     else:
#         expire = datetime.utcnow() + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
#     return encoded_jwt

# @router.post("/login", response_model=Token)
# async def login(user: User):
#     db_user = authenticate_user(user.username, user.password)
#     if not db_user:
#         raise HTTPException(status_code=401, detail="Invalid username or password")
#     access_token = create_access_token(data={"sub": db_user["user_id"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
#     return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login(request: LoginRequest):
    # user = fake_user_db.get(request.username)
    res = ServiceFactory.get_service("CompositeResource")
    user = res.get_jwt_token(request.username)
    print("USER: ", user)
    if not user:
        raise HTTPException(status_code=400, detail="Invalid username")

    # Create the JWT
    expiration = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    token_data = {"user_id": user["user_id"], "username": user["username"], "exp": expiration}
    jwt_token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    update_response = resource.update_jwt_token(user["user_id"], jwt_token)

    # (Optional) Save JWT in database
    user["jwt_token"] = jwt_token
    print("jwt token: ", jwt_token)

    return {"access_token": jwt_token, "token_type": "bearer"}

@router.get("/composite/recipes/id/{recipe_id}", tags=["Recipes"])
async def get_recipe(recipe_id: int):
    try:
        recipe = resource.recipe_client.get(f"recipes/id/{recipe_id}")
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.get("/composite/recipes/name/{recipe_name}", tags=["Recipes"])
async def get_recipe(recipe_name: str):
    try:
        recipe = resource.recipe_client.get(f"recipes/name/{recipe_name}")
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/composite/recipes", tags=["Recipes"])
async def get_recipes(skip: int = Query(0, ge=0), limit: int = Query(10, gt=0)):
    """
    Retrieve recipes with pagination parameters skip and limit.
    """
    try:
        # Forward the query parameters to the recipe client
        recipes = resource.recipe_client.get(f"recipes?skip={skip}&limit={limit}")
        return recipes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/composite/recipes/allrecipes", tags=["Recipes"])
async def get_recipes():
    """
    Retrieve all recipes.
    """
    try:
        # Forward the query parameters to the recipe client
        recipes = resource.recipe_client.get(f"recipes?skip=0&limit=100")
        return recipes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/composite/recipes", tags=["Recipes"], response_model=Recipe)
async def create_recipe(recipe: Recipe):
    try:
        # print(recipe)
        recipe = resource.recipe_client.post(f"recipes", recipe.dict())
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/composite/recipes/id/{recipe_id}", tags=["Recipes"], response_model=Recipe)
async def update_recipe(recipe_id: int, recipe: Recipe):
    try:
        # print(recipe)
        recipe = resource.recipe_client.put(f"recipes/id/{recipe_id}", recipe.dict())
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/composite/recipes/name/{recipe_name}", tags=["Recipes"], response_model=Recipe)
async def update_recipe(recipe_name: str, recipe: Recipe):
    try:
        # print(recipe)
        recipe = resource.recipe_client.put(f"recipes/name/{recipe_name}", recipe.dict())
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/composite/recipes/id/{recipe_id}", tags=["Recipes"])
async def delete_recipe(recipe_id: int):
    try:
        print("try delete")
        # Perform delete operation for the recipe
        response = resource.recipe_client.delete(f"recipes/id/{recipe_id}")
        print(response)
        return {"message": "Recipe deleted successfully", "recipe_id": recipe_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.delete("/composite/recipes/name/{recipe_name}", tags=["Recipes"])
async def delete_recipe(recipe_name: str):
    try:
        print("try delete")
        # Perform delete operation for the recipe
        response = resource.recipe_client.delete(f"recipes/name/{recipe_name}")
        print(response)
        return {"message": "Recipe deleted successfully", "recipe_id": recipe_name}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# NUTRITION

@router.get("/composite/nutrition/{ingredient_id}", tags=["Nutrition"])
async def get_ingredient_nutrition(ingredient_id: int):
    try:
        nutrition_info = resource.nutrition_client.get(f"nutrition/{ingredient_id}")
        return nutrition_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/composite/nutrition/alternatives/{ingredient_id}", tags=["Nutrition"])
async def get_alternatives_from_ingredient(ingredient_id: int):
    try:
        nutrition_info = resource.nutrition_client.get(f"nutrition/alternatives/{ingredient_id}")
        return nutrition_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/composite/nutrition/alternatives/recipe/{recipe_id}", tags=["Nutrition"])
async def get_alternatives_from_recipe(recipe_id: int):
    try:
        nutrition_info = resource.nutrition_client.get(f"nutrition/alternatives/recipe/{recipe_id}")
        return nutrition_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/composite/nutrition/recipe/stats/{recipe_id}", tags=["Nutrition"])
async def get_ingredient_nutrition(recipe_id: int):
    try:
        nutrition_info = resource.nutrition_client.get(f"nutrition/recipe/stats/{recipe_id}")
        return nutrition_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/composite/nutrition/alternative", tags=["Nutrition"], response_model=Alternatives)
async def create_alternative(alternatives: Alternatives):
    try:
        nutrition = resource.nutrition_client.post(f"nutrition/alternative", alternatives.dict())
        print("ingredient: ", nutrition)
        return nutrition["data"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/composite/nutrition/ingredient", tags=["Nutrition"], response_model=Nutrition)
async def create_nutrition(nutrition: Nutrition):
    try:
        nutrition = resource.nutrition_client.post(f"nutrition/ingredient", nutrition.dict())
        print("recipe: ", nutrition)
        return nutrition["data"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/composite/nutrition/", tags=["Nutrition"], response_model=Nutrition)
# async def get_all_nutrition():
#     try:
#         nutrition = resource.nutrition_client.get(f"nutrition/")
#         # print(nutrition)
#         # return nutrition["data"]
#         return nutrition
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

# @router.post("/composite/nutrition/alternative", tags=["Nutrition"], response_model=Nutrition)
# async def create_nutrition(nutrition: Nutrition):
#     try:
#         nutrition = resource.nutrition_client.post(f"nutrition/", nutrition.dict())
#         print(nutrition)
#         return nutrition["data"]
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    

    

@router.put("/composite/nutrition/{ingredient_id}", tags=["Nutrition"], response_model=Nutrition)
async def update_nutrition(ingredient_id: int, nutrition: Nutrition):
    try:
        # Send the PUT request to the nutrition microservice
        response = resource.nutrition_client.put(f"nutrition/{ingredient_id}", nutrition.dict())

        # Extract the data from the response and structure it into the appropriate format
        # nutrition_data = response["data"][0]  # Assuming the data is a list, take the first item
        return response["data"]
        # # Map the response data to the Nutrition model
        # updated_nutrition = Nutrition(
        #     recipe_id=nutrition_data[1],  # Example: assuming the first element is the id
        #     calories=nutrition_data[2],
        #     carbohydrates=nutrition_data[3],
        #     protein=nutrition_data[4],
        #     fiber=nutrition_data[5],
        #     fat=nutrition_data[6],
        #     sugar=nutrition_data[7],
        #     sodium=nutrition_data[8]
        # )

        # return updated_nutrition  # Return the structured Nutrition object
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/composite/nutrition/{ingredient_id}", tags=["Nutrition"])
async def delete_nutrition(ingredient_id: int):
    try:
        # Perform delete operation for the nutrition data
        response = resource.nutrition_client.delete(f"nutrition/{ingredient_id}")
        return {"message": "Nutrition data deleted successfully", "recipe_id": ingredient_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# OLD NUTRITION
# @router.get("/composite/nutrition/{nutrition_id}", tags=["Nutrition"])
# async def get_nutrition(nutrition_id: int):
#     try:
#         nutrition_info = resource.nutrition_client.get(f"nutrition/{nutrition_id}")
#         return nutrition_info
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
# @router.get("/composite/nutrition/recipe/{recipe_id}", tags=["Nutrition"])
# async def get_nutrition_from_recipe(recipe_id: int):
#     try:
#         nutrition_info = resource.nutrition_client.get(f"nutrition/recipe/{recipe_id}")
#         return nutrition_info
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    


    
@router.post("/composite/nutrition/callback", tags=["Nutrition"])
async def nutrition_creation_callback(data: dict):
    # print("In callback")
    # Store or process the created nutrition data as needed
    created_nutrition = data.get("data")
    
    # print(created_nutrition)
    # Additional handling (e.g., updating a database, notifying the user)
    return {"message": "Callback received", "data": created_nutrition}


@router.post("/composite/nutrition/async", tags=["Nutrition"])
async def create_nutrition_async(nutrition: Nutrition):
    callback_url = "http://0.0.0.0:5006/composite/nutrition/callback"
    # Issue: Not properly sending back the data 

    try:
        # Add callback_url to the request body instead of params
        payload = nutrition.dict()
        payload["callback_url"] = callback_url
        print(payload)
        
        response = resource.nutrition_client.post(
            "nutrition/async",
            payload  # This includes both nutrition data and callback URL in the body
        )
        
        # print("Response:", response)
        return {"task_id": response.get("task_id")}
    except Exception as e:
        print("Exception occurred:", e)
        raise HTTPException(status_code=500, detail=str(e))

# @router.put("/composite/nutrition/{nutrition_id}", tags=["Nutrition"], response_model=Nutrition)
# async def update_nutrition(nutrition_id: int, nutrition: Nutrition):
#     try:
#         # Send the PUT request to the nutrition microservice
#         response = resource.nutrition_client.put(f"nutrition/{nutrition_id}", nutrition.dict())

#         # Extract the data from the response and structure it into the appropriate format
#         nutrition_data = response["data"][0]  # Assuming the data is a list, take the first item

#         # Map the response data to the Nutrition model
#         updated_nutrition = Nutrition(
#             recipe_id=nutrition_data[1],  # Example: assuming the first element is the id
#             calories=nutrition_data[2],
#             carbohydrates=nutrition_data[3],
#             protein=nutrition_data[4],
#             fiber=nutrition_data[5],
#             fat=nutrition_data[6],
#             sugar=nutrition_data[7],
#             sodium=nutrition_data[8],
#             ingredient_alternatives=nutrition_data[9],
#             diet_type=nutrition_data[10],
#             goal=nutrition_data[11]
#         )

#         return updated_nutrition  # Return the structured Nutrition object
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



# @router.get("/composite/mealplans/{mealplan_id}", tags=["Meal Plans"])
# async def get_mealplan(mealplan_id: int) -> Mealplan:
#     try:
#         mealplan = resource.mealplan_client.get(f"/mealplans/{mealplan_id}")
#         return mealplan
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))


# @router.get("/composite/mealplans/{mealplan_id}")
# async def get_mealplans(request: Request,mealplan_id: int):
#     print("composite called")
#     user_id = request.state.user_id
#     token = request.headers.get("Authorization")  # Extract the Authorization token
#     print("user id: ", user_id)
#     print("Authorization token: ", token)

#     try:
#         # Pass the `user_id` and `Authorization` token to the mealplan client
#         headers = {"Authorization": token}  # Forward the token in the headers
#         mealplans = resource.mealplan_client.get(f"mealplans/{mealplan_id}", headers=headers)
#         return mealplans
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




@router.get("/composite/mealplans", tags=["Meal Plans"])
async def get_all_mealplans(request: Request):

    try:
        # Pass the `user_id` to the mealplan client
        # mealplans = resource.mealplan_client.get(f"mealplans/{user_id}/{meal_id}")
        mealplans = resource.mealplan_client.get(f"mealplans")
        return mealplans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mealplan Functions
@router.get("/composite/mealplans/{meal_id}", tags=["Meal Plans"])
async def get_mealplans(request: Request, meal_id: int):
    # user_id = request.state.user_id
    # print("user id: ", user_id)
    try:
        # Pass the `user_id` to the mealplan client
        # mealplans = resource.mealplan_client.get(f"mealplans/{user_id}/{meal_id}")
        mealplans = resource.mealplan_client.get(f"mealplans/{meal_id}")
        print(mealplans)
        return mealplans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/composite/mealplans/", tags=["Meal Plans"], response_model=Mealplan)
async def create_mealplan(mealplan: Mealplan):
    try:
        mealplan = resource.mealplan_client.post(f"mealplans/", mealplan.dict())
        return mealplan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/composite/mealplans/{meal_id}", tags=["Meal Plans"], response_model=Mealplan)
async def update_mealplan(meal_id: int, mealplan: Mealplan):
    try:
        mealplan = resource.mealplan_client.put(f"mealplans/{meal_id}", mealplan.dict())
        return mealplan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/composite/mealplans/{meal_id}", tags=["Meal Plans"])
async def delete_mealplan(meal_id: int):
    try:
        # Perform delete operation for the meal plan
        response = resource.mealplan_client.delete(f"mealplans/{meal_id}")
        return {"message": "Meal plan deleted successfully", "meal_id": meal_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ---------------- Daily Functions
@router.get("/composite/daily-mealplans/{day_plan_id}", tags=["Meal Plans"])
async def get_daily_mealplans(request: Request, day_plan_id: int):
    # user_id = request.state.user_id
    # print("user id: ", user_id)
    try:
        # Pass the `user_id` to the mealplan client
        # mealplans = resource.mealplan_client.get(f"mealplans/{user_id}/{meal_id}")
        mealplans = resource.mealplan_client.get(f"daily-mealplans/{day_plan_id}")
        print(mealplans)
        return mealplans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/composite/daily-mealplans", tags=["Meal Plans"])
async def create_daily_mealplan(daily_mealplan: DailyMealplan):
    try:
        mealplan = resource.mealplan_client.post(f"daily-mealplans", daily_mealplan.dict())
        return mealplan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.put("/composite/daily-mealplans/{day_plan_id}", tags=["Meal Plans"])
async def update_daily_mealplan_by_id(day_plan_id: int, daily_mealplan: DailyMealplan):
    try:
        mealplan = resource.mealplan_client.put(f"daily-mealplans/{day_plan_id}", daily_mealplan.dict())
        return mealplan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/composite/daily-mealplans/{day_plan_id}", tags=["Meal Plans"])
async def delete_daily_mealplan(day_plan_id: int):
    try:
        # Perform delete operation for the meal plan
        response = resource.mealplan_client.delete(f"daily-mealplans/{day_plan_id}")
        return {"message": "Meal plan deleted successfully", "day plan": day_plan_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
# ---------------- Weekly Functions

@router.get("/composite/weekly-mealplans/{week_plan_id}/daily-mealplans", tags=["Meal Plans"])
async def get_daily_mealplans_by_week(request: Request, week_plan_id: int):
    # user_id = request.state.user_id
    # print("user id: ", user_id)
    try:
        # Pass the `user_id` to the mealplan client
        # mealplans = resource.mealplan_client.get(f"mealplans/{user_id}/{meal_id}")
        result = resource.mealplan_client.get(f"weekly-mealplans/{week_plan_id}/daily-mealplans")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/composite/weekly-mealplans", tags=["Meal Plans"])
async def get_daily_meal_plans_by_date(request: Request, date: str):
    """
    Fetch daily meal plans by the date passed as a query parameter.
    """
    try:
        # Pass the `date` query parameter to your data service or logic
        result = resource.mealplan_client.get(f"weekly-mealplans?date={date}")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
@router.get("/composite/weekly-mealplans/{week_plan_id}", tags=["Meal Plans"])
async def get_weekly_mealplans(request: Request, week_plan_id: int):
    # user_id = request.state.user_id
    # print("user id: ", user_id)
    try:
        # Pass the `user_id` to the mealplan client
        # mealplans = resource.mealplan_client.get(f"mealplans/{user_id}/{meal_id}")
        mealplans = resource.mealplan_client.get(f"weekly-mealplans/{week_plan_id}")
        return mealplans
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/composite/weekly-mealplans", tags=["Meal Plans"])
async def create_weekly_mealplan(weekly_mealplan: WeeklyMealplan):
    try:
        mealplan = resource.mealplan_client.post(f"weekly-mealplans", weekly_mealplan.dict())
        return mealplan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    


@router.put("/weekly-mealplans/{week_plan_id}", tags=["Meal Plans"])
async def update_weekly_mealplan_by_id(week_plan_id: int, weekly_mealplan: WeeklyMealplan):
    try:
        mealplan = resource.mealplan_client.put(f"weekly-mealplans/{week_plan_id}", weekly_mealplan.dict())
        return mealplan
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/composite/weekly-mealplans/{week_plan_id}", tags=["Meal Plans"])
async def delete_weekly_mealplan_by_id(week_plan_id: int):
    try:
        # Perform delete operation for the meal plan
        response = resource.mealplan_client.delete(f"weekly-mealplans/{week_plan_id}")
        return {"message": "Meal plan deleted successfully", "day plan": week_plan_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    




# # mealplan_router.py
# from fastapi import APIRouter, HTTPException, Query, Request
# from typing import List

# from app.models.composite_model import Mealplan, DailyMealplan, WeeklyMealplan, PaginatedResponse
# from app.resources.composite_resource import MealplanResource
# from app.services.service_factory import ServiceFactory

# router = APIRouter()

# @router.post("/mealplans", tags=["mealplans"], status_code=201, response_model=Mealplan)
# async def create_mealplan(mealplan: Mealplan) -> Mealplan:
#     """
#     Create a new meal plan.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     try:
#         # Log the input for debugging
#         print("Creating new meal plan:", mealplan)
        
#         # Pass the meal plan data to the service for creation
#         new_mealplan = res.create_meal_plan(mealplan)
#         return new_mealplan
#     except HTTPException as e:
#         raise e
#     except Exception as e:
#         print(f"Error in create_mealplan endpoint: {e}")
#         raise HTTPException(status_code=500, detail=f"Failed to create meal plan: {e}")

# @router.get("/mealplans/{meal_id}", tags=["mealplans"], response_model=Mealplan)
# async def get_mealplan_by_id(meal_id: int) -> Mealplan:
#     """
#     Retrieve a meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     result = res.get_by_key(meal_id, "meal_plans")
#     print(result)

#     if not result:
#         raise HTTPException(status_code=404, detail="Meal plan not found")

#     return result

# @router.put("/mealplans/{meal_id}", tags=["mealplans"], response_model=Mealplan)
# async def update_mealplan_by_id(meal_id: int, mealplan: Mealplan) -> Mealplan:
#     """
#     Update a meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     update_data = mealplan.dict(exclude_unset=True)
#     updated_mealplan = res.update_meal_plan(meal_id, update_data)

#     if not updated_mealplan:
#         raise HTTPException(status_code=404, detail="Meal plan not found")

#     return updated_mealplan

# @router.put("/weekly-mealplans/{week_plan_id}", tags=["weekly-mealplans"], response_model=WeeklyMealplan)
# async def update_weekly_mealplan_by_id(week_plan_id: int, weekly_mealplan: WeeklyMealplan) -> WeeklyMealplan:
#     """
#     Update a meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     update_data = weekly_mealplan.dict(exclude_unset=True)
#     updated_mealplan = res.update_weekly_meal_plan(week_plan_id, update_data)

#     if not updated_mealplan:
#         raise HTTPException(status_code=404, detail="Meal plan not found")

#     return updated_mealplan

# @router.put("/daily-mealplans/{day_plan_id}", tags=["daily-mealplans"], response_model=DailyMealplan)
# async def update_daily_mealplan_by_id(day_plan_id: int, daily_mealplan: DailyMealplan) -> DailyMealplan:
#     """
#     Update a meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     update_data = daily_mealplan.dict(exclude_unset=True)
#     updated_daily_mealplan = res.update_daily_meal_plan(day_plan_id, update_data)

#     if not updated_daily_mealplan:
#         raise HTTPException(status_code=404, detail="Meal plan not found")

#     return updated_daily_mealplan



# @router.delete("/mealplans/{meal_id}", tags=["mealplans"])
# async def delete_mealplan_by_id(meal_id: int):
#     """
#     Delete a meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     res.delete_meal_plan(meal_id)
#     return {"message": f"Meal plan with ID {meal_id} has been deleted"}

# @router.delete("/daily-mealplans/{day_plan_id}", tags=["daily-mealplans"])
# async def delete_daily_mealplan_by_id(day_plan_id: int):
#     """
#     Delete a daily meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     res.delete_daily_meal_plan(day_plan_id)
#     return {"message": f"Meal plan with ID {day_plan_id} has been deleted"}

# @router.delete("/weekly-mealplans/{weekly_meal_id}", tags=["weekly-mealplans"])
# async def delete_weekly_mealplan_by_id(weekly_meal_id: int):
#     """
#     Delete a weekly meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     res.delete_weekly_meal_plan(weekly_meal_id)
#     return {"message": f"Meal plan with ID {weekly_meal_id} has been deleted"}

# @router.post("/weekly-mealplans", tags=["weekly-mealplans"], status_code=201, response_model=WeeklyMealplan)
# async def create_weekly_mealplan(weekly_mealplan: WeeklyMealplan) -> WeeklyMealplan:
#     """
#     Create a new weekly meal plan.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     try:
#         new_weekly_plan = res.create_weekly_meal_plan(weekly_mealplan)
#         return new_weekly_plan
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create weekly meal plan: {e}")

# @router.get("/weekly-mealplans/{week_plan_id}", tags=["weekly-mealplans"], response_model=WeeklyMealplan)
# async def get_weekly_mealplan_by_id(week_plan_id: int) -> WeeklyMealplan:
#     """
#     Retrieve a weekly meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     result = res.get_by_key(week_plan_id, "weekly_meal_plans")

#     if not result:
#         raise HTTPException(status_code=404, detail="Weekly meal plan not found")

#     return result

# @router.post("/daily-mealplans", tags=["daily-mealplans"], status_code=201, response_model=DailyMealplan)
# async def create_daily_mealplan(daily_mealplan: DailyMealplan) -> DailyMealplan:
#     """
#     Create a new daily meal plan.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     try:
#         new_daily_plan = res.create_daily_meal_plan(daily_mealplan)
#         return new_daily_plan
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Failed to create daily meal plan: {e}")

# @router.get("/daily-mealplans/{day_plan_id}", tags=["daily-mealplans"], response_model=DailyMealplan)
# async def get_daily_mealplan_by_id(day_plan_id: int) -> DailyMealplan:
#     """
#     Retrieve a daily meal plan by its ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     result = res.get_by_key(day_plan_id, "daily_meal_plans")

#     if not result:
#         raise HTTPException(status_code=404, detail="Daily meal plan not found")

#     return result

# @router.get("/weekly-mealplans/{week_plan_id}/daily-mealplans", tags=["weekly-mealplans"], response_model=List[DailyMealplan])
# async def get_daily_mealplans_by_week(week_plan_id: int) -> List[DailyMealplan]:
#     """
#     Retrieve all daily meal plans within a weekly plan by the weekly plan ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     daily_mealplans = res.get_daily_meal_plans_by_week(week_plan_id)

#     if not daily_mealplans:
#         raise HTTPException(status_code=404, detail="No daily meal plans found for this weekly plan")

#     return daily_mealplans

# @router.get("/weekly-mealplans/", tags=["weekly-mealplans"], response_model=List[WeeklyMealplan])
# async def get_daily_meal_plans_by_date(date: str) -> List[DailyMealplan]:
#     """
#     Retrieve all daily meal plans within a weekly plan by the weekly plan ID.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     daily_mealplans = res.get_daily_meal_plans_by_date(date)
#     print("DAILY: ", daily_mealplans)

#     if not daily_mealplans:
#         raise HTTPException(status_code=404, detail="No daily meal plans found for this weekly plan")

#     return daily_mealplans

# @router.get("/mealplans", tags=["mealplans"], response_model=PaginatedResponse)
# async def get_all_mealplans(
#     request: Request,
#     skip: int = Query(0, ge=0, description="Number of records to skip"),
#     limit: int = Query(10, ge=1, le=100, description="Number of records to retrieve")
# ) -> PaginatedResponse:
#     """
#     Retrieve all meal plans with pagination.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     mealplans = res.get_all_meal_plans(skip=skip, limit=limit)
#     total_count = res.get_total_count()

#     base_url = str(request.url).split('?')[0]
#     links = {
#         "first": {"href": f"{base_url}?skip=0&limit={limit}"},
#         "last": {"href": f"{base_url}?skip={(total_count // limit) * limit}&limit={limit}"}
#     }

#     if skip + limit < total_count:
#         links["next"] = {"href": f"{base_url}?skip={skip + limit}&limit={limit}"}
#     if skip > 0:
#         links["previous"] = {"href": f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"}

#     return PaginatedResponse(items=mealplans, links=links)

# @router.get("/weekly-mealplans", tags=["weekly-mealplans"], response_model=PaginatedResponse)
# async def get_all_weekly_mealplans(
#     request: Request,
#     skip: int = Query(0, ge=0, description="Number of records to skip"),
#     limit: int = Query(10, ge=1, le=100, description="Number of records to retrieve")
# ) -> PaginatedResponse:
#     """
#     Retrieve all meal plans with pagination.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     weekly_mealplans = res.get_all_weekly_meal_plans(skip=skip, limit=limit)
#     total_count = res.get_total_count()

#     base_url = str(request.url).split('?')[0]
#     links = {
#         "first": {"href": f"{base_url}?skip=0&limit={limit}"},
#         "last": {"href": f"{base_url}?skip={(total_count // limit) * limit}&limit={limit}"}
#     }

#     if skip + limit < total_count:
#         links["next"] = {"href": f"{base_url}?skip={skip + limit}&limit={limit}"}
#     if skip > 0:
#         links["previous"] = {"href": f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"}

#     return PaginatedResponse(items=weekly_mealplans, links=links)

# @router.get("/daily-mealplans", tags=["daily-mealplans"], response_model=PaginatedResponse)
# async def get_all_daily_mealplans(
#     request: Request,
#     skip: int = Query(0, ge=0, description="Number of records to skip"),
#     limit: int = Query(10, ge=1, le=100, description="Number of records to retrieve")
# ) -> PaginatedResponse:
#     """
#     Retrieve all meal plans with pagination.
#     """
#     res = ServiceFactory.get_service("MealplanResource")
#     daily_mealplans = res.get_all_daily_meal_plans(skip=skip, limit=limit)
#     total_count = res.get_total_count()

#     base_url = str(request.url).split('?')[0]
#     links = {
#         "first": {"href": f"{base_url}?skip=0&limit={limit}"},
#         "last": {"href": f"{base_url}?skip={(total_count // limit) * limit}&limit={limit}"}
#     }

#     if skip + limit < total_count:
#         links["next"] = {"href": f"{base_url}?skip={skip + limit}&limit={limit}"}
#     if skip > 0:
#         links["previous"] = {"href": f"{base_url}?skip={max(skip - limit, 0)}&limit={limit}"}

#     return PaginatedResponse(items=daily_mealplans, links=links)