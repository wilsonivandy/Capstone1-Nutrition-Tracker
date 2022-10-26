from models import db, connect_db, User, Meal, Food, Preference, User_Preference, Meal_Food, PREFERENCES, INTOLERANCES
from flask import Flask, redirect, render_template, session, flash, request
from api import complexList

def getSuggestions(intolerances, preferences, calorieTarget, key):
    resp = complexList(False, intolerances, preferences, calorieTarget, key)
    return getFoodList(resp)

def getPreferences(user_id):
    intol = User_Preference.query.filter_by(user_id = user_id)
    intolerances = []
    preferences = []
    for user_pref in intol:
        pref = Preference.query.get(user_pref.preference_id).preference
        if user_pref.importance == False:
            if pref in INTOLERANCES:
                intolerances.append(pref.lower())
            if pref in PREFERENCES:
                preferences.append(pref.lower())
    exclusions = getExclusions(intolerances, preferences)
    return [intolerances, preferences, exclusions]

def getExclusions(intolerances, preferences):
    exclude = "Exclude: "
    for f in INTOLERANCES + PREFERENCES:
        if f.lower() in intolerances or f.lower() in preferences:
            exclude += f'{f} / '
    return exclude

def getQueryResults(name, intolerances, preferences, calorieTarget, key):
    resp = complexList(name, intolerances, preferences, calorieTarget, key)
    res = getFoodList(resp)
    session['queries'] = res
    return res

def resetQueries():
    if "queries" in session:
        queries = session['queries']
        session.pop('queries')
    else:
        queries = []
    return queries

def getFoodList(resp):
    res = []
    for food in resp.json()['results']:
        res.append({
            "id": food["id"],
            "name": food["title"],
            "image": food["image"],
            "calories": (food["nutrition"])["nutrients"][0]["amount"]
        })
    return res

def createMeal(user_id, type):
    if Meal.query.filter_by(meal = type, user_id = user_id).count() == 0:
        print("CREATEd MEAL")
        newMeal = Meal(meal = type, user_id = user_id)
        db.session.add(newMeal)
        db.session.commit()

    