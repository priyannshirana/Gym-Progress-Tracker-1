import sqlite3
from datetime import datetime

DATABASE_NAME = 'tracker.db'

def init_db():
    """Initializing database and create tables if it doesnt exist"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Create meals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS meals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT NOT NULL,
            quantity REAL,
            protein REAL,
            calories REAL,
            meal_time TEXT,
            date_logged TEXT        
        )
    ''')

    # Create settings table for user goals
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            protein_goal REAL,
            calorie_goal REAL
        )
    ''')


    # Create user_preferences table for onboarding
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY,
            is_onboarded INTEGER DEFAULT 0,
            cuisine_preference TEXT,
            tracking_goal TEXT,
            weight REAL,
            activity_level TEXT,
            theme TEXT DEFAULT 'soft'
        )
    ''')

    # ADD THIS NEW TABLE - Workouts
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            exercise_name TEXT NOT NULL,
            weight REAL,
            reps INTEGER,
            sets INTEGER,
            date_logged TEXT,
            notes TEXT
        )
    ''')

    # Insert default settings if the table is empty
    cursor.execute('SELECT COUNT(*) FROM settings')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO settings (id, protein_goal, calorie_goal) VALUES (1, 70, 2300)')
        print("DEBUG: Inserted default settings row")

    # Insert default user_preferences if the table is empty
    cursor.execute('SELECT COUNT(*) FROM user_preferences')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO user_preferences (id, is_onboarded) VALUES (1, 0)')
        print("DEBUG: Inserted default user_preferences row")

    conn.commit()
    conn.close()


def add_meal(food_name, quantity, protein, calories, meal_time):
    """Add a new meal to the database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    #Get today's date
    date_logged = datetime.now().strftime('%Y-%m-%d')

    #Insert the meal into the meals table
    cursor.execute('''
        INSERT INTO meals(food_name, quantity, protein, calories, meal_time,date_logged)
        VALUES (?,?,?,?,?,?)
    ''', (food_name, quantity, protein, calories, meal_time, date_logged))

    conn.commit()
    conn.close()

def get_todays_meals():

    """Get all meals logged today"""

    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    #Get Today's date
    today = datetime.now().strftime('%Y-%m-%d')

    #Query all meals from today
    cursor.execute('''
        SELECT food_name, quantity, protein, calories, meal_time
        FROM meals
        WHERE date_logged = ?
    ''', (today,))

    #Fetch all results
    rows = cursor.fetchall()
    conn.close()

    #Convert rows to list to dictornieres

    meals = []
    for row in rows:
        meals.append({
            'food' : row[0],
            'quantity': row[1],
            'protein' : row[2],
            'calories': row[3],
            'meal_time': row[4]
        })

    return meals

def clear_todays_meals():
    """Delete all meals logged today"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    # Delete all meals from today
    cursor.execute('DELETE FROM meals WHERE date_logged = ?', (today,))

    conn.commit()
    conn.close()

def get_goals():
    """Get user's protein and calorie goals"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT protein_goal, calorie_goal FROM settings WHERE id = 1')
    result = cursor.fetchone()

    conn.close()

    if result:
        return {'protein_goal': result[0], 'calorie_goal': result[1]}
    else:
        return {'protein_goal': 70, 'calorie_goal': 2300}

def update_goals(protein_goal, calorie_goal):
    """Update user's goals"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE settings 
        SET protein_goal = ?, calorie_goal = ?
        WHERE id = 1
    ''', (protein_goal, calorie_goal))

    conn.commit()
    conn.close()

def is_user_onboarded():
    """Check if user has completed onboarding"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT is_onboarded FROM user_preferences WHERE id = 1')
    result = cursor.fetchone()

    conn.close()

    is_onboarded = result[0] == 1 if result else False
    print(f"DEBUG: is_onboarded = {is_onboarded}, result = {result}")  # ADD THIS
    return is_onboarded

def save_onboarding(protein_goal, calorie_goal, cuisine, tracking_goal, weight, activity_level):
    """Save onboarding data"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Update preferences
    cursor.execute('''
        UPDATE user_preferences 
        SET is_onboarded = 1, 
            cuisine_preference = ?, 
            tracking_goal = ?,
            weight = ?,
            activity_level = ?
        WHERE id = 1
    ''', (cuisine, tracking_goal, weight, activity_level))

    print(f"DEBUG: Updated {cursor.rowcount} rows in user_preferences")  # ADD THIS

    # Update goals
    cursor.execute('''
        UPDATE settings 
        SET protein_goal = ?, calorie_goal = ?
        WHERE id = 1
    ''', (protein_goal, calorie_goal))

    print(f"DEBUG: Updated {cursor.rowcount} rows in settings")  # ADD THIS

    conn.commit()
    conn.close()

    print("DEBUG: Onboarding saved!")  # ADD THIS



def get_user_preferences():
    """Get user preferences"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT cuisine_preference, tracking_goal, weight, activity_level FROM user_preferences WHERE id = 1')
    result = cursor.fetchone()

    conn.close()

    if result:
        return {
            'cuisine': result[0],
            'goal': result[1],
            'weight': result[2],
            'activity': result[3]
        }
    return None

def add_workout(exercise_name, weight, reps, sets, notes =''):
    """Add a new workout to the database"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    date_logged = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('''
        INSERT INTO workouts (exercise_name, weight, reps, sets, date_logged, notes)
        VALUES (?,?,?,?,?,?)
    ''', (exercise_name, weight,reps, sets, date_logged, notes))

    conn.commit()
    conn.close()

def get_todays_workouts():
    """GET all workouts logged today"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('''
        SELECT exercise_name, weight, reps, sets, notes
        FROM workouts
        WHERE date_logged = ?
        ORDER BY id DESC
    ''', (today,))

    rows = cursor.fetchall()
    conn.close()

    # Convert to list of dictionaries
    workouts = []
    for row in rows:
        workouts.append({
            'exercise': row[0],
            'weight': row[1],
            'reps': row[2],
            'sets': row[3],
            'notes': row[4]
        })

    return workouts
def get_last_workout(exercise_name):
    """Get the last time you did this exercise"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT weight, reps, sets, date_logged
        FROM workouts
        WHERE exercise_name = ?
        ORDER BY date_logged DESC, id DESC
        LIMIT 1
    ''', (exercise_name,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'weight': result[0],
            'reps': result[1],
            'sets': result[2],
            'date': result[3]
        }
    return None

def clear_todays_workouts():
    """Delete all workouts logged today"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('DELETE FROM workouts WHERE date_logged = ?', (today,))

    conn.commit()
    conn.close()

def get_theme():
    """Get user's theme preference"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT theme FROM user_preferences WHERE id = 1')
    result = cursor.fetchone()

    conn.close()

    return result[0] if result and result[0] else 'soft'

def update_theme(theme):
    """Update user's theme preference"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('UPDATE user_preferences SET theme = ? WHERE id = 1', (theme,))

    conn.commit()
    conn.close()