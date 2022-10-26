from models import db, connect_db, User, Meal, Food, Preference, User_Preference, Meal_Food, PREFERENCES, INTOLERANCES
from flask import Flask, redirect, render_template, session, flash, request

def validateSignUp(form):
    if form.validate():
        if User.query.filter_by(username = form.username.data).count() > 0:
            return "Username Taken. Please Choose Another."
        elif User.query.filter_by(email = form.email.data).count() > 0:
            return "Email Taken. Please Choose Another."
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
            return newUser
    else:
        return False

def validateLogIn(form):
    if form.validate():
        user = User.authenticate(form.username.data, form.password.data)
        if user:
            if session["setPreference"] == False:
                return f'/users/{user.id}/preference'
            else:
                session["username"] = user.username
                return f'/users/{user.id}'
    else:
        return False

def validatePreferences(form, user_id):
    user = User.query.get_or_404(user_id)
    preferences = User_Preference.query.filter_by(user_id = user_id)
    for p in PREFERENCES:
        val = True
        resp = form.get(p)
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
    user.totalcalories = int(float(form['totalcalories']))
    user.totalcarbs = int(float(form['totalcarbs']))
    user.totalproteins = int(float(form['totalproteins']))
    user.totalfats = int(float(form['totalfats']))
    db.session.commit()
    session["setPreference"] = True
    return f'/users/{user.id}'
    
def getCumulative(user_id):
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