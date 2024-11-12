from __future__ import annotations
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class WeeklyMealplan(BaseModel):
    week_plan_id: int
    start_date: str  # Format: YYYY-MM-DD
    end_date: str  # Format: YYYY-MM-DD
    links: Optional[Dict[str, Any]] = Field(None, alias="links")

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "week_plan_id": 1,
                "start_date": "2024-10-01",
                "end_date": "2024-10-07",
                "links": {
                    "self": "/weekly-mealplans/1",
                    "daily_mealplans": "/weekly-mealplans/1/daily-mealplans",
                    "edit": "/weekly-mealplans/1/edit",
                    "delete": "/weekly-mealplans/1/delete"
                }
            }
        }

class DailyMealplan(BaseModel):
    day_plan_id: int
    week_plan_id: int
    date: str  # Format: YYYY-MM-DD
    meal_id: int
    links: Optional[Dict[str, Any]] = Field(None, alias="links")

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "day_plan_id": 1,
                "week_plan_id": 1,
                "date": "2024-10-01",
                "meal_id": 10,
                "links": {
                    "self": "/daily-mealplans/1",
                    "week": "/weekly-mealplans/1",
                    "mealplan": "/mealplans/10",
                    "edit": "/daily-mealplans/1/edit",
                    "delete": "/daily-mealplans/1/delete"
                }
            }
        }

class Mealplan(BaseModel):
    meal_id: int
    breakfast_recipe: Optional[int] = None
    lunch_recipe: Optional[int] = None
    dinner_recipe: Optional[int] = None
    links: Optional[Dict[str, Any]] = Field(None, alias="links")

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "meal_id": 10,
                "breakfast_recipe": 171,
                "lunch_recipe": 180,
                "dinner_recipe": 192,
                "links": {
                    "self": "/mealplans/10",
                    "breakfast_recipe": "/recipes/171",
                    "lunch_recipe": "/recipes/180",
                    "dinner_recipe": "/recipes/192",
                    "edit": "/mealplans/10/edit",
                    "delete": "/mealplans/10/delete"
                }
            }
        }


class Nutrition(BaseModel):
    recipe_id: int
    calories: float
    carbohydrates: float
    protein: float
    fiber: float
    fat: float
    sugar: float
    sodium: float
    ingredient_alternatives: str
    diet_type: str
    goal: str

    class Config:
        schema_extra = {
            "example": {
                "recipe_id": 1,
                "calories": 400,
                "carbohydrates": 45.0,
                "protein": 20.5,
                "fiber": 8.0,
                "fat": 15.0,
                "sugar": 8.0,
                "sodium": 230,
                "ingredient_alternatives": "mayo -> yogurt",
                "diet_type": "high_protein",
                "goal": "general_health"
            }
        }

class Ingredient(BaseModel):
    ingredient_name: str
    quantity: str

class Recipe(BaseModel):
    recipe_id: Optional[int] = None
    name: str
    ingredients: List[Ingredient]
    steps: Optional[str] = None
    time_to_cook: Optional[int] = None
    meal_type: Optional[str] = None
    calories: Optional[int] = None
    rating: Optional[float] = None
    links: Optional[Dict[str, Any]] = Field(None, alias="links")

    class Config:
        json_schema_extra  = {
            "example": {
                "recipe_id": 171,
                "name": "Avocado Toast",
                "ingredients": [
                    {
                        "ingredient_name": "Avocado",
                        "quantity": "1 large"
                    },
                    {
                        "ingredient_name": "Bread",
                        "quantity": "2 slices"
                    },
                    {
                        "ingredient_name": "Lime",
                        "quantity": "1/2"
                    },
                    {
                        "ingredient_name": "Olive oil",
                        "quantity": "1 tbsp"
                    },
                    {
                        "ingredient_name": "Salt",
                        "quantity": "1/4 tsp"
                    }
                ],
                "steps": "1. Toast bread. 2. Mash avocado with lime. 3. Spread on toast and season.",
                "time_to_cook": 10,
                "meal_type": "breakfast",
                "calories": 300,
                "rating": 4.4,
                "links": {
                    "self": {
                        "href": "/recipes/171"
                    },
                    "update": {
                        "href": "/recipes/171",
                        "method": "PUT"
                    },
                    "delete": {
                        "href": "/recipes/171",
                        "method": "DELETE"
                    }
                }
            }
        }

class PaginatedResponse(BaseModel):
    items: List[Any]
    links: Dict[str, Any]

    class Config:
        orm_mode = True
        json_schema_extra = {
            "example": {
                "items": [
                    {"day_plan_id": 1, "week_plan_id": 1, "date": "2024-10-01", "meal_id": 10},
                    {"day_plan_id": 2, "week_plan_id": 1, "date": "2024-10-02", "meal_id": 11}
                ],
                "links": {
                    "self": "/weekly-mealplans/1/daily-mealplans?page=1",
                    "next": "/weekly-mealplans/1/daily-mealplans?page=2",
                    "prev": "/weekly-mealplans/1/daily-mealplans?page=1"
                }
            }
        }
