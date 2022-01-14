from turtle import title
from flask_login    import UserMixin
from project        import db

class Book(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    code = db.Column(db.String(100), unique=True)
    author = db.Column(db.String(100))
    title = db.Column(db.String(100))
    stock = db.Column(db.Integer)