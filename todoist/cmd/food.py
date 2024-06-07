import os
import questionary
import sqlite3

from enum import Enum


class MealType(Enum):
    Lunch = 1
    Dinner = 2
    Night = 3
    Snacks = 4


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
            snack INTEGER NOT NULL DEFAULT 0);
        """
    )
    return conn
