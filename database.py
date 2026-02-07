import sqlite3
from datetime import datetime, timedelta

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


    # ADD THIS NEW TABLE - Favorite Foods
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS favorite_foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            food_name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit TEXT NOT NULL,
            protein REAL NOT NULL,
            calories REAL NOT NULL,
            times_logged INTEGER DEFAULT 1
        )
    ''')

    # Daily streaks
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL UNIQUE,
            protein_goal_met INTEGER DEFAULT 0,
            calorie_goal_met INTEGER DEFAULT 0,
            both_goals_met INTEGER DEFAULT 0
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
            theme TEXT DEFAULT 'light'
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
        SELECT id, food_name, quantity, protein, calories, meal_time
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
            'id': row[0],
            'food' : row[1],
            'quantity': row[2],
            'protein' : row[3],
            'calories': row[4],
            'meal_time': row[5]
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

def delete_meal(food_name, meal_time):
    """Delete a specific meal by food name and meal time for today"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    # Delete the specific meal from today
    cursor.execute('''
        DELETE FROM meals
        WHERE food_name = ? AND meal_time = ? AND date_logged = ?
        LIMIT 1
    ''', (food_name, meal_time, today))

    conn.commit()
    conn.close()

def delete_meal_by_id(meal_id):
    """Delete a specific meal by ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('DELETE FROM meals WHERE id = ?', (meal_id,))

    conn.commit()
    conn.close()

def update_meal(meal_id, food_name, quantity, protein, calories, meal_time):
    """Update a specific meal by ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE meals
        SET food_name = ?, quantity = ?, protein = ?, calories = ?, meal_time = ?
        WHERE id = ?
    ''', (food_name, quantity, protein, calories, meal_time, meal_id))

    conn.commit()
    conn.close()

def get_meal_by_id(meal_id):
    """Get a specific meal by ID"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT id, food_name, quantity, protein, calories, meal_time
        FROM meals
        WHERE id = ?
    ''', (meal_id,))

    result = cursor.fetchone()
    conn.close()

    if result:
        return {
            'id': result[0],
            'food': result[1],
            'quantity': result[2],
            'protein': result[3],
            'calories': result[4],
            'meal_time': result[5]
        }
    return None

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

def get_workout_history(days=30):
    """Get workout history for the last N days for progress tracking"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Get workouts grouped by date
    cursor.execute('''
        SELECT date_logged, 
               COUNT(*) as workout_count,
               SUM(weight * reps * sets) as total_volume
        FROM workouts
        WHERE date_logged >= ? AND date_logged <= ?
        GROUP BY date_logged
        ORDER BY date_logged ASC
    ''', (start_date_str, end_date_str))

    rows = cursor.fetchall()
    conn.close()

    history = []
    for row in rows:
        history.append({
            'date': row[0],
            'workout_count': row[1],
            'total_volume': row[2] if row[2] else 0
        })

    return history

def get_exercise_progress(exercise_name, days=30):
    """Get progress for a specific exercise over the last N days"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    # Get workouts for this exercise
    cursor.execute('''
        SELECT date_logged, weight, reps, sets, (weight * reps * sets) as volume
        FROM workouts
        WHERE exercise_name = ? AND date_logged >= ? AND date_logged <= ?
        ORDER BY date_logged ASC
    ''', (exercise_name, start_date_str, end_date_str))

    rows = cursor.fetchall()
    conn.close()

    progress = []
    for row in rows:
        progress.append({
            'date': row[0],
            'weight': row[1],
            'reps': row[2],
            'sets': row[3],
            'volume': row[4]
        })

    return progress

def clear_todays_workouts():
    """Delete all workouts logged today"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')

    cursor.execute('DELETE FROM workouts WHERE date_logged = ?', (today,))

    conn.commit()
    conn.close()

