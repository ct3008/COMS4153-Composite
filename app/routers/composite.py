# composite.py
from fastapi import APIRouter, HTTPException, Request, Query, Response, BackgroundTasks
from app.resources.composite_resource import CompositeResource
from app.models.composite_model import Mealplan, DailyMealplan, WeeklyMealplan, Nutrition, Recipe, PaginatedResponse, Alternatives
from app.services.service_factory import ServiceFactory
from typing import Optional
from enum import Enum
import boto3
import json
import asyncio
import requests
from typing import Dict, List
from fastapi import FastAPI, HTTPException, APIRouter, Depends
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
# fake_user_db = {
#     "ct3008": {"user_id": 1, "username": "ct3008", "password": "password"}
# }

# Initialize the SNS client
sns_client = boto3.client("sns", region_name="us-east-1")
lambda_client = boto3.client("lambda", region_name="us-east-1")

# ARN for your SNS topic
RECIPE_ALERT_SNS_ARN = "arn:aws:sns:us-east-1:108782072640:RecipeCreatedAlert"

class LoginRequest(BaseModel):
    username: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DietType(str, Enum):
    high_protein = "high protein"
    gluten_free = "gluten free"
    low_carb = "low carb"
    vegan = "vegan"
    keto = "keto"
    low_sodium = "low sodium"
    vegetarian = "vegetarian"
    paleo = "paleo"

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
    # jwt_token = "invalid"

    user["jwt_token"] = jwt_token
    # print("jwt token: ", jwt_token)

    return {"access_token": jwt_token, "token_type": "bearer"}

# @router.get("/composite/step")
# async def get_recipe(recipe_id: int):

#     step_functions_client = boto3.client('stepfunctions')

#     # ARN of your Step Function
#     state_machine_arn = "arn:aws:states:us-east-1:108782072640:stateMachine:MyStateMachine-cnz0373nu"
    
#     print("start executing")
#     # Start execution of the Step Function
#     response = step_functions_client.start_execution(
#         stateMachineArn=state_machine_arn,  # ARN of the Step Function execution
#         input=json.dumps({})  # Convert payload to JSON format
#     )

#     # Return the execution ARN from the response
#     execution_arn = response['executionArn']
#     print(f"Step Function execution started: {execution_arn}")

#     return execution_arn

def lambda_handler(event, context=None):
    # URL of the API you want to call
    try:
        date = json.loads(event).get('date')
        api_url = json.loads(event).get('mealplan_api_url')
        if not date:
            return {
                'statusCode': 400,
                'body': json.dumps({'message': 'Date is required'})
            }
        # print(date)
        # api_url = "http://0.0.0.0:5002"
        # KNOW THAT WE NEED TO PASS IN THE URL TO THE LAMBDA FUNCS FROM THE CHOSEN_MEALPLAN_URL IN REAL USE
        
        # GET WEEK PLAN ID THAT DATE IS FOUND IN

        # result = requests.get(f"{api_url}/weekly-mealplans?date={date}")
        # if result.status_code == 200:
        #     result = result.json() 
        
        result = {"weekly_meal_plan":[{"week_plan_id":1,"start_date":"2024-12-09","end_date":"2024-12-15"}],"meals":[{"date":"2024-12-10","meal_id":2,"breakfast_recipe":"BBQ Ribs","lunch_recipe":"Omelette","dinner_recipe":"Veggie Burger","breakfast_id":14,"lunch_id":33,"dinner_id":37}],"daily_mealplan":[{"day_plan_id":3}]}
        
        # print("associated data for daily meal: ", result)
        week_plan_id = result["weekly_meal_plan"][0]["week_plan_id"]
        # print("week_plan_id: ",week_plan_id)

        # GET MEAL_IDS FROM DAILY MEALS IN WEEK
        
        # result = requests.get(f"{api_url}/weekly-mealplans/{week_plan_id}/daily-mealplans")
        # if result.status_code == 200:
        #     result = result.json()
        result = [{"day_plan_id":1,"week_plan_id":1,"date":"2024-12-08","meal_id":1,"links":None},{"day_plan_id":2,"week_plan_id":1,"date":"2024-12-09","meal_id":1,"links":None},{"day_plan_id":3,"week_plan_id":1,"date":"2024-12-10","meal_id":2,"links":None},{"day_plan_id":4,"week_plan_id":1,"date":"2024-12-11","meal_id":3,"links":None},{"day_plan_id":5,"week_plan_id":1,"date":"2024-12-12","meal_id":7,"links":None}]
        
        
        # print(result[0])
        meal_ids = {}

        for item in result:
            # print("item:", item)
            meal_id = item.get('meal_id')
            try:
                meal_ids[meal_id]
                meal_ids[meal_id] += 1
            except:
                meal_ids[meal_id] = 1
            

        # print("meal_ids: ", meal_ids)
        
        # GET RECIPE IDS
        recipe_ids = {}
        for meal_id in meal_ids:
            multi = meal_ids[meal_id]
            result = requests.get(f"{api_url}/mealplans/{meal_id}")
            if result.status_code == 200:
                result = result.json()
            # print('result:', result)
            breakfast_id = result["breakfast_recipe"]
            lunch_id = result["lunch_recipe"]
            dinner_id = result["dinner_recipe"]
            # print(breakfast_id, lunch_id, dinner_id)
            try:
                recipe_ids[breakfast_id]
                recipe_ids[breakfast_id] += multi*1
            except:
                recipe_ids[breakfast_id] = multi*1
            try:
                recipe_ids[lunch_id]
                recipe_ids[lunch_id] += multi*1
            except:
                recipe_ids[lunch_id] = multi*1

            try:
                recipe_ids[dinner_id]
                recipe_ids[dinner_id] += multi*1
            except:
                recipe_ids[dinner_id] = multi*1
            
        # print("recipe ids: ", recipe_ids)
        # Check if the response is successful (status code 200)
        
        payload =  {'statusCode': 200, 'body': json.dumps(recipe_ids)}
        return json.dumps(payload)
    except Exception as e:
        print("e")
        return {'statusCode': 400, 'body': str(e)} 



