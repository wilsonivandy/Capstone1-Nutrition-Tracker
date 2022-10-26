import requests


def complexList(name, intolerances, preferences, calorieTarget, key):
    url = 'https://api.spoonacular.com/recipes/complexSearch'
    if name:
        print("****complexListTrue")
        print(name)
        params = {
            'query': name,
            'intolerances': intolerances,
            'excludeIngredients':preferences,
            'type': type,
            'minCalories': calorieTarget * 0.5,
            'maxCalories': calorieTarget * 1.2,
            'number': 20,
            'apiKey': key
            }
    else:
        params = {
            'intolerances': intolerances,
            'excludeIngredients':preferences,
            'type': type,
            'minCalories': calorieTarget * 0.5,
            'maxCalories': calorieTarget * 1.2,
            'number': 20,
            'apiKey': key
            }
    return requests.get(url, params)

def apiFoodInfo(food_id, key):
    url = f'https://api.spoonacular.com/recipes/{food_id}/information'
    params = {
        'includeNutrition': True,
        'apiKey': key 
    }
    return requests.get(url, params).json()

def apiRecipeSteps(food_id, key):
    url = f'https://api.spoonacular.com/recipes/{food_id}/analyzedInstructions'
    params = {
        'stepBreakdown': True,
        'apiKey': key 
    }
    return requests.get(url, params).json()

def apiRecipeIngredients(food_id, key):
    ingredients_url = f'https://api.spoonacular.com/recipes/{food_id}/ingredientWidget.json'
    ingredients_params = {
        'apiKey': key 
    }
    return requests.get(ingredients_url, ingredients_params).json()
    
def apiMealPlan(totalCalories, key):
    url = 'https://api.spoonacular.com/mealplanner/generate'
    params = {
        'timeFrame': 'day',
        'targetCalories': totalCalories,
        'apiKey': key 
    }
    return requests.get(url, params).json()['meals']