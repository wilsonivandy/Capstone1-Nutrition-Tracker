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

class UserViewsTestCase(TestCase):
    """Tests for views of User Model"""
    def setUp(self):
        """Set up"""
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['setPreference'] = False
                session['username'] = "coffeebean1"
            client.post("/signup", data=USER_DATA, follow_redirects=True)
            client.post("/users/1/preference", data={"Gluten": "off",
                                                    "Peanut": "off",
                                                    "totalcalories": 2000,
                                                    "totalcarbs": 300,
                                                    "totalproteins": 100,
                                                    "totalfats":44.44})
        db.session.commit()
    
    def tearDown(self):
        """Tear Down"""
        User.query.delete()
        db.session.rollback()
    
    def test_signup(self):
        with app.test_client() as client:
            self.assertEqual(User.query.filter_by(username = 'coffeebean1').count(), 1)
            resp1 = client.post("/signup", data=USER_DATA_2)
            self.assertEqual(resp1.status_code, 302)
            self.assertEqual(User.query.filter_by(last_name = 'Doe').count(), 2)

    def test_login(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['setPreference'] = True
            url = "/login"
            resp = client.post(url, data={"username": "coffeebean1",
                                            "password": "pass1"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            html = resp.get_data(as_text=True)
            self.assertIn('<span class="text-warning"\n            >John Doe</span\n          >', html)
            resp1 = client.post(url, data={"username": "coffeebean2",
                                            "password": "pass2"}, follow_redirects=True)
            self.assertEqual(resp1.status_code, 200)
            html1 = resp1.get_data(as_text=True)
            self.assertIn('<p class="text-danger">Incorrect Username / Password</p>', html1)

    def test_show_preferences(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['setPreference'] = False
            resp = client.get("users/1/preference")
            self.assertEqual(resp.status_code, 302)

    def test_home_page(self):
        with app.test_client() as client:
            resp = client.get("/users/1")
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<span class="text-warning"\n            >John Doe</span\n          >', html)