def lambda_handler2(event, context=None):
    # Step 1: Extract the body from the event and load it as a Python dictionary
    # print(event)
    print("event: ", event)
    recipe_data = json.loads(json.loads(event)['body'])  # event['body'] contains the raw JSON string
    print(recipe_data)

    # api_url = "https://sunny-truth-444203-c0.ue.r.appspot.com/recipes/id"
    api_url  = 'http://0.0.0.0:8000'
    ingredient_amounts = {}
    try:
        
        for recipe_id in recipe_data:
            # print("recipe id: ", recipe_id)
            multi = recipe_data[recipe_id]
            result = requests.get(f"{api_url}/recipes/id/{recipe_id}")
            if result.status_code == 200:
                result = result.json()
            ingredients = result.get('ingredients')
            
            for ingredient in ingredients:
                # print("ingredient:", ingredient)
                name = ingredient.get('ingredient_name')
                try:
                    og_amt, og_unit = ingredient_amounts[name].split(' ')
                    amt, unit = ingredient.get('quantity').split(' ')
                    
                    # print("Values: ", og_amt, og_unit, amt, unit)
                    if '/' in og_amt:
                        # print("og split")
                        num, denom = og_amt.split('/')
                        og_amt = round(float(num) / float(denom), 2)
                    if '/' in amt:
                        # print("new split")
                        num,denom =amt.split('/')
                        amt = round(float(num)/float(denom),2)
                    print("new amt: ", og_amt,amt,og_unit)
                    og_amt = float(og_amt)
                    amt = float(amt)
                    new_total = og_amt + (amt*multi)
                    ingredient_amounts[name] = f"{new_total} {og_unit}"
                    # print(f"---------------normal: {ingredient_amounts}----------------")
                except:
                    amt, unit = ingredient.get('quantity').split(' ')
                    # print("EXCEPT amt unit", amt, unit)
                    if '/' in amt:
                        # print("EXCEPT div new new")
                        num, denom = amt.split('/')
                        amt = round(float(num)/float(denom),2)
                    amt = float(amt)
                    new_amt = multi * amt
                    ingredient_amounts[name] = f"{new_amt} {unit}"
                    # print(f"---------------new: {ingredient_amounts}----------------")
        # print("final ingredient amount: ", ingredient_amounts)
        
        # return {'statusCode': 200, 'body': ingredient_amounts}
        return {'statusCode': 200, 'body': json.dumps(ingredient_amounts)}
        print("After return?")

    except Exception as e: 
        return {'statusCode': 400, 'body': str(e)}

@router.get("/composite/step")
async def stepfunction_ingredient_list(date: str):
    print("deployed urls: ", resource.chosen_recipe_url, resource.chosen_mealplan_url, resource.chosen_nutrition_url)
    if "0.0.0.0" in resource.chosen_recipe_url or "0.0.0.0" in resource.chosen_mealplan_url:
        print("failed connection to deployed url: ", resource.chosen_recipe_url, resource.chosen_mealplan_url)
        # payload=json.dumps({"date": date, "mealplan_api_url": resource.chosen_mealplan_url, "recipe_api_url": resource.chosen_recipe_url})
        # result = lambda_handler(payload)
        # result2 = lambda_handler2(result)
        # print("Final result: ", result2)
        # # result_done = json.loads(result2)
        # result_done = result2["body"]
        
        # return {"status": "SUCCEEDED", "output": result2}
        payload = json.dumps({"date": date, "mealplan_api_url": resource.chosen_mealplan_url, "recipe_api_url": resource.chosen_recipe_url})
        result = lambda_handler(payload)
        result2 = lambda_handler2(result)
        # print("result: ", result2)

        result_done = json.loads(result2["body"])  # Parse the final result body
        # print("result_done: ", result_done)
        return {"status": "SUCCEEDED", "output": {"Payload": {"body": json.dumps(result_done)}}}
    else:
        step_functions_client = boto3.client('stepfunctions',region_name='us-east-1')

        # ARN of your Step Function
        state_machine_arn = "arn:aws:states:us-east-1:108782072640:stateMachine:MyStateMachine-cnz0373nu"

        print("Starting Step Function execution...")
        # Start execution of the Step Function
        response = step_functions_client.start_execution(
            stateMachineArn=state_machine_arn,
            input=json.dumps({"date": date, "mealplan_api_url": resource.chosen_mealplan_url, "recipe_api_url": resource.chosen_recipe_url})  # Pass the recipe_id to the Step Function
        )

        execution_arn = response['executionArn']
        print(f"Step Function execution started: {execution_arn}")

        # Poll for execution status asynchronously
        while True:
            status_response = step_functions_client.describe_execution(
                executionArn=execution_arn
            )
            status = status_response['status']
            print(f"Current status: {status}")

            if status == "SUCCEEDED":
                # Get the output when the execution is complete
                output = status_response.get("output")
                print("Execution succeeded!")
                # print(json.loads(output))
                return {"status": "SUCCEEDED", "output": json.loads(output)}
            elif status in ["FAILED", "TIMED_OUT", "ABORTED"]:
                print(f"Execution ended with status: {status}")
                return {"status": status, "message": "Execution did not complete successfully."}

            # Wait asynchronously for 5 seconds before polling again
            await asyncio.sleep(5)

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

def pub_sub_update(recipe):
    
    ingredients = recipe.get("ingredients", [])
    if not ingredients:
        print("No ingredients found in recipe.")
        return
    nutritions = {}
    all_alternatives = {}

    for item in ingredients:
        ingredient_id = item.get('ingredient_id')
        print("Processing ingredient_id: ", ingredient_id)

        if not ingredient_id:
            continue

        # Fetch mixed data for the ingredient
        mixed_data = resource.nutrition_client.get(f"nutrition/duplicates/{ingredient_id}")
        print(f"Fetched mixed data for ingredient_id {ingredient_id}:", mixed_data)
        if mixed_data:
            temp_ingredient_id = mixed_data[0].get('ingredient_id')
        else:
            continue

        # Filter out nutrition data (unique rows by ingredient_id)
        nutrition_data = next(
            (entry for entry in mixed_data if entry.get("ingredient_id") == temp_ingredient_id),
            None
        )
        if not nutrition_data:
            print(f"No nutrition data found for ingredient_id {temp_ingredient_id}")
            continue
        
        nutrition_data = {
            "ingredient_id": ingredient_id,
            "calories": nutrition_data.get("nutrition_calories"),
            "carbohydrates": nutrition_data.get("nutrition_carbohydrates"),
            "protein": nutrition_data.get("nutrition_protein"),
            "fiber": nutrition_data.get("nutrition_fiber"),
            "fat": nutrition_data.get("nutrition_fat"),
            "sugar": nutrition_data.get("nutrition_sugar"),
            "sodium": nutrition_data.get("nutrition_sodium"),
        }

        nutritions[ingredient_id] = nutrition_data
        nutrition = Nutrition(**nutrition_data)
        
        resource.nutrition_client.post("nutrition/ingredient", data=nutrition.dict())
        print(f"Posted Nutrition data for ingredient_id {ingredient_id}:", nutrition.dict())
        # nutritions[ingredient_id] = nutrition_data

        # Filter and process alternatives for the ingredient
        alternatives = [
            entry for entry in mixed_data
            if entry.get("ingredient_id") == temp_ingredient_id and entry.get("alternative_id")
        ]

        # all_alternatives[ingredient_id] = alternatives
        all_alternatives[ingredient_id] = []
        for alt in alternatives:
            alternative_data_dict = {
                "alternative_id": alt["alternative_id"],
                "ingredient_id": ingredient_id,
                "alternative_name": alt.get("alternative_name"),
                "calories": alt.get("calories"),
                "carbohydrates": alt.get("carbohydrates"),
                "protein": alt.get("protein"),
                "fiber": alt.get("fiber"),
                "fat": alt.get("fat"),
                "sugar": alt.get("sugar"),
                "sodium": alt.get("sodium"),
                "diet_type": alt.get("diet_type"),
            }
            all_alternatives[ingredient_id].append(alternative_data_dict)
            alternative_data = Alternatives(**alternative_data_dict)
            
            resource.nutrition_client.post("nutrition/alternative", data=alternative_data.dict())
            print(f"Posted Alternative data for ingredient_id {ingredient_id}:", alternative_data.dict())

   
    payload = {
        "recipe_id": recipe['recipe_id'],
        "recipe_name": recipe.get('name', 'Unknown Recipe'),
        "ingredients": recipe.get("ingredients", {}),
        "new_nutrition": nutritions,
        "alternatives": all_alternatives
    }
    # print("payload: ", payload)

    try:
        # Invoke the Lambda function
        response = lambda_client.invoke(
            FunctionName="arn:aws:lambda:us-east-1:108782072640:function:recipe_alerts",
            InvocationType="RequestResponse",  # Ensures synchronous invocation
            Payload=json.dumps(payload)
        )
        
        # Process the Lambda response
        lambda_response = json.load(response['Payload'])
        print("Lambda response:", lambda_response)
        
        # Additional fallback SNS notification (optional)
        # message = f"New recipe created: {recipe['name']} (ID: {recipe['recipe_id']})"
        # sns_response = sns_client.publish(
        #     TopicArn=RECIPE_ALERT_SNS_ARN,
        #     Message=message,
        #     Subject="New Recipe Alert"
        # )
        # print("Fallback SNS publish response:", sns_response)
    except Exception as e:
        print("Error invoking Lambda or publishing SNS alert:", e)
    
@router.post("/composite/recipes", tags=["Recipes"], response_model=Recipe)
async def create_recipe(recipe: Recipe):
    try:
        print(recipe)
        recipe = resource.recipe_client.post(f"recipes", recipe.dict())
        pub_sub_update(recipe)
        
        

        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.put("/composite/recipes/id/{recipe_id}", tags=["Recipes"], response_model=Recipe)
async def update_recipe(recipe_id: int, recipe: Recipe):
    print(recipe)
    try:
        print(recipe)
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

@router.get("/composite/nutrition", tags=["Nutrition"])
async def get_ingredient_nutrition(
        response: Response,
        page: int = Query(1, ge=1, description="Page number starting from 1"),
        page_size: int = Query(10, ge=1, description="Number of items per page"),
        min_calories: Optional[float] = Query(None, description="Minimum calorie value"),
        max_calories: Optional[float] = Query(None, description="Maximum calorie value"),
        diet_type: Optional[DietType] = Query(None, description="Diet type filter"),
):
    """
    Proxy for the nutrition endpoint, replicating its functionality.
    """
    try:
        # Build the query parameters dynamically
        query_params = {
            "page": page,
            "page_size": page_size,
        }
        if min_calories is not None:
            query_params["min_calories"] = min_calories
        if max_calories is not None:
            query_params["max_calories"] = max_calories
        if diet_type is not None:
            query_params["diet_type"] = diet_type.value  # Extract enum value

        # Make the request to the underlying nutrition endpoint
        nutrition_info = resource.nutrition_client.get(
            "nutrition", params=query_params
        )
        print("nutrition info: ", nutrition_info)

        # Proxy Link headers for pagination
        # if "Link" in nutrition_info.headers:
        #     response.headers["Link"] = nutrition_info.headers["Link"]

        return nutrition_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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

@router.get("/composite/nutrition/ingredient_name/{ingredient_id}", tags=["Nutrition"])
async def get_ingredient_name(ingredient_id: int):
    try:
        nutrition_info = resource.nutrition_client.get(f"nutrition/ingredient_name/{ingredient_id}")
        print(nutrition_info)
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
    

@router.post("/composite/mealplans", tags=["Meal Plans"], response_model=Mealplan)
async def create_mealplan(mealplan: Mealplan):
    try:
        mealplan = resource.mealplan_client.post(f"mealplans", mealplan.dict())
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

    
@router.get("/composite/mealplans/test/{meal_id}", tags=["mealplans"])
async def test_mealplans_performance(meal_id: int):
    try:
        # Perform delete operation for the meal plan
        response = resource.mealplan_client.get(f"mealplans/test/{meal_id}")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/composite/mealplans/start-task")
async def start_mealplans_task(background_tasks: BackgroundTasks, meal_id: int):
    try:
        # Perform delete operation for the meal plan
        response = resource.mealplan_client.get(f"mealplans/start-task")
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
