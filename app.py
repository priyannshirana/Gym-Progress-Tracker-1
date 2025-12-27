from flask import Flask, render_template, request, redirect, url_for
import database
app = Flask(__name__)
app.secret_key = 'nutritrack-secret-key-2024'

database.init_db()

# Store meals in a list
Food_database = {

    #Grains/Bread
    'White Rice': {'calories':130, 'protein':2.7, 'base_Unit': '100g'},
    'Bread (1 slice)': {'calories':80, 'protein': 5, 'base_Unit': 'slice', 'grams_per_unit': 30},
    'Almond Tortilla': {'calories':150, 'protein':2, 'base_Unit': 'piece', 'grams_per_unit': 50},

    #Proteins
    'Egg (1 large)' : {'calories' : 70, 'protein' : 6, 'base_Unit' : 'piece'},
    'Chicken' : {'calories' : 165, 'protein' : 31, 'base_Unit' : '100g'},
    'Shrimp' : {'calories' : 99, 'protein' : 24, 'base_Unit' : '100g'},
    'Fish' : {'calories' : 140, 'protein' : 25, 'base_Unit' : '100g'},
    'Paneer' : {'calories' : 265, 'protein' : 18, 'base_Unit' : '100g'},
    'Tofu' : {'calories' : 76, 'protein' : 8, 'base_Unit' : '100g'},
    'Protein Powder (1 scoop)' : {'calories' : 120, 'protein' : 24, 'base_Unit' : 'scoop', 'grams_per_unit': 30},

    #Vegetables
    'Spinach': {'calories': 23, 'protein': 3, 'base_Unit': '100g'},
    'Potatoes': {'calories': 87, 'protein': 2, 'base_Unit': '100g'},
    'Broccoli': {'calories': 35, 'protein': 3, 'base_Unit': '100g'},

    #Dairy
    'Yogurt': {'calories': 60, 'protein': 3.5, 'base_Unit': '100g'},
    'Whole Milk': {'calories': 150, 'protein': 8, 'base_Unit': '1 cup', 'grams_per_unit': 240},
    'Cheese': {'calories': 400, 'protein': 25, 'base_Unit': '100g'},
    'Ghee': {'calories': 45, 'protein': 0, 'base_Unit': '1 tsp', 'grams_per_unit': 5},

    #Fruits
    'Apple (1 medium)': {'calories': 95, 'protein': 0.5, 'base_Unit': 'piece', 'grams_per_unit': 180},
    'Banana (1 medium)': {'calories': 105, 'protein': 1.3, 'base_Unit': 'piece', 'grams_per_unit': 120},
    'Avocado': {'calories': 160, 'protein': 2, 'base_Unit': '100g'},
    'Dates (1 date)': {'calories': 20, 'protein': 0.2, 'base_Unit': 'piece', 'grams_per_unit': 8},
    'Orange (1 medium)': {'calories': 62, 'protein': 1.2, 'base_Unit': 'piece', 'grams_per_unit': 130},
    'Pear (1 medium)': {'calories': 100, 'protein': 0.6, 'base_Unit': 'piece' , 'grams_per_unit': 180},
}

@app.route('/')
def home():

    # Check if user needs onboarding
    if not database.is_user_onboarded():
        return redirect(url_for('onboarding'))

    theme = database.get_theme()

    # Get goals from database
    goals = database.get_goals()
    protein_goal = goals['protein_goal']
    calorie_goal = goals['calorie_goal']

    # Get today's meals from database
    meals = database.get_todays_meals()

    # Calculate totals from all meals
    proteinTotal = sum(float(meal['protein']) for meal in meals)
    caloriesTotal = sum(float(meal['calories']) for meal in meals)

    # Calculate percentages for progress bars
    protein_percentage = (proteinTotal / protein_goal * 100) if protein_goal > 0 else 0
    calorie_percentage = (caloriesTotal / calorie_goal * 100) if calorie_goal > 0 else 0

    # Check if goals are met
    protein_met = protein_percentage >= 100
    calorie_met = calorie_percentage >= 100

    # Record today's stats
    database.record_daily_stats(protein_met, calorie_met)

    # Get streak data
    current_streak = database.get_current_streak()
    best_streak = database.get_best_streak()
    total_days = database.get_total_days_tracked()

    goal_just_reached = request.args.get('goal_reached') == '1'

    # Get success message if exists
    success_message = request.args.get('success')

    return render_template('index.html',
                           meals=meals,
                           proteinTotal=proteinTotal,
                           caloriesTotal=caloriesTotal,
                           protein_goal=protein_goal,
                           calorie_goal=calorie_goal,
                           protein_percentage=protein_percentage,
                           calorie_percentage=calorie_percentage,
                           food_database=Food_database,
                           theme = theme,
                           goal_reached = goal_just_reached, success_message=success_message)


