import os
import questionary
import sqlite3

from datetime import datetime
from enum import Enum

from rich.console import Console

from todoist.tasks import get_full_label_names


LUNCH_PROJECT_ID = 2321701711
DINNER_PROJECT_ID = 2321953095
NIGHT_PROJECT_ID = 2334412048
SNACKS_BEFORE_LUNCH_PROJECT_ID = 2334492361
SNACKS_AFTER_LUNCH_PROJECT_ID = 2334492378
SNACKS_AFTER_DINNER_PROJECT_ID = 2334492398


class SnackType(Enum):
    BeforeLunch = 1
    AfterLunch = 2
    AfterDinner = 3

    def get_project_id(self):
        project_ids = {
            SnackType.BeforeLunch: SNACKS_BEFORE_LUNCH_PROJECT_ID,
            SnackType.AfterLunch: SNACKS_AFTER_LUNCH_PROJECT_ID,
            SnackType.AfterDinner: SNACKS_AFTER_DINNER_PROJECT_ID
        }
        return project_ids[self]


class MealType(Enum):
    Lunch = 1
    Dinner = 2
    Night = 3

    def get_project_id(self):
        project_ids = {
            MealType.Lunch: LUNCH_PROJECT_ID,
            MealType.Dinner: DINNER_PROJECT_ID,
            MealType.Night: NIGHT_PROJECT_ID,
        }
        return project_ids[self]


class NutritionInfo:
    def __init__(self, calories, protein, fat, carbohydrates, fiber, sugar, salt):
        self.calories = calories
        self.protein = protein
        self.fat = fat
        self.carbohydrates = carbohydrates
        self.fiber = fiber
        self.sugar = sugar
        self.salt = salt

    def __str__(self):
        return (
            f"Calories: {self.calories}\n"
            f"Protein: {self.protein}\n"
            f"Fat: {self.fat}\n"
            f"Carbohydrates: {self.carbohydrates}\n"
            f"Fiber: {self.fiber}\n"
            f"Sugar: {self.sugar}\n"
            f"Salt: {self.salt}\n"
        )


class Meal:
    def __init__(self, id, name, meal_type_id):
        self.id = id
        self.name = name
        self.meal_type = MealType(meal_type_id)
        self.items = []
        self.items_with_quantities = {}

    def add_item(self, item, quantity):
        self.items.append(item)
        self.items_with_quantities[item.id] = quantity

    def get_nutrition_info(self):
        return NutritionInfo(
            sum((item.calories * self.items_with_quantities[item.id] for item in self.items)),
            sum((item.protein * self.items_with_quantities[item.id] for item in self.items)),
            sum((item.fat * self.items_with_quantities[item.id] for item in self.items)),
            sum((item.carbohydrates * self.items_with_quantities[item.id] for item in self.items)),
            sum((item.fiber * self.items_with_quantities[item.id] for item in self.items)),
            sum((item.sugar * self.items_with_quantities[item.id] for item in self.items)),
            sum((item.salt * self.items_with_quantities[item.id] for item in self.items)),
        )

    def save(self, conn):
        cursor = conn.cursor()
        try:
            cursor.execute(
                """
                INSERT INTO meals (name, meal_type_id) 
                VALUES (?, ?)
                """,
                (self.name, self.meal_type.value)
            )
            self.id = cursor.lastrowid

            for item in self.items:
                cursor.execute(
                    """
                    INSERT INTO meals_food_items (meal_id, food_item_id, quantity) 
                    VALUES (?, ?, ?)
                    """,
                    (self.id, item.id, self.items_with_quantities[item.id])
                )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            conn.rollback()
            print("Error saving meal: ", e)
            raise e

    def __str__(self):
        return (
            f"ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Meal Type: {self.meal_type.name}\n"
        )

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def create(cls, food_items):
        meal_name = questionary.text("Name: ").ask()
        meal_type_choices = [meal_type.name for meal_type in MealType]
        meal_type = questionary.select("Meal type: ", choices=meal_type_choices).ask()

        food_item_choices = sorted([food_item.name for food_item in food_items])
        selected_food_names = questionary.checkbox("Food items: ", choices=food_item_choices).ask()
        selected_food_items = []
        for name in selected_food_names:
            found_item = next((item for item in food_items if item.name == name), None)
            if found_item:
                selected_food_items.append(found_item)

        items_with_quantities = {}
        for item in selected_food_items:
            quantity = int(questionary.text(f"{item.name} quantity: ", default="1").ask())
            items_with_quantities[item.id] = quantity

        meal = cls(0, meal_name, MealType[meal_type])
        for food_item in selected_food_items:
            meal.add_item(food_item, items_with_quantities[food_item.id])
        return meal