def get_all_exercises():
    """Get all unique exercise names"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT DISTINCT exercise_name
        FROM workouts
        ORDER BY exercise_name ASC
    ''')

    rows = cursor.fetchall()
    conn.close()

    exercises = [row[0] for row in rows]
    return exercises

def get_theme():
    """Get user's theme preference"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT theme FROM user_preferences WHERE id = 1')
    result = cursor.fetchone()

    conn.close()

    return result[0] if result and result[0] else 'light'

def update_theme(theme):
    """Update user's theme preference"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('UPDATE user_preferences SET theme = ? WHERE id = 1', (theme,))

    conn.commit()
    conn.close()

def record_daily_stats(protein_met, calorie_met):
    """Record whether goals were met today"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    today = datetime.now().strftime('%Y-%m-%d')
    both_met = 1 if (protein_met and calorie_met) else 0

    # Insert or update today's stats
    cursor.execute('''
        INSERT INTO daily_stats (date, protein_goal_met, calorie_goal_met, both_goals_met)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(date) DO UPDATE SET
            protein_goal_met = ?,
            calorie_goal_met = ?,
            both_goals_met = ?
    ''', (today, protein_met, calorie_met, both_met, protein_met, calorie_met, both_met))

    conn.commit()
    conn.close()


def get_current_streak():
    """Get the current streak of consecutive days meeting goals"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Get all days where both goals were met, ordered by date descending
    cursor.execute('''
        SELECT date, both_goals_met
        FROM daily_stats
        WHERE both_goals_met = 1
        ORDER BY date DESC
    ''')

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    # Check for consecutive days
    streak = 0
    today = datetime.now().date()

    for i, (date_str, _) in enumerate(rows):
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
        expected_date = today - timedelta(days=i)

        if date_obj == expected_date:
            streak += 1
        else:
            break

    return streak


def get_total_days_tracked():
    """Get total number of days with any activity"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM daily_stats')
    result = cursor.fetchone()

    conn.close()
    return result[0] if result else 0


def get_best_streak():
    """Get the longest streak ever achieved"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT date, both_goals_met
        FROM daily_stats
        ORDER BY date ASC
    ''')

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        return 0

    max_streak = 0
    current_streak = 0
    prev_date = None

    for date_str, both_met in rows:
        date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()

        if both_met == 1:
            if prev_date is None or (date_obj - prev_date).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
            prev_date = date_obj
        else:
            current_streak = 0
            prev_date = None

    return max_streak

def add_favorite_food(food_name, quantity, unit, protein, calories):
    """Add a food to favorites or increment its count"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Check if this exact combo already exists
    cursor.execute('''
        SELECT id, times_logged FROM favorite_foods 
        WHERE food_name = ? AND quantity = ? AND unit = ?
    ''', (food_name, quantity, unit))

    result = cursor.fetchone()

    if result:
        # Increment count
        cursor.execute('''
            UPDATE favorite_foods 
            SET times_logged = times_logged + 1
            WHERE id = ?
        ''', (result[0],))
    else:
        # Add new favorite
        cursor.execute('''
            INSERT INTO favorite_foods (food_name, quantity, unit, protein, calories)
            VALUES (?, ?, ?, ?, ?)
        ''', (food_name, quantity, unit, protein, calories))

    conn.commit()
    conn.close()


def get_favorite_foods(limit=5):
    """Get top favorite foods sorted by times logged"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT food_name, quantity, unit, protein, calories, times_logged
        FROM favorite_foods
        ORDER BY times_logged DESC
        LIMIT ?
    ''', (limit,))

    rows = cursor.fetchall()
    conn.close()

    favorites = []
    for row in rows:
        favorites.append({
            'food_name': row[0],
            'quantity': row[1],
            'unit': row[2],
            'protein': row[3],
            'calories': row[4],
            'times_logged': row[5]
        })

    return favorites


def remove_favorite_food(food_name, quantity, unit):
    """Remove a food from favorites"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    cursor.execute('''
        DELETE FROM favorite_foods
        WHERE food_name = ? AND quantity = ? AND unit = ?
    ''', (food_name, quantity, unit))

    conn.commit()
    conn.close()