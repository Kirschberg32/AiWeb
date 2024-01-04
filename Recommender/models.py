from flask_sqlalchemy import SQLAlchemy
from flask_user import UserMixin

db = SQLAlchemy()

# Define the User data-model.
# NB: Make sure to add flask_user UserMixin as this adds additional fields and properties required by Flask-User
class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')

    # User authentication information. The collation='NOCASE' is required
    # to search case insensitively when USER_IFIND_MODE is 'nocase_collation'.
    username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False, server_default='')
    email_confirmed_at = db.Column(db.DateTime())

    # User information
    first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
    last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')

    # contact to moviedata
    ratings = db.relationship('MovieRating', backref='user', lazy=True)

    def get_rating(self, movie_id, as_num = True):
        for r in self.ratings:
            if r.movie_id == movie_id:
                if as_num:
                    return r.rating
                return r
        return 0

class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True, unique=True)
    title = db.Column(db.String(100, collation='NOCASE'), nullable=False)
    genres = db.relationship('MovieGenre', backref='movie', lazy=True)
    links = db.relationship('MovieLink', backref='movie', lazy=True)
    tags = db.relationship('MovieTag', backref='movie', lazy=True)
    ratings = db.relationship('MovieRating', backref='movie', lazy=True)

    def average_ratings(self):
        """ returns the average rating for this movie rounded. 0.0 if no rating."""
        if len(self.ratings) > 0:
            return round(sum([rating.rating for rating in self.ratings])/(len(self.ratings)),1)
        return 0.0

class MovieGenre(db.Model):
    __tablename__ = 'movie_genres'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    genre = db.Column(db.String(255), nullable=False, server_default='')

class MovieLink(db.Model):
    __tablename__ = 'movie_link'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    link = db.Column(db.String(255), nullable=False, server_default='')

class MovieTag(db.Model):
    __tablename__ = 'movie_tag'
    id = db.Column(db.Integer, primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False)
    tag = db.Column(db.String(255), nullable=False, server_default='')

class MovieRating(db.Model):
    __tablename__ = 'movie_rating'
    id = db.Column(db.Float)
    movie_id = db.Column(db.Integer, db.ForeignKey('movies.id'), nullable=False, primary_key=True)
    rating = db.Column(db.Integer, nullable=False, server_default='')
    user_id = db.Column(db.Integer, db.ForeignKey('users.username'), nullable=False, primary_key = True)