class FoodItem:
    def __init__(self, id, name, serving, calories, protein, fat, carbohydrates, fiber, sugar, salt, snack):
        self.id = id
        self.name = name
        self.serving = serving
        self.calories = calories
        self.protein = protein
        self.fat = fat
        self.carbohydrates = carbohydrates
        self.fiber = fiber
        self.sugar = sugar
        self.salt = salt
        self.snack = snack

    def __str__(self):
        return (
            f"ID: {self.id}\n"
            f"Name: {self.name}\n"
            f"Serving: {self.serving}\n"
            f"Calories: {self.calories}\n"
            f"Protein: {round(self.protein, 1)}\n"
            f"Fat: {round(self.fat, 1)}\n"
            f"Carbohydrates: {round(self.carbohydrates, 1)}\n"
            f"Fiber: {round(self.fiber, 1)}\n"
            f"Sugar: {round(self.sugar, 1)}\n"
            f"Salt: {round(self.salt, 1)}\n"
            f"Snack: {'Yes' if self.snack else 'No'}"
        )

    def get_nutrition_info(self):
        return NutritionInfo(
            self.calories,
            self.protein,
            self.fat,
            self.carbohydrates,
            self.fiber,
            self.sugar,
            self.salt,
        )

    def save(self, conn):
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO food_items 
            (name, serving, calories, protein, fat, carbohydrates, fiber, sugar, salt, snack) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                self.name, self.serving, self.calories,
                self.protein, self.fat, self.carbohydrates,
                self.fiber, self.sugar, self.salt,
                self.snack
            )
        )
        conn.commit()
        self.id = cursor.lastrowid
        conn.close()

    @classmethod
    def from_db_row(cls, row):
        return cls(*row)

    @classmethod
    def create(cls):
        name = questionary.text("Name: ").ask()
        serving = questionary.text("Serving: ").ask()
        calories = int(questionary.text("Calories: ").ask())
        fat = float(questionary.text("Fat (grams): ").ask())
        carbohydrates = float(questionary.text("Carbohydrates (grams): ").ask())
        fiber = float(questionary.text("Fibre (grams): ").ask())
        protein = float(questionary.text("Protein (grams): ").ask())
        sugar = float(questionary.text("Sugar (grams): ").ask())
        salt = float(questionary.text("Salt (grams): ").ask())
        multiplier = float(questionary.text("Enter the multiplier (default is 1): ", default="1").ask())
        
        calories = int(calories * multiplier)
        protein *= multiplier
        fat *= multiplier
        carbohydrates *= multiplier
        fiber *= multiplier
        sugar *= multiplier
        salt *= multiplier

        snack = questionary.confirm("Is this item a snack?").ask()
        return cls(
            0, name, serving, calories, protein, fat, carbohydrates, fiber, sugar, salt, snack)


#
# Command processing
#
def new_item():
    conn = get_db_connection()
    new_item = FoodItem.create()
    new_item.save(conn)
    print("=======================")
    print("= Saved new food item =")
    print("=======================")
    print(new_item)


def new_meal():
    food_items = get_food_items()
    conn = get_db_connection()
    meal = Meal.create(food_items)
    meal.save(conn)
    print("==================")
    print("= Saved new meal =")
    print("==================")
    print(meal)


