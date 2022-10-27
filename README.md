# Nutrition Planner App

Visit the deployed app here: http://nutrition-planner.herokuapp.com/

## Description

The website is an application that lets you track your daily nutrition, by letting the user pick foods and recipes that will suit to their daily needs. 

## Features

- Creating an account, signing in and logging out
- Setting account preferences and daily macronutrient needs
- Ability to set food allergens and intolerances. All foods and recipes shown will be adjusted for each user.
- Automatically create daily meal plan that suits one's needs
- Detailed dashboard showing chosen meals for the day and tally running calories
- Search query, add, and remove specific food(s) to/from daily planner
- View any recipe for chosen foods

These standard features are the basic necessities for anyone who wants a clear picture of their diet and nutrition. Often recipes found in other nutrition trackers do not account for intolerances or allergens. 
The ability to search for recipes, view them and their nutrition facts, is very valuable. This eliminates the need to search for individual ingredients and adding them one-by-one. This is the approach many other trackers use, and can be a troublesome routine for some people looking for a simple habit instead. 

## User Flow

The user starts on the homepage and logs in or signs up with their specific dietary requirements. From the home page (dashboard) the user is able to choose to add foods to any of three: Breakfast, Lunch, or Dinner. Then, they are redirected to the food page and can search query for recipes that suits their dietary needs. After searching, the User can add a recipe which will redirect back to the main page. Alternatively, they can view the recipe to see all the necessary steps. 
From the home page the user can also autopopulate their meal plans according to their specified customizations. The user is also able to see the total running calories and macronutrients for the day in the dashboard.

![alt text](https://github.com/wilsonivandy/Capstone1-Nutrition-Tracker/blob/main/User%20Flow.png?raw=true)

## API

API Used: Spoonacular API
https://spoonacular.com/food-api

## Technology Stack

Front-end =  CSS-Bootstrap, HTML
Back-end = Python: Flask, flask_wtf, WTForms, bcrypt, SQLAlchemy