@app.route('/add_custom', methods=['POST'])
def add_custom():
    try:
        food = request.form['food']
        quantity = float(request.form['quantity'])
        unit = request.form['unit']  # Get unit from form
        protein_per_unit = float(request.form['protein'])
        calories_per_unit = float(request.form['calories'])
        meal_time = request.form['meal_time']

        # Input Validation
        if not food:
            return redirect(url_for('home', success='error_empty_food'))
        if quantity <= 0 or quantity > 10000:
            return redirect(url_for('home', success = 'error_quantity'))
        if protein_per_unit < 0 or protein_per_unit > 1000:
            return redirect(url_for('home', success = 'error_protein'))
        if calories_per_unit < 0 or calories_per_unit > 10000:
            return redirect(url_for('home', success = 'error_calories'))

        # Calculate totals
        total_protein = protein_per_unit * quantity
        total_calories = calories_per_unit * quantity

        # Create food name with unit
        food_name = f"{food} ({quantity} {unit})"

        # Check if this will reach goal
        goals = database.get_goals()
        meals = database.get_todays_meals()
        current_protein = sum(float(meal['protein']) for meal in meals)
        current_calories = sum(float(meal['calories']) for meal in meals)

        was_below_protein = (current_protein / goals['protein_goal'] * 100) < 100
        was_below_calories = (current_calories / goals['calorie_goal'] * 100) < 100

        # Add to database (not to list!)
        database.add_meal(food_name, quantity, total_protein, total_calories, meal_time)

        # Check if goal just reached
        new_protein = current_protein + total_protein
        new_calories = current_calories + total_calories
        new_protein_pct = (new_protein / goals['protein_goal'] * 100)
        new_calorie_pct = (new_calories / goals['calorie_goal'] * 100)

        goal_reached = (was_below_protein and new_protein_pct >= 100) or (was_below_calories and new_calorie_pct >= 100)

        if goal_reached:
            return redirect(url_for('home', success='food_logged', goal_reached='1'))
        else:
            return redirect(url_for('home', success='food_logged'))

    except ValueError:
        return redirect(url_for('home', success='error_invalid'))
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('home', success='error'))

@app.route('/add_from_database', methods=['POST'])
def add_from_database():

    try:
        """Add a food item from the existing database"""
        food = request.form['food']
        quantity = float(request.form['quantity'])
        unit = request.form['unit']
        meal_time = request.form['meal_time']

        #Validation
        if quantity <= 0 or quantity > 10000:
            return redirect(url_for('home', success = "error_quantity"))
        # Get nutrition info from database
        food_info = Food_database[food]
        if not food_info:
            return redirect(url_for('home', success ='error_food_not_found'))
        # Calculate multiplier based on unit
        if unit == 'grams':
            if food_info['base_Unit'] == '100g':
                multiplier = quantity / 100
            else:
                grams_per_unit = food_info.get('grams_per_unit', 100)
                multiplier = quantity / grams_per_unit
        elif unit == 'piece':
            if food_info['base_Unit'] in ['piece', 'slice', 'scoop', 'cup', 'tsp']:
                multiplier = quantity
            else:
                grams_per_unit = food_info.get('grams_per_unit', 100)
                total_grams = quantity * grams_per_unit
                multiplier = total_grams / 100
        else:
            multiplier = quantity

        # Calculate totals
        total_protein = food_info['protein'] * multiplier
        total_calories = food_info['calories'] * multiplier

        # Create food name with unit
        food_name = f"{food} ({quantity} {unit})"


        # Check if this will reach goal
        goals = database.get_goals()
        meals = database.get_todays_meals()
        current_protein = sum(float(meal['protein']) for meal in meals)
        current_calories = sum(float(meal['calories']) for meal in meals)

        was_below_protein = (current_protein / goals['protein_goal'] * 100) < 100
        was_below_calories = (current_calories / goals['calorie_goal'] * 100) < 100


        # Add to database
        database.add_meal(food_name, quantity, total_protein, total_calories, meal_time)

        # Check if goal just reached
        new_protein = current_protein + total_protein
        new_calories = current_calories + total_calories
        new_protein_pct = (new_protein / goals['protein_goal'] * 100)
        new_calorie_pct = (new_calories / goals['calorie_goal'] * 100)

        goal_reached = (was_below_protein and new_protein_pct >= 100) or (was_below_calories and new_calorie_pct >= 100)

        if goal_reached:
            return redirect(url_for('home', success='food_logged', goal_reached='1'))
        else:
            return redirect(url_for('home', success='food_logged'))

    except ValueError:
        return redirect(url_for('home', success='error_invalid'))
    except Exception as e:
        print(f"Error: {e}")
        return redirect(url_for('home', success='error'))
