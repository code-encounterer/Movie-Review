from app import db, login_manager
from flask_login import UserMixin

@login_manager.user_loader
def load_user(id):
    return User.query.filter_by(id=id).first()

feedback = db.Table('feedback',
        db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
        db.Column('movie_id', db.Integer, db.ForeignKey('movie.id')),
        db.Column('review', db.Text(500)))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    reviewed = db.relationship('Movie', secondary=feedback, backref='reviewer')
    
    def __repr__(self):
        return f"<User {self.name}, {self.email}>"

class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<Movie {self.name}>"