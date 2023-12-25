from . import db
from flask_login import UserMixin

class users(db.Model, UserMixin):
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(30), nullable = False, unique = True)
    password = db.Column(db.String(500), nullable=False)
    
    def get_id(self):
        return str(self.user_id)

    def __repr__(self):
        return f'id:{self.user_id}, username:{self.username}, password:{self.password}'

class profiles(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'))
    age = db.Column(db.Integer)
    name = db.Column(db.String(30), nullable = False)
    gender = db.Column(db.String(15), nullable = False)
    searching_for = db.Column(db.String(15), nullable = False)
    about_me = db.Column(db.String())
    photo = db.Column(db.String())
    hide_profile = db.Column(db.Boolean)

    def __repr__(self):
        return f'id:{self.id}, user_id:{self.user_id}, name:{self.name}, age:{self.age}, gender:{self.gender}, searching_for:{self.searching_for}, about_me:{self.about_me}, photo:{self.password}, hide_profile:{self.hide_profile}'
        
    
