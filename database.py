import sqlite3

DATABASE = "fitbuddy.db"


def create_database():
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            weight REAL,
            goal TEXT,
            intensity TEXT,
            workout_plan TEXT,
            nutrition_tip TEXT
        )
    """)

    connection.commit()
    connection.close()


def save_user(
    name,
    age,
    weight,
    goal,
    intensity,
    workout_plan,
    nutrition_tip
):
    connection = sqlite3.connect(DATABASE)

    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO users
        (name, age, weight, goal, intensity, workout_plan, nutrition_tip)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        name,
        age,
        weight,
        goal,
        intensity,
        workout_plan,
        nutrition_tip
    ))

    connection.commit()

    user_id = cursor.lastrowid

    connection.close()

    return user_id