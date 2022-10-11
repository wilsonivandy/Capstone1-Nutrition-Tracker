from unittest import TestCase
from app import app
from forms import signUpForm, logInForm
from models import db, connect_db, User, Meal, Food, Preference, User_Preference, Meal_Food

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
        User.query.delete()
        user = User.signup(**USER_DATA)
        db.session.add(user)
        db.session.commit()
    
    def tearDown(self):
        """Tear Down"""
        db.session.rollback()
    
    def test_signup(self):
        with app.test_client() as client:
            url = "/signup"
            resp = client.post(url, data=USER_DATA)
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(User.query.filter_by(username = 'coffeebean1').count(), 1)
            html = resp.get_data(as_text=True)
            self.assertIn('<p class="text-danger">Username Taken. Please Choose Another.</p>', html)
            resp1 = client.post(url, data=USER_DATA_2)
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
            resp1 = client.post(url, data={"username": "coffeebean1",
                                            "password": "pass2"}, follow_redirects=True)
            self.assertEqual(resp1.status_code, 200)
            html1 = resp1.get_data(as_text=True)
            self.assertIn('<p class="text-danger">Invalid username / password</p>', html1)

    def test_show_preferences(self):
        with app.test_client() as client:
            with client.session_transaction() as session:
                session['setPreference'] = False
            url = "/users/1/preference"
            resp = client.post(url, data={"Gluten": "off",
                                        "Peanut": "off",
                                        "totalCalories": 2000,
                                        "totalCarbs": 300,
                                        "totalProteins": 100,
                                        "totalFats":44.44})
            self.assertEqual(resp.status_code, 302)

    def test_home_page(self):
        with app.test_client() as client:
            client.post("/users/1/preference", data={"Gluten": "off",
                                        "Peanut": "off",
                                        "totalCalories": 2000,
                                        "totalCarbs": 300,
                                        "totalProteins": 100,
                                        "totalFats":44.44})
            url = "/users/1"
            resp = client.get(url)
            html = resp.get_data(as_text=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn('<span class="text-warning"\n            >John Doe</span\n          >', html)
    
    def test_add_Meal(self):
        with app.test_client() as client:
            client.post("/users/1/preference", data={"Gluten": "off",
                                        "Peanut": "off",
                                        "totalcalories": 2000,
                                        "totalcarbs": 300,
                                        "totalproteins": 100,
                                        "totalfats":44.44})
            user = User.query.get(1)
            # user.totalcalories = 2000
            print(user.totalcalories)
            # user = User.query.get(1)
            # # user.totalcalories = 2000
            # self.assertEqual(Meal.query.filter_by(meal = 'breakfast').count(), 0)
            # url = "/users/1/meal/add/breakfast"
            # resp = client.post(url)
            # html = resp.get_data(as_text=True)
            # self.assertEqual(Meal.query.filter_by(meal = 'breakfast').count(), 1)
            # self.assertEqual(Meal.query.filter_by(meal = 'lunch').count(), 0)
            # self.assertIn('<span class="text-warning">Breakfast</span>', html)
            