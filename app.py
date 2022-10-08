from cmath import log
from crypt import methods
from xxlimited import foo
import requests
from unicodedata import decimal
from unittest.loader import VALID_MODULE_NAME
from flask import Flask, redirect, render_template, jsonify, session, flash, request
from importlib_metadata import method_cache
from sqlalchemy import desc
from secret import API_SECRET_KEY, APP_SECRET_KEY
from decimal import Decimal
from flask_bootstrap import Bootstrap
from forms import signUpForm, logInForm
import multidict

from models import db, connect_db, User, Meal, Food, Preference, User_Preference, Meal_Food

app = Flask(__name__)
Bootstrap(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nutrition'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
app.config['SECRET_KEY'] = APP_SECRET_KEY
INTOLERANCES = ['Dairy', 'Egg', 'Gluten', 'Grain', 'Peanut', 'Seafood', 'Sesame', 'Shellfish', 'Soy', 'Sulfite', 'Tree nut', 'Wheat']
PREFERENCES = ['Beef', 'Pork']


connect_db(app)
db.drop_all()
db.create_all()

@app.route("/")
def root():
    return redirect('/signup')

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    """Signup: redirect to /login if already have account, otherwise create user."""
    form = signUpForm(request.form, meta={'csrf': False})
    message = False
    if form.validate():
        if User.query.filter_by(username = form.username.data).count() > 0:
            message = "Username Taken. Please Choose Another."
        elif User.query.filter_by(email = form.email.data).count() > 0:
            message = "Email Taken. Please Choose Another."
        else:
            newUser = User.signup(first_name = form.first_name.data, last_name=form.last_name.data, username=form.username.data, password=form.password.data, email=form.email.data)
            for p in PREFERENCES + INTOLERANCES:
                if Preference.query.filter_by(preference= p).count() >= 1:
                    newPreference = Preference.query.filter_by(preference=p).first()
                else:
                    newPreference = Preference(preference=p)
                newUser.preferences.append(newPreference)
                db.session.add(newPreference)
            db.session.add(newUser)
            db.session.commit()
            session["username"] = form.username.data
            return redirect(f'/users/{newUser.id}/preference')
    return render_template('signup.html', message = message)

@app.route("/login", methods=['GET', 'POST'])
def login():
    """Login: Log in and if authenticated, redirect to /user/<user_id>."""
    form = logInForm(request.form, meta={'csrf': False})
    message = False
    if form.validate():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            session["username"] = user.username
            return redirect(f'/users/{user.id}')
        else:
            message = 'Invalid username / password'
    return render_template('login.html', message = message)

@app.route("/users/<int:user_id>/preference", methods=['GET', 'POST'])
def preference(user_id):
    if "username" not in session:
        flash("You must be logged in!")
        return redirect('/login')
    else:
        user = User.query.get_or_404(user_id)
        preferences = User_Preference.query.filter_by(user_id = user_id)
        if request.method =="POST":
            for p in PREFERENCES:
                val = True
                resp = request.form.get(p)
                if resp != 'on':
                    val = False
                pref_id = Preference.query.filter_by(preference=p).first().id
                preferences.filter_by(preference_id = pref_id).first().importance = val
            for i in INTOLERANCES:
                val = True
                resp = request.form.get(i)
                if resp != 'on':
                    val = False
                pref_id = Preference.query.filter_by(preference=i).first().id
                preferences.filter_by(preference_id = pref_id).first().importance = val
            user.totalcalories = int(float(request.form['totalcalories']))
            user.totalcarbs = int(float(request.form['totalcarbs']))
            user.totalproteins = int(float(request.form['totalproteins']))
            user.totalfats = int(float(request.form['totalfats']))
            db.session.commit()
            return redirect(f'/users/{user.id}')
        return render_template('preference.html', user = user, preferences = PREFERENCES, intolerances = INTOLERANCES)

@app.route("/logout")
def logout():
    session.pop("username")
    return redirect("/")

@app.route("/users/<int:user_id>")
def home(user_id):
    """Home: Page showing brief summary of meals eaten in the day so far"""
    user = User.query.get_or_404(user_id)
    preferences = User_Preference.query.filter_by(user_id = user_id)
    meals = Meal.query.filter_by(user_id = user_id)
    runningCalories, runningCarbs, runningProteins, runningFats = get_Cumulative(user_id)
    return render_template('home.html', user = user, preferences = preferences, meals = meals, runningCalories = runningCalories, runningCarbs=runningCarbs, runningProteins=runningProteins,runningFats=runningFats)

@app.route("/users/<int:user_id>/meal/add/<type>", methods=['GET', 'POST'])
def add_Meal(user_id, type):
    user = User.query.get_or_404(user_id)
    intol = User_Preference.query.filter_by(user_id = user_id)
    runningCalories, runningCarbs, runningProteins, runningFats = get_Cumulative(user_id)
    intolerances = []
    preferences = []
    target = user.totalcalories / 3
    for user_pref in intol:
        pref = Preference.query.get(user_pref.preference_id).preference
        if user_pref.importance == False:
            if pref in INTOLERANCES:
                intolerances.append(pref.lower())
            if pref in PREFERENCES:
                preferences.append(pref.lower())
    url = 'https://api.spoonacular.com/recipes/complexSearch'
    params = {
        'intolerances': intolerances,
        'excludeIngredients':preferences,
        'type': type,
        'minCalories': target * 0.5,
        'maxCalories': target * 1.2,
        'apiKey': API_SECRET_KEY }
    respSuggestions = requests.get(url, params)
    session["suggestions"] = []
    suggestions = session["suggestions"]
    for food in respSuggestions.json()['results']:
        suggestions.append({
            "id": food["id"],
            "name": food["title"],
            "image": food["image"],
            "calories": (food["nutrition"])["nutrients"][0]["amount"]
        })
        session["suggestions"] = suggestions

    exclude = "Exclude: "
    for f in INTOLERANCES + PREFERENCES:
        if f.lower() in intolerances or f.lower() in preferences:
            exclude += f'{f} / '

    if "queries" in session:
        queries = session['queries']
        session.pop('queries')
    else:
        queries = []

    if Meal.query.filter_by(meal = type, user_id = user.id).count() == 0:
        newMeal = Meal(meal = type, user_id = user.id)
        db.session.add(newMeal)
        db.session.commit()
    
    if request.method == 'POST':

        print("***********")
        print(intolerances)
        print(preferences)
        name = request.form.get('query')
        params = {
        'query': name,
        'intolerances': intolerances,
        'excludeIngredients':preferences,
        'type': type,
        'minCalories': target * 0.5,
        'maxCalories': target * 1.2,
        'number': 20,
        'apiKey': API_SECRET_KEY
        }
        respQueries = requests.get(url, params)
        queries =  []
        for food in respQueries.json()['results']:
            queries.append({
                "id": food["id"],
                "name": food["title"],
                "image": food["image"],
                "calories": (food["nutrition"])["nutrients"][0]["amount"]
            })
        session["queries"] = queries
        return redirect(f"/users/{user.id}/meal/add/{type}")

    return render_template('foodList.html', user = user, suggestions = suggestions, queries = queries, type = type, intolerances = intolerances, preferences=preferences, exclude=exclude, runningCalories = runningCalories, runningCarbs = runningCarbs, runningProteins = runningProteins, runningFats = runningFats)

@app.route("/users/<int:user_id>/meal/add/<type>/<food_id>", methods=['POST'])
def add_Food(user_id, type, food_id):
    url = f'https://api.spoonacular.com/recipes/{food_id}/information'
    params = {
        'includeNutrition': True,
        'apiKey': API_SECRET_KEY 
    }
    resp = requests.get(url, params).json()
    user = User.query.get_or_404(user_id)
    meal = Meal.query.filter_by(user_id = user.id, meal = type).first()

    for n in resp["nutrition"]["nutrients"]:
        if n['name'] == "Calories":
            calories = n["amount"]
        if n['name'] == "Carbohydrates":
            carbohydrates =n["amount"]
        if n['name'] == "Protein":
            proteins = n["amount"]
        if n['name'] == "Fat":
            fats = n["amount"]
    name = resp['title']
    image = resp['image']
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
        print('post')
        return redirect(f'/users/{user.id}')
    else:
        print('no post')
        return redirect(f'/users/{user.id}')

@app.route("/users/<int:user_id>/<type>/<food_id>/recipe")
def view_Recipe(user_id, food_id, type):
    user = User.query.get_or_404(user_id)
    runningCalories, runningCarbs, runningProteins, runningFats = get_Cumulative(user_id)
    info_url = f'https://api.spoonacular.com/recipes/{food_id}/information'
    info_params = {
        'includeNutrition': True,
        'apiKey': API_SECRET_KEY 
    }
    info_response = requests.get(info_url, info_params).json()
    steps_url = f'https://api.spoonacular.com/recipes/{food_id}/analyzedInstructions'
    steps_params = {
        'stepBreakdown': True,
        'apiKey': API_SECRET_KEY 
    }
    steps_response = requests.get(steps_url, steps_params).json()
    ingredients_url = f'https://api.spoonacular.com/recipes/{food_id}/ingredientWidget.json'
    ingredients_params = {
        'apiKey': API_SECRET_KEY 
    }
    ingredients_response = requests.get(ingredients_url, ingredients_params).json()
    ingredients = []
    for i in ingredients_response['ingredients']:
        ingredients.append(f"{i['amount']['metric']['value']}" + " " + f"{i['amount']['metric']['unit']}" + " " + f"{i['name']}")
    steps = []
    for s in steps_response[0]['steps']:
        steps.append({s['number']:s['step']})
    for n in info_response["nutrition"]["nutrients"]:
        if n['name'] == "Calories":
            calories = n["amount"]
        if n['name'] == "Carbohydrates":
            carbohydrates =n["amount"]
        if n['name'] == "Protein":
            proteins = n["amount"]
        if n['name'] == "Fat":
            fats = n["amount"]
    return render_template('viewRecipe.html', user = user, food_id = food_id, steps = steps, type = type, ingredients = ingredients, info = info_response, calories = calories, carbs = carbohydrates, proteins = proteins,  fats = fats, runningCalories = runningCalories, runningCarbs = runningCarbs, runningProteins = runningProteins, runningFats = runningFats)

@app.route("/users/<int:user_id>/autopopulate", methods=['POST'])
def autopopulate(user_id):
    user = User.query.get_or_404(user_id)
    url = 'https://api.spoonacular.com/mealplanner/generate'
    params = {
        'timeFrame': 'day',
        'targetCalories': user.totalcalories,
        'apiKey': API_SECRET_KEY 
    }
    resp = requests.get(url, params).json()['meals']
    session['types'] = ['breakfast, lunch, dinner']
    ids = []
    for r in resp:
        ids.append(r['id'])
    session['ids'] = ids
    return redirect(f'/users/{user.id}/meal/add/autopopulate')


@app.route("/users/<int:user_id>/meal/add/autopopulate")
def add_Foods(user_id):
    user = User.query.get_or_404(user_id)
    ids = session['ids']
    types = ['breakfast', 'lunch', 'dinner']
    counter = 0
    for f in ids:
        url = f'https://api.spoonacular.com/recipes/{f}/information'
        params = {
        'includeNutrition': True,
        'apiKey': API_SECRET_KEY
        }
        if Meal.query.filter_by(meal = types[counter], user_id = user.id).count() == 0:
            newMeal = Meal(meal = types[counter], user_id = user.id)
            db.session.add(newMeal)
            db.session.commit()
        resp = requests.get(url, params).json()
        user = User.query.get_or_404(user_id)
        meal = Meal.query.filter_by(user_id = user.id, meal = types[counter]).first()
        meal.foods = []
        for n in resp["nutrition"]["nutrients"]:
            if n['name'] == "Calories":
                calories = n["amount"]
            if n['name'] == "Carbohydrates":
                carbohydrates =n["amount"]
            if n['name'] == "Protein":
                proteins = n["amount"]
            if n['name'] == "Fat":
                fats = n["amount"]
        name = resp['title']
        image = resp['image']
        counter += 1
        newFood = Food(name = name, food_id = f, image_url = image, calories = calories, carbs = carbohydrates, proteins = proteins,  fats = fats)
        db.session.add(newFood)
        meal.foods.append(newFood)
    db.session.commit()
    return redirect(f'/users/{user.id}')

def get_Cumulative(user_id):
    meals = Meal.query.filter_by(user_id = user_id)
    runningCalories = 0
    runningCarbs = 0
    runningProteins = 0
    runningFats = 0
    for meal in meals:
        for food in meal.foods:
            runningCalories += food.calories
            runningCarbs += food.carbs
            runningProteins += food.proteins
            runningFats += food.fats
    return [runningCalories, runningCarbs, runningProteins, runningFats]