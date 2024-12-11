import pymysql
from .BaseDataService import DataDataService
from typing import Any, List, Optional
from fastapi import HTTPException


class MySQLRDBDataService(DataDataService):
    """
    A generic data service for MySQL databases. The class implement common
    methods from BaseDataService and other methods for MySQL. More complex use cases
    can subclass, reuse methods and extend.
    """

    def __init__(self, context):
        super().__init__(context)

    def _get_connection(self):
        connection = pymysql.connect(
            host=self.context["host"],
            port=self.context["port"],
            user=self.context["user"],
            passwd=self.context["password"],
            cursorclass=pymysql.cursors.DictCursor,
            autocommit=True
        )
        return connection
    
    def get_jwt_token(self, username:str):
        connection = None
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            sql = "SELECT user_id, username, jwt_token FROM `users`.`account` WHERE username = %s"
            print("SQL: ", sql)
            cursor.execute(sql, (username,))
            result = cursor.fetchone()
            if result:
                return result
            return None
        except Exception as e:
            print(f"Error in get_jwt_token: {e}")
            raise e
        finally:
            if connection:
                connection.close()


    def update_jwt_token(self, user_id: int, new_jwt_token: str):
        connection = None
        try:
            connection = self._get_connection()
            cursor = connection.cursor()

            # Use parameterized queries to avoid SQL injection
            sql = """
                UPDATE `users`.`account` 
                SET jwt_token = %s
                WHERE user_id = %s
            """

            print("JWT TOKEN NEW SQL: ", new_jwt_token, len(new_jwt_token))
            cursor.execute(sql, (new_jwt_token, user_id))  # Pass parameters to avoid SQL injection
            
            # Commit the transaction to save the changes
            connection.commit()

            # Check if any row was updated
            if cursor.rowcount > 0:
                return {"message": "JWT token updated successfully"}
            else:
                return {"message": "No matching user found, token not updated"}
        except Exception as e:
            print(f"Error in updating JWT token: {e}")
            raise e
        finally:
            if connection:
                connection.close()
        

    def get_total_count(self, database_name: str, collection_name: str) -> int:
        connection = None
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            sql = f"SELECT COUNT(*) as count FROM `{database_name}`.`{collection_name}`"
            cursor.execute(sql)
            result = cursor.fetchone()
            if result:
                return result["count"]
            return 0
        except Exception as e:
            print(f"Error in get_total_count: {e}")
            raise e
        finally:
            if connection:
                connection.close()

    def get_data_object(self, database_name: str, collection_name: str, key_field: str, key_value: any):
        connection = None
        result = None
        
        try:
            if collection_name == "meal_plans":
                sql_statement = f"""
                    SELECT m.meal_id, m.breakfast_recipe, m.lunch_recipe, m.dinner_recipe
                    FROM `{database_name}`.`{collection_name}` m
                    WHERE m.{key_field}=%s
                """
                
            elif collection_name == "weekly_meal_plans":
                sql_statement = f"""
                    SELECT w.week_plan_id, w.start_date, w.end_date
                    FROM `{database_name}`.`{collection_name}` w
                    WHERE w.{key_field}=%s
                """
                
            elif collection_name == "daily_meal_plans":
                sql_statement = f"""
                    SELECT d.day_plan_id, d.week_plan_id, d.date, d.meal_id
                    FROM `{database_name}`.`{collection_name}` d
                    WHERE d.{key_field}=%s
                """
            
            else:
                raise ValueError("Invalid collection name")

            connection = self._get_connection()
            cursor = connection.cursor()  # Use dictionary cursor for easier row handling
            cursor.execute(sql_statement, [key_value])
            row = cursor.fetchone()

            if row:
                # Structure data based on the collection
                if collection_name == "meal_plans":
                    result = {
                        "meal_id": row["meal_id"],
                        "breakfast_recipe": row["breakfast_recipe"],
                        "lunch_recipe": row["lunch_recipe"],
                        "dinner_recipe": row["dinner_recipe"]
                    }
                elif collection_name == "weekly_meal_plans":
                    result = {
                        "week_plan_id": row["week_plan_id"],
                        "start_date": row["start_date"].isoformat(),
                        "end_date": row["end_date"].isoformat()
                    }
                elif collection_name == "daily_meal_plans":
                    result = {
                        "day_plan_id": row["day_plan_id"],
                        "week_plan_id": row["week_plan_id"],
                        "date": row["date"].isoformat(),
                        "meal_id": row["meal_id"]
                    }

        except Exception as e:
            print(f"An error occurred: {e}")
            if connection:
                connection.close()
            raise
        finally:
            if connection:
                connection.close()

        return result


    def get_all_data(self, database_name: str, collection_name: str, skip: int = 0, limit: int = 10, filters: Optional[dict] = None) -> list[dict]:
        """
        Retrieve all data objects from the specified database and collection/table with pagination,
        including related ingredients.
        """
        connection = None
        results = []

        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            

            if collection_name == "weekly_meal_plans":
                mealplan_sql = (
                    f"SELECT m.week_plan_id, m.start_date, m.end_date "
                    f"FROM `{database_name}`.`{collection_name}` m "
                )
            elif collection_name == "meal_plans":
                mealplan_sql = (
                    f"SELECT m.meal_id, m.breakfast_recipe, m.lunch_recipe, m.dinner_recipe "
                    f"FROM `{database_name}`.`{collection_name}` m "
                )
            elif collection_name == "daily_meal_plans":
                mealplan_sql = (
                    f"SELECT m.day_plan_id, m.week_plan_id, m.date, m.meal_id "
                    f"FROM `{database_name}`.`{collection_name}` m "
                )

            if filters:
                filter_conditions = " AND ".join(
                    f"{field} = %s" for field in filters.keys()
                )
                mealplan_sql += f"WHERE {filter_conditions} "

            mealplan_sql += "LIMIT %s OFFSET %s "

            values = list(filters.values()) if filters else []
            values.extend([limit, skip])
            # print(f"{mealplan_sql}",values)



            
            cursor.execute(mealplan_sql, values)
            mealplans = cursor.fetchall()

            if not mealplans:
                return []
            return mealplans


        except Exception as e:
            print(f"Error in get_all_data: {e}")
            if connection:
                connection.rollback()
        finally:
            if connection:
                connection.close()

        return results

    def update_data(self, database_name: str, collection_name: str, data: dict, key_field: str, key_value: any):
        """
        Update a data object in the specified database and collection/table.
        """
        connection = None
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            connection.begin()

            # Remove non-serializable fields
            data.pop('links', None)
            
            # Handle updating logic based on collection type
            if collection_name == 'weekly_meal_plans':
                print(data)
                # For weekly_meal_plans, remove unsupported fields
                data.pop('week_plan_id', None)

            elif collection_name == 'daily_meal_plans':
                # For daily_meal_plans, remove unsupported fields
                data.pop('day_plan_id', None)

            elif collection_name == 'meal_plans':
                # For meal_plans, remove unsupported fields
                data.pop('meal_id', None)

            # Convert data to be updated into SQL set clause
            set_clause = ", ".join([f"`{field}`=%s" for field in data.keys()])
            sql_statement = f"UPDATE `{database_name}`.`{collection_name}` SET {set_clause} WHERE `{key_field}`=%s"
            values = list(data.values()) + [key_value]

            # Execute update statement
            print("Data before SQL execution:", data)
            print("Values before SQL execution:", values)
            cursor.execute(sql_statement, values)
            print(f"Updated {collection_name} table for {key_field}={key_value}")

            connection.commit()
            print("Transaction committed successfully.")

        except Exception as e:
            print(f"Error in update_data: {e}")
            if connection:
                connection.rollback()
                print("Transaction rolled back due to error.")
            raise HTTPException(status_code=500, detail="Failed to update record.")
        finally:
            if connection:
                connection.close()
                print("Database connection closed.")


    def delete_data(self, database_name: str, collection_name: str, key_field: str, key_value: any):
        """
        Delete a data object from the specified database and collection/table,
        including any related data such as nutrition information, ingredients, or daily meal plans.
        """

        connection = None
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            connection.begin()

            # Determine related data handling based on collection name
            if collection_name == 'weekly_meal_plans':
                # Delete associated daily meal plans first
                delete_daily_plans_sql = f"DELETE FROM `{database_name}`.`daily_meal_plans` WHERE `{key_field}`=%s"
                cursor.execute(delete_daily_plans_sql, [key_value])
                print(f"Deleted daily meal plans for week_plan_id={key_value}")

            elif collection_name == 'daily_meal_plans':
                # Delete associated meal if `meal_id` exists in `daily_meal_plans`
                select_meal_id_sql = f"SELECT `meal_id` FROM `{database_name}`.`{collection_name}` WHERE `{key_field}`=%s"
                cursor.execute(select_meal_id_sql, [key_value])
                meal_id_result = cursor.fetchone()

                if meal_id_result:
                    meal_id = meal_id_result['meal_id']
                    delete_meal_sql = f"DELETE FROM `{database_name}`.`meal_plans` WHERE `meal_id`=%s"
                    cursor.execute(delete_meal_sql, [meal_id])
                    print(f"Deleted meal with meal_id={meal_id}")

            elif collection_name == 'meal_plans':                
                delete_mealplan_sql = f"DELETE FROM `{database_name}`.`{collection_name}` WHERE `{key_field}`=%s"
                cursor.execute(delete_mealplan_sql, [key_value])
                print(f"Deleted meal plan with {key_field}={key_value}")
            delete_main_record_sql = f"DELETE FROM `{database_name}`.`{collection_name}` WHERE `{key_field}`=%s"
            cursor.execute(delete_main_record_sql, [key_value])
            print(f"Deleted record with {key_field}={key_value} from {collection_name}.")

            # Commit the transaction
            connection.commit()
            print("Transaction committed successfully.")

        except Exception as e:
            print(f"Error in delete_data: {e}")
            if connection:
                connection.rollback()
                print("Transaction rolled back due to error.")
            raise HTTPException(status_code=500, detail="Failed to delete record.")
        finally:
            if connection:
                connection.close()
                print("Database connection closed.")


    def insert_data(self, database_name: str, collection_name: str, data: dict):
        """
        Insert a new meal plan into the database.
        """
        connection = None
        try:
            connection = self._get_connection()
            cursor = connection.cursor()
            connection.begin()

            # Remove any non-serializable fields if they exist
            data.pop('links', None)

            # Prepare the fields and values for insertion
            fields = ', '.join([f"`{field}`" for field in data.keys()])
            placeholders = ', '.join(['%s'] * len(data))
            insert_sql = f"INSERT INTO `{database_name}`.`{collection_name}` ({fields}) VALUES ({placeholders})"
            # Execute the insertion
            cursor.execute(insert_sql, list(data.values()))
            # meal_id = cursor.lastrowid
            # print(f"Inserted meal plan with ID {meal_id} into '{collection_name}' table.")

            connection.commit()
            # print("Transaction committed successfully.")

            # Include the generated `meal_id` in the response data
            # data['meal_id'] = meal_id
            return data

        except pymysql.err.IntegrityError as e:
            print(f"Integrity error in insert_data: {e}")
            if connection:
                connection.rollback()
                print("Transaction rolled back due to integrity error.")
            raise HTTPException(status_code=400, detail="Integrity error: Invalid meal plan data.")
        except Exception as e:
            print(f"Error in insert_data: {e}")
            if connection:
                connection.rollback()
                print("Transaction rolled back due to error.")
            raise HTTPException(status_code=500, detail="Failed to insert meal plan.")
        finally:
            if connection:
                connection.close()
                print("Database connection closed.")


    def get_daily_meal_plans_by_date(self, date: str):
        """
        Fetches daily meal plans based on the weekly plan ID.
        """
        
        cursor = self.data_service.connection.cursor()
        query1 = """
        SELECT wmp.*
        FROM weekly_meal_plans wmp
        JOIN daily_meal_plans dmp ON wmp.week_plan_id = dmp.week_plan_id
        WHERE dmp.date = %s;
        """
        cursor.execute(query1, (date,))
        weekly_meal_plans = cursor.fetchall()

        # Get column names for the weekly meal plans
        weekly_column_names = [column[0] for column in cursor.description]
        weekly_result = [dict(zip(weekly_column_names, row)) for row in weekly_meal_plans]

        # Second query to get meal ids and related recipes
        query2 = """
            SELECT 
                dmp.date,
                recipes_breakfast.name AS breakfast_recipe,
                recipes_lunch.name AS lunch_recipe,
                recipes_dinner.name AS dinner_recipe
            FROM mealplan_db.meal_plans
            JOIN mealplan_db.daily_meal_plans dmp ON dmp.meal_id = meal_plans.meal_id
            LEFT JOIN recipes_database.recipes AS recipes_breakfast ON meal_plans.breakfast_recipe = recipes_breakfast.recipe_id
            LEFT JOIN recipes_database.recipes AS recipes_lunch ON meal_plans.lunch_recipe = recipes_lunch.recipe_id
            LEFT JOIN recipes_database.recipes AS recipes_dinner ON meal_plans.dinner_recipe = recipes_dinner.recipe_id
            WHERE dmp.date = %s;
        """
        
        cursor.execute(query2, (date,))
        meals = cursor.fetchall()

        # Get column names for meals
        meals_column_names = [column[0] for column in cursor.description]
        meals_result = [dict(zip(meals_column_names, row)) for row in meals]

        # Combine results into a single response object
        combined_results = {
            "weekly_meal_plan": weekly_result,
            "meals": meals_result
        }
        # cursor.execute(query, (week_plan_id,))
        # daily_mealplans = cursor.fetchall()

        # Fetch column names for the result mapping
        # column_names = [column[0] for column in cursor.description]
        # daily_mealplans_result = [dict(zip(column_names, row)) for row in daily_mealplans]

        cursor.close()
        return combined_results