@app.route('/clear')
def clear_meals():
    """Clear all logged meals (reset for new day)"""
    database.clear_todays_meals()  # Use database function
    return redirect(url_for('home', success = 'meals_cleared'))

@app.route('/settings')
def settings():
    """Display settings page"""
    goals = database.get_goals()
    theme = database.get_theme()
    success_message = request.args.get('success')

    return render_template('settings.html',
                           protein_goal=goals['protein_goal'],
                           calorie_goal=goals['calorie_goal'],
                           theme = theme,
                           success_message = success_message)

@app.route('/update_settings', methods=['POST'])
def update_settings():
    try:

        """Update user goals"""
        protein_goal = float(request.form['protein_goal'])
        calorie_goal = float(request.form['calorie_goal'])

        # VALIDATION
        if protein_goal <= 0 or protein_goal > 1000:
            return redirect(url_for('settings', success='error_protein'))

        if calorie_goal <= 0 or calorie_goal > 10000:
            return redirect(url_for('settings', success='error_calories'))


        database.update_goals(protein_goal, calorie_goal)
        return redirect(url_for('settings', success='goals_updated'))

    except ValueError:
        return redirect(url_for('settings', success='error_invalid'))
@app.route('/onboarding')
def onboarding():
    """Show onboarding page for new users"""
    return render_template('onboarding.html')

@app.route('/complete_onboarding', methods=['POST'])
def complete_onboarding():
    try:
        """Save onboarding data and redirect to home"""
        # Get form data
        protein_goal = float(request.form['protein_goal'])
        calorie_goal = float(request.form['calorie_goal'])
        cuisine = request.form['cuisine_preference']
        tracking_goal = request.form['tracking_goal']
        weight = float(request.form['weight'])
        activity_level = request.form['activity_level']

        # VALIDATION
        if weight <= 0 or weight > 1000:
            return "Invalid weight", 400

        if protein_goal <= 0 or protein_goal > 1000:
            return "Invalid protein goal", 400

        if calorie_goal <= 0 or calorie_goal > 10000:
            return "Invalid calorie goal", 400

        database.save_onboarding(protein_goal, calorie_goal, cuisine, tracking_goal, weight, activity_level)
        return redirect(url_for('home'))

    except ValueError:
        return "Invalid input", 400

@app.route('/fix_db')
def fix_db():
    """Temporary route to fix database"""
    import sqlite3
    conn = sqlite3.connect('tracker.db')
    cursor = conn.cursor()

    # Check if row exists
    cursor.execute('SELECT COUNT(*) FROM user_preferences')
    if cursor.fetchone()[0] == 0:
        cursor.execute('INSERT INTO user_preferences (id, is_onboarded) VALUES (1, 0)')
        conn.commit()
        return "Fixed! Now go to <a href='/'>home</a>"
    else:
        return "Already has a row. Go to <a href='/'>home</a>"

    conn.close()

@app.route('/gym')
def gym_tracker():
    """Display gym tracker page"""
    # Check if user needs onboarding
    if not database.is_user_onboarded():
        return redirect(url_for('onboarding'))

    theme = database.get_theme()

    # Get today's workouts
    workouts = database.get_todays_workouts()
    theme = database.get_theme()
    success_message = request.args.get('success')
    return render_template('gym_tracker.html',
                           workouts=workouts,
                           theme= theme,
                           success_message=success_message)

@app.route('/add_workout', methods=['POST'])
def add_workout():
    try:
        """Add a workout to the database"""
        exercise = request.form['exercise']
        weight = float(request.form['weight'])
        reps = int(request.form['reps'])
        sets = int(request.form['sets'])
        notes = request.form.get('notes', '')  # Optional field

        # VALIDATION
        if not exercise:
            return redirect(url_for('gym_tracker', success='error_empty_exercise'))

        if weight < 0 or weight > 10000:
            return redirect(url_for('gym_tracker', success='error_weight'))

        if reps <= 0 or reps > 1000:
            return redirect(url_for('gym_tracker', success='error_reps'))

        if sets <= 0 or sets > 100:
            return redirect(url_for('gym_tracker', success='error_sets'))

        database.add_workout(exercise, weight, reps, sets, notes)
        return redirect(url_for('gym_tracker', success='workout_logged'))

    except ValueError:
        return redirect(url_for('gym_tracker', success='error_invalid'))

@app.route('/clear_workouts')
def clear_workouts():
    """Clear all workouts for today"""
    database.clear_todays_workouts()
    return redirect(url_for('gym_tracker',  success='workouts_cleared'))

@app.route('/update_theme', methods=['POST'])
def update_theme():
    """Update user's theme preference"""
    theme = request.form['theme']
    if theme not in ['soft', 'minimal']:
        return redirect(url_for('settings', success='error_theme'))

    database.update_theme(theme)
    return redirect(url_for('settings', success='theme_updated'))

if __name__ == '__main__':
    app.run(debug = True)