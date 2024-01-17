# Contains parts from: https://flask-user.readthedocs.io/en/latest/quickstart_app.html

from flask import Flask, render_template, request
from flask_user import login_required, UserManager, current_user
from sqlalchemy.exc import IntegrityError

from models import db, User, Movie, MovieRating
from read_data import check_and_read_data
from algorithm import RecommenderAlgorithm as Rec

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
page = 0
movies = []
result = []

# Create the matrix used to calculate the recommendations
Rec.create_df_matrix()

@app.cli.command('initdb')
def initdb_command():
    global db 
    """Creates the database tables."""
    check_and_read_data(db)
    print('Initialized the database.')

# The Home page is accessible to anyone
@app.route('/')
def home_page():
    global page
    global movies
    global result
    # render home.html template
    page = 0
    movies = []
    result = []
    return render_template("home.html")

def rating_check():
    movie_id, rating = request.form.get('rating').split(",")

    # check whether user already rated this movie
    rated = current_user.get_rating(int(movie_id), False)

    try:
        if rated == 0:
            #Safe it to Database
            movie_rating = MovieRating(movie_id=int(movie_id),rating=int(rating),user_id=current_user.username)
            db.session.add(movie_rating)
        else: # change rating
            if rated.rating == int(rating): # delete rating
                db.session.delete(rated)
                rating = 0
            else:
                rated.rating = rating

        db.session.commit()
    except IntegrityError:
        pass
    # save to matrix for algorithm
    Rec.add_rating(current_user.username, int(movie_id), int(rating))

    return int(movie_id), int(rating)

# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/movies', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def movies_page():
    global page
    global movies
    global result

    show = []
    # String-based templates
    if request.method == 'POST':
        if 'rating' in request.form:
            rating_check()

        elif 'load_more' in request.form:
            page = int(request.form.get('load_more'))

            show = []
            if len(result) > 10*(page+1):
                show = result[(10*page):((10*page)+10)] # show 10 per page

    else:
        # page is newly loaded
        page = 0
        movies = []
        result = Rec.recommend(current_user.username)
        show = result[:10] if len(result) > 10 else result

    # get the objects of the movies
    if show:
        print("Show: ", show)
        results = Movie.query.filter(Movie.id.in_(show)).all()

        # sort results so they are in the same order as show
        for s in show:
            for m in results:
                if s == m.id:
                    movies.append(m)
                    break

        print("Movies: ", movies)

    # check which movies are rated by the user
    ratings = [current_user.get_rating(m.id,True) for m in movies] # 0 for no rating

    return render_template("movies.html", movies = zip(movies,ratings), page = page, path_to_follow = "movies")

# The Members page is only accessible to authenticated users via the @login_required decorator
@app.route('/ratings', methods=['GET', 'POST'])
@login_required  # User must be authenticated
def rating_page():
    global page
    global movies
    global result

    movie_id = None
    rating = None
    show = []

    # String-based templates
    if request.method == 'POST':
        if 'rating' in request.form:
            movie_id, rating = rating_check()

            # change rated value
            for m_r in movies:
                if m_r[0].id == movie_id:
                    m_r[1] = rating
                    break

        elif 'load_more' in request.form:
            page = int(request.form.get('load_more'))

            show = []
            if len(result) > 10*(page+1):
                show = result[(10*page):((10*page)+10)] # show 10 per page
    else:
        # page is newly loaded
        page = 0
        movies = []
        result = current_user.ratings
        show = result[:10] if len(result) > 10 else result

    # get the objects of the movies
    if show:
        movies.extend([[r.movie, r.rating] for r in show])

    return render_template("movies.html", movies = movies, page = page, path_to_follow = "ratings")

# Start development web server
if __name__ == '__main__':
    app.run(port=5000, debug=True)
