from models import db, connect_db, User, Meal, Food, Preference, User_Preference, Meal_Food, PREFERENCES, INTOLERANCES
from flask import Flask, redirect, render_template, session, flash, request
from api import apiFoodInfo, apiRecipeSteps, apiRecipeIngredients, apiMealPlan
import requests

def getFoodInfo(food_id, key):
    resp = apiFoodInfo(food_id, key)
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
    return [name, image, calories, carbohydrates, proteins, fats]

def getRecipeSteps(food_id, key):
    resp = apiRecipeSteps(food_id, key)
    steps = []
    for s in resp[0]['steps']:
        steps.append({s['number']:s['step']})
    return steps

def getRecipeIngredients(food_id, key):
    ingredients = []
    resp = apiRecipeIngredients(food_id, key)
    for i in resp['ingredients']:
        ingredients.append(f"{i['amount']['metric']['value']}" + " " + f"{i['amount']['metric']['unit']}" + " " + f"{i['name']}")
    return ingredients

def getMealPlan(user, key):
    resp = apiMealPlan(user.totalcalories, key)
    ids = []
    for r in resp:
        ids.append(r['id'])
    return ids

