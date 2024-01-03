# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request
from flask_user import login_required, UserManager, current_user
from sqlalchemy.exc import IntegrityError

from models import db, User, Movie, MovieRating
from read_data import check_and_read_data

# Class-based application configuration
class ConfigClass(object):
    """ Flask application config """

    # Flask settings
    SECRET_KEY = 'This is an INSECURE secret!! DO NOT use this in production!!'

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'sqlite:///movie_recommender.sqlite'  # File-based SQL database
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # Avoids SQLAlchemy warning

    # Flask-User settings
    USER_APP_NAME = "Movie Recommender"  # Shown in and email templates and page footers
    USER_ENABLE_EMAIL = False  # Disable email authentication
    USER_ENABLE_USERNAME = True  # Enable username authentication
    USER_REQUIRE_RETYPE_PASSWORD = True  # Simplify register form

# Create Flask app
app = Flask(__name__)
app.config.from_object(__name__ + '.ConfigClass')  # configuration
app.app_context().push()  # create an app context before initializing db
db.init_app(app)  # initialize database
db.create_all()  # create database if necessary
user_manager = UserManager(app, db, User)  # initialize Flask-User management

@app.cli.command('initdb')
def initdb_command():
    global db
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    # render home.html template
    return render_template("home.html")


# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def movies_page():

    # String-based templates
    if request.method == 'POST':
        movie_id, rating = request.form.get('rating').split(",")

        # check whether user already rated this movie
        rated = current_user.get_rating(int(movie_id), False)

        try:
            if rated != 0: # change rating
                if rated.rating == int(rating): # delete rating
                    db.session.delete(rated)
                else:
                    rated.rating = rating

            if rated == 0:
                #Safe it to Database
                movie_rating = MovieRating(movie_id=int(movie_id),rating=int(rating),user_id=current_user.username)
                db.session.add(movie_rating)

            db.session.commit()
        except IntegrityError:
            pass

    # first 10 movies
    movies = Movie.query.limit(10).all()

    #for m in movies:
    #    print(m.title, len(m.ratings))

    # only Romance movies
    # movies = Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()

    # only Romance AND Horror movies
    # movies = Movie.query\
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Romance')) \
    #     .filter(Movie.genres.any(MovieGenre.genre == 'Horror')) \
    #     .limit(10).all()

    # check which movies are rated by the user
    ratings = [current_user.get_rating(m.id,True) for m in movies] # 0 for no rating

    return render_template("movies.html", movies = zip(movies,ratings))


# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
