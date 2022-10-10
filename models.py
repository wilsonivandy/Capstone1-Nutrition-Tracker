from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


bcrypt = Bcrypt()
db = SQLAlchemy()


def connect_db(app):
    """Connect to database."""

    db.app = app
    db.init_app(app)


class User(db.Model):
    __tablename__ = 'user'

    @classmethod
    def signup(cls, username, password, email, first_name, last_name):
        hashed = bcrypt.generate_password_hash(password)
        hashed_utf8 = hashed.decode("utf8")
        # call the userform properties
        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
    
    @classmethod
    def authenticate(cls, username, password):
        user = User.query.filter_by(username = username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            return user
        else:
            return False

    id = db.Column(db.Integer,
            primary_key=True,
            autoincrement=True)
    first_name = db.Column(db.String(100),
                      nullable=False,
                      unique=False)
    last_name = db.Column(db.String(100),
                      nullable=True,
                      unique=False)
    username = db.Column(db.String(100),
                      nullable=False,
                      unique=True)
    password = db.Column(db.String(100),
                      nullable=False,
                      unique=False)
    email = db.Column(db.String(100),
                      nullable=False,
                      unique=False)
    totalcalories = db.Column(db.Integer)
    totalcarbs = db.Column(db.Integer)
    totalproteins = db.Column(db.Integer)
    totalfats = db.Column(db.Integer)
    preferences = db.relationship('Preference', secondary='userpreference', backref='users')

class Meal(db.Model):
    __tablename__ = 'meal'

    id = db.Column(db.Integer,
            primary_key=True,
            autoincrement=True)
    meal = db.Column(db.String(100),
                      nullable=False,
                      unique=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))
    foods = db.relationship('Food', secondary='mealfood', backref='meals')

class Food(db.Model):
    __tablename__ = 'food'  

    id = db.Column(db.Integer,
            primary_key=True,
            autoincrement=True)
    food_id = db.Column(db.Integer)
    name = db.Column(db.String(200),
                      nullable=False,
                      unique=False)
    image_url = db.Column(db.String(100),
                      nullable=False,
                      unique=False)
    calories = db.Column(db.Integer,
            autoincrement=True)
    proteins = db.Column(db.Integer,
            autoincrement=True)
    carbs = db.Column(db.Integer,
            autoincrement=True)
    fats = db.Column(db.Integer,
            autoincrement=True)

class Preference(db.Model):
    __tablename__ = 'preference'
    id = db.Column(db.Integer,
            primary_key=True,
            autoincrement=True)
    preference = db.Column(db.String(100),
                      nullable=False,
                      unique=False)
    foods = db.relationship('Food', secondary='preferencefood', backref='preferences')

class Meal_Food(db.Model):
    __tablename__ = 'mealfood'
    id = db.Column(db.Integer,
        primary_key=True,
        autoincrement=True)
    meal_id = db.Column(db.Integer, db.ForeignKey('meal.id', ondelete="CASCADE"))
    food_id = db.Column(db.Integer, db.ForeignKey('food.id', ondelete="CASCADE"))

class User_Preference(db.Model):
    __tablename__ = 'userpreference'
    id = db.Column(db.Integer,
            primary_key=True,
            autoincrement=True)
    importance = db.Column(db.Boolean)
    preference_id = db.Column(db.Integer, db.ForeignKey('preference.id', ondelete="CASCADE"))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete="CASCADE"))

class Preference_Food(db.Model):
    __tablename__ = 'preferencefood' 
    id = db.Column(db.Integer,
            primary_key=True,
            autoincrement=True) 
    preference_id = db.Column(db.Integer, db.ForeignKey('preference.id', ondelete="CASCADE"))
    food_id = db.Column(db.Integer, db.ForeignKey('food.id', ondelete="CASCADE"))

        