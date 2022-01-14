from flask_login    import UserMixin
from project        import db

class Borrowed(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key=True)
    id_student = db.Column(db.Integer)
    code_borrowed = db.Column(db.String(100))
    title_borrowed = db.Column(db.String(100))
    author_borrowed = db.Column(db.String(100))
    issue_date = db.Column(db.String(10))
    return_date = db.Column(db.String(10))