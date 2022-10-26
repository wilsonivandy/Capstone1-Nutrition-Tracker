from unittest import TestCase
from app import app
from forms import signUpForm, logInForm
from models import db, connect_db, User, Meal, Food, Preference, User_Preference, Meal_Food
import models

# Use test database and don't clutter tests with SQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///nutrition_planner_test'
app.config['SQLALCHEMY_ECHO'] = False

# Make Flask errors be real errors, rather than HTML pages with error info
app.config['TESTING'] = True

db.drop_all()
db.create_all()


USER_DATA = {
    "first_name": "John",
    "last_name": "Doe",
    "username": "coffeebean1",
    "password": "pass1",
    "email": "coffeebean@gmail.com"
}

USER_DATA_2 = {
    "first_name": "Jane",
    "last_name": "Doe",
    "username": "coffeebean2",
    "password": "pass2",
    "email": "coffeebean2@gmail.com"
}

class MealsTestCase(TestCase):
    """Tests for views of User Model"""
    def setUp(self):
        """Set up"""
        with app.test_client() as client:
            client.post("/signup", data=USER_DATA)
            client.post("/users/1/preference", data={"Gluten": "off",
                                        "Peanut": "off",
                                        "totalcalories": 2000,
                                        "totalcarbs": 300,
                                        "totalproteins": 100,
                                        "totalfats":44.44})
            client.post("/users/1/meal/add/breakfast", follow_redirects=True)
            client.post("/users/1/meal/add/lunch", follow_redirects=True)
            client.post("/users/1/meal/add/dinner", follow_redirects=True)
        db.session.commit()
    
    def tearDown(self):
        """Tear Down"""
        User.query.delete()
        db.session.rollback()
    
    def test_add_Meal(self):
        with app.test_client() as client:
            self.assertEqual(User.query.filter_by(username = 'coffeebean1').count(), 1)
            self.assertEqual(Meal.query.filter_by(meal = 'breakfast').count(), 1)
            self.assertEqual(Meal.query.filter_by(meal = 'lunch').count(), 1)

    def test_add_Food(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['setPreference'] = False
            url = "/users/1/meal/add/breakfast/1"
            self.assertEqual(len(Meal.query.filter_by(meal = 'breakfast').first().foods), 0)
            resp = client.post("/users/1/meal/add/breakfast/1")
            self.assertEqual(len(Meal.query.filter_by(meal = 'breakfast').first().foods), 1)
            self.assertEqual(resp.status_code, 302)

    def test_autopopulate(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['setPreference'] = False
            resp = client.post("/users/1/meal/add/autopopulate")
            self.assertEqual(len(Meal.query.filter_by(meal = 'breakfast').first().foods), 1)
            self.assertEqual(len(Meal.query.filter_by(meal = 'lunch').first().foods), 1)
            self.assertEqual(len(Meal.query.filter_by(meal = 'dinner').first().foods), 1)