def plan(api):
    food_items = get_food_items()
    meals = get_meals(food_items)

    print("Provide the date for the meal plan")
    date = date_picker()

    total_calories = 0
    while True:
        choice = questionary.select(
            "Add a meal or a snack to the plan?", choices=["meal", "snack"]).ask()
        if choice == "meal":
            selection = questionary.select(
                "Meal: ",
                choices=sorted([f"{meal.meal_type.name}: {meal.name}" for meal in meals])).ask()
            name = selection.split(":")[1].strip()
            meal = next((meal for meal in meals if meal.name == name))

            console = Console()
            with console.status("[bold green]Creating task on Todoist...") as _:
                nutrition_info = meal.get_nutrition_info()
                total_calories += nutrition_info.calories
                task = api.add_task(
                    content=f"{meal.name} [{nutrition_info.calories}]",
                    labels=get_full_label_names(api, ["food"]),
                    project_id=meal.meal_type.get_project_id(),
                    due_date=date.strftime("%Y-%m-%d")
                )
                api.add_comment(task_id=task.id, content=str(nutrition_info))
                print(f"Added {meal.name} to plan")
        elif choice == "snack":
            selection = questionary.select(
                "Snack: ",
                choices=sorted([item.name for item in food_items if item.snack])).ask()
            snack = next(item for item in food_items if item.name == selection)

            if questionary.confirm("Is the snack part of a meal?").ask():
                meal_type_choices = [
                    MealType.Lunch.name,
                    MealType.Dinner.name,
                    MealType.Night.name,
                ]
                meal_type = questionary.select("Meal for snack: ", choices=meal_type_choices).ask()
                meal_type = MealType[meal_type]
                project_id = meal_type.get_project_id()
            else:
                selection = questionary.select(
                    "Snack type: ",
                    choices=[item.name for item in SnackType]).ask()
                snack_type = next(item for item in SnackType if item.name == selection)
                project_id = snack_type.get_project_id()

            console = Console()
            with console.status("[bold green]Creating task on Todoist...") as _:
                nutrition_info = snack.get_nutrition_info()
                total_calories += nutrition_info.calories
                task = api.add_task(
                    content=f"{snack.name} [{nutrition_info.calories}]",
                    labels=get_full_label_names(api, ["food"]),
                    project_id=project_id,
                    due_date=date.strftime("%Y-%m-%d")
                )
                api.add_comment(task_id=task.id, content=str(nutrition_info))
                print(f"Added {snack.name} to plan")

        if not questionary.confirm("Add another?").ask():
            break

    print(f"Total calories for planned items: {total_calories}")
#
# Helpers
#
def get_db_connection():
    app_data_path = os.path.join(os.environ["HOME"], ".local", "share", "todoist-personal")
    if not os.path.exists(app_data_path):
        os.makedirs(app_data_path)
    database_path = os.path.join(app_data_path, "food.db")
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meal_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
    )
    cursor.execute(
        """
        INSERT OR IGNORE INTO meal_types (id, name) VALUES
        (1, 'Lunch'),
        (2, 'Dinner'),
        (3, 'Night'),
        (4, 'Snacks');
        """
    )
    cursor.execute("DELETE FROM meal_types WHERE id = 4")

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS snack_types (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL
        );
        """
    )
    cursor.execute(
        """
        INSERT OR IGNORE INTO snack_types (id, name) VALUES
        (1, 'Before Lunch'),
        (2, 'After Lunch'),
        (3, 'After Dinner');
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS food_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            serving TEXT NOT NULL,
            calories INTEGER NOT NULL,
            protein REAL NOT NULL,
            fat REAL NOT NULL,
            carbohydrates REAL NOT NULL,
            fiber REAL NOT NULL,
            sugar REAL NOT NULL,
            salt REAL NOT NULL,
            snack INTEGER NOT NULL DEFAULT 0
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            meal_type_id INTEGER NOT NULL,
            FOREIGN KEY (meal_type_id) REFERENCES meal_types (id)
        );
        """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS meals_food_items (
            meal_id INTEGER NOT NULL,
            food_item_id INTEGER NOT NULL,
            quantity INTEGER NOT NULL,
            FOREIGN KEY (meal_id) REFERENCES meals (id),
            FOREIGN KEY (food_item_id) REFERENCES food_items (id),
            PRIMARY KEY (meal_id, food_item_id, quantity)
        );
        """
    )
    return conn


def get_food_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM food_items")

    food_items = []
    for row in cursor.fetchall():
        food_items.append(FoodItem.from_db_row(row))

    cursor.close()
    conn.close()
    return food_items


def get_meals(food_items):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM meals")

    meals = []
    for row in cursor.fetchall():
        meals.append(Meal.from_db_row(row))

    for meal in meals:
        cursor.execute("SELECT * FROM meals_food_items WHERE meal_id = ?", (meal.id,))
        for row in cursor.fetchall():
            item_id = row[1]
            quantity = row[2]
            item = next((item for item in food_items if item.id == item_id), None)
            meal.add_item(item, quantity)

    cursor.close()
    conn.close()
    return meals


def date_picker():
    year = questionary.text("Year (YYYY):").ask()
    month = questionary.text("Month (MM):").ask()
    day = questionary.text("Day (DD):").ask()
    
    try:
        date = datetime(year=int(year), month=int(month), day=int(day))
        return date
    except ValueError:
        print("Invalid date. Please try again.")
        return date_picker()
