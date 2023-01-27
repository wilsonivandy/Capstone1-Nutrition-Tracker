import requests
from unittest.loader import VALID_MODULE_NAME
from flask import Flask, redirect, render_template, session, flash, request
from flask_bootstrap import Bootstrap
from food import getFoodInfo
from forms import signUpForm, logInForm
import os
#from secret import API_SECRET_KEY, APP_SECRET_KEY
from models import db, connect_db, User, Meal, Food, Preference, User_Preference, Meal_Food, PREFERENCES, INTOLERANCES
from user import validateSignUp, validateLogIn, validatePreferences, getCumulative
from meal import getSuggestions, getPreferences, getQueryResults, resetQueries, createMeal
from food import getFoodInfo, getRecipeSteps, getRecipeIngredients, getMealPlan
from api import apiFoodInfo


app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
   'DATABASE_URL').replace("postgres://", "postgresql://", 1)
API_SECRET_KEY = os.environ.get('API_SECRET_KEY')

connect_db(app)
#db.drop_all()
db.create_all()

@app.route("/")
def root():
    return redirect('/signup')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """Signup: redirect to /login if already have account, otherwise create user."""
    form = signUpForm(request.form, meta={'csrf': False})
    message = validateSignUp(form)
    if message:
        if isinstance(message, User):
            return redirect(f'/users/{message.id}/preference')
    session["username"] = form.username.data
    return render_template('signup.html', message = message)

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login: Log in and if authenticated, redirect to /user/<user_id>."""
    form = logInForm(request.form, meta={'csrf': False})
    message = validateLogIn(form)
    if request.method == "POST":
        if message:
            return redirect(message)
        else:
            message = "Incorrect Username / Password"
    return render_template('login.html', message = message)

@app.route("/users/<int:user_id>/preference", methods=['GET', 'POST'])
def preference(user_id):
    """
    Preference: If user is logged in user is a newly created account, display form to set total calories, carbs,
    proteins, fats, along with all intolerances and preferences. Then redirect to home page.     
    """
    if "username" not in session:
        flash("You must be logged in!")
        return redirect('/login')
    else:
        if request.method =="POST":
            validatePreferences(request.form, user_id)
            return redirect(f'/users/{user_id}')
        return render_template('preference.html', user_id = user_id, preferences = PREFERENCES, intolerances = INTOLERANCES)

@app.route("/users/<int:user_id>", methods=['GET'])
def home(user_id):
    """Home: Page showing brief summary of meals eaten in the day so far"""
    user = User.query.get_or_404(user_id)
    preferences = User_Preference.query.filter_by(user_id = user_id)
    meals = Meal.query.filter_by(user_id = user_id)
    runningCalories, runningCarbs, runningProteins, runningFats = getCumulative(user_id)
    return render_template('home.html', user = user, preferences = preferences, meals = meals, runningCalories = runningCalories, runningCarbs=runningCarbs, runningProteins=runningProteins,runningFats=runningFats)

@app.route("/users/<int:user_id>/meal/add/<type>", methods=['GET', 'POST'])
def add_Meal(user_id, type):
    user = User.query.get_or_404(user_id)
    calorieTarget = user.totalcalories / 3
    runningCalories, runningCarbs, runningProteins, runningFats = getCumulative(user_id)
    intolerances, preferences, exclusions = getPreferences(user_id)
    suggestions = getSuggestions(intolerances, preferences, calorieTarget, API_SECRET_KEY)
    queries = resetQueries()
    createMeal(user_id, type)
    if request.method == 'POST':
        queries = getQueryResults(request.form.get('query'), intolerances, preferences, calorieTarget, API_SECRET_KEY)
        return redirect(f"/users/{user.id}/meal/add/{type}")
    return render_template('foodList.html', user = user, suggestions = suggestions, queries = queries, type = type, intolerances = intolerances, preferences=preferences, exclude=exclusions, runningCalories = runningCalories, runningCarbs = runningCarbs, runningProteins = runningProteins, runningFats = runningFats)

@app.route("/users/<int:user_id>/meal/add/<type>/<food_id>", methods=['POST'])
def add_Food(user_id, type, food_id):
    user = User.query.get_or_404(user_id)
    meal = Meal.query.filter_by(user_id = user.id, meal = type).first()
    name, image, calories, carbohydrates, proteins, fats = getFoodInfo(food_id, API_SECRET_KEY)
    newFood = Food(name = name, food_id = food_id, image_url = image, calories = calories, carbs = carbohydrates, proteins = proteins,  fats = fats)
    db.session.add(newFood)
    meal.foods.append(newFood)
    db.session.commit()
    return redirect(f'/users/{user.id}')

@app.route("/users/<int:user_id>/meal/remove/<type>/<food_id>", methods=['GET','POST'])
def remove_Food(user_id, type, food_id):
    user = User.query.get_or_404(user_id)
    print(request)
    if request.method == 'POST':
        food = Food.query.filter_by(food_id = food_id).first()
        db.session.delete(food)
        db.session.commit()
    return redirect(f'/users/{user.id}')

@app.route("/users/<int:user_id>/<type>/<food_id>/recipe")
def view_Recipe(user_id, food_id, type):
    user = User.query.get_or_404(user_id)
    runningCalories, runningCarbs, runningProteins, runningFats = getCumulative(user_id)
    name, image, calories, carbohydrates, proteins, fats = getFoodInfo(food_id, API_SECRET_KEY)
    steps = getRecipeSteps(food_id, API_SECRET_KEY)
    ingredients = getRecipeIngredients(food_id, API_SECRET_KEY)
    info_response = apiFoodInfo(food_id, API_SECRET_KEY)
    return render_template('viewRecipe.html', user = user, food_id = food_id, steps = steps, type = type, ingredients = ingredients, info = info_response, calories = calories, carbs = carbohydrates, proteins = proteins,  fats = fats, runningCalories = runningCalories, runningCarbs = runningCarbs, runningProteins = runningProteins, runningFats = runningFats)

@app.route("/users/<int:user_id>/autopopulate", methods=['POST'])
def autopopulate(user_id):
    user = User.query.get_or_404(user_id)
    ids = getMealPlan(user, API_SECRET_KEY)
    session['ids'] = ids
    return redirect(f'/users/{user.id}/meal/add/autopopulate')


@app.route("/users/<int:user_id>/meal/add/autopopulate")
def add_Foods(user_id):
    ids = session['ids']
    types = ['breakfast', 'lunch', 'dinner']
    counter = 0
    for f in ids:
        createMeal(user_id, types[counter])
        meal = Meal.query.filter_by(user_id = user_id, meal = types[counter]).first()
        meal.foods = []
        name, image, calories, carbohydrates, proteins, fats = getFoodInfo(f, API_SECRET_KEY)
        newFood = Food(name = name, food_id = f, image_url = image, calories = calories, carbs = carbohydrates, proteins = proteins,  fats = fats)
        db.session.add(newFood)
        meal.foods.append(newFood)
        counter += 1
    db.session.commit()
    return redirect(f'/users/{user_id}')

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/")


