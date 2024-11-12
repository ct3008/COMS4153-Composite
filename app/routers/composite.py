# composite.py
from fastapi import APIRouter, HTTPException
from app.resources.composite_resource import CompositeResource
from app.models.composite_model import Mealplan, DailyMealplan, WeeklyMealplan, Nutrition, Recipe, PaginatedResponse


router = APIRouter()
resource = CompositeResource(config={})  # Pass actual config if needed

@router.get("/composite/recipes/id/{recipe_id}")
async def get_recipe(recipe_id: int):
    try:
        recipe = resource.recipe_client.get(f"recipes/id/{recipe_id}")
        return recipe
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/composite/nutrition/{nutrition_id}")
async def get_nutrition(nutrition_id: int):
    try:
        nutrition_info = resource.nutrition_client.get(f"nutrition/{nutrition_id}")
        return nutrition_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/composite/mealplan/{mealplan_id}")
async def get_mealplan(mealplan_id: int) -> Mealplan:
    try:
        mealplan = resource.mealplan_client.get(f"/mealplans/{mealplan_id}")
        return mealplan
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