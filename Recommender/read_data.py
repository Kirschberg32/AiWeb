import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, MovieLink, MovieTag, MovieRating, User

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if database is empty
    if Movie.query.count() == 0:
        check_and_read_ratings(db)
        check_and_read_tags(db)
        check_and_read_movie_and_link(db)

def check_and_read_movie_and_link(db):
    # read movies from csv
    with open('data/movies.csv', newline='', encoding='utf8') as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        with open('data/links.csv', newline='', encoding='utf8') as csvlinkfile:
            reader_link = csv.reader(csvlinkfile, delimiter=',')

            count = 0
            count_link = 0

            for row, row_link in zip(reader,reader_link):
                if count > 0:
                    try:

                        # create movie
                        id = row[0]
                        title = row[1]
                        movie = Movie(id=id, title=title)
                        db.session.add(movie)

                        # create genre
                        genres = row[2].split('|')  # genres is a list of genres
                        for genre in genres:  # add each genre to the movie_genre table
                            movie_genre = MovieGenre(movie_id=id, genre=genre)
                            db.session.add(movie_genre)

                        # check to find id link
                        movieId = row_link[0]
                        if id == movieId:

                            # create urls
                            imdbId = row_link[1]
                            tmdbId = row_link[2]

                            count_link += 1

                            if tmdbId:
                                base = "https://www.themoviedb.org/movie/"
                                str_link = base + str(tmdbId)
                                movie_link = MovieLink(movie_id=id,link = str_link)
                                db.session.add(movie_link)
                            elif imdbId:
                                base = "http://www.imdb.com/title/tt"
                                str_link = base + str(imdbId)
                                movie_link = MovieLink(movie_id=id,link = str_link)
                                db.session.add(movie_link)

                        else:
                            pass
                            # search

                        db.session.commit()  # save data to database

                    except IntegrityError:
                        print("Ignoring duplicate movie: " + title)
                        db.session.rollback()
                        pass
                count += 1
                if count % 100 == 0:
                    print(count, " movies read")


def check_and_read_tags(db):
    print("Now reading tags.")
    #read tags from csv
    with open('data/tags.csv', newline='', encoding='utf8') as file:
        reader = csv.reader(file, delimiter=',')

        count = 0

        for tag in reader:
            if count > 0:
                
                try:
                    movie_tag = MovieTag(movie_id=tag[1],tag=tag[2])
                    db.session.add(movie_tag)
                    db.session.commit()

                except IntegrityError:
                    print("Ignoring duplicate tag: " + tag[2])
                    db.session.rollback()
                    pass

            count += 1
            if count % 100 == 0:
                print(count, " tags read")
        

def check_and_read_ratings(db):
    print("Now reading ratings.")
    #read ratings from csv
    with open('data/ratings.csv', newline='', encoding='utf8') as file: #TODO short for testing
        reader = csv.reader(file, delimiter=',')

        user_counter = 0
        count = 0

        for rating in reader:
            if count > 0:
                
                try:
                    # check if new user (ratings are sorted by user!)
                    if user_counter < int(rating[0]):
                        user_counter = int(rating[0])
                        user = User(active=0,username="database" + rating[0])
                        db.session.add(user)
                        db.session.commit()

                except IntegrityError:
                    print("\nIgnoring duplicate User: ")
                    print("userId: ", rating[0])
                    print("user_counter: ", user_counter)

                    db.session.rollback()
                    pass

                try:

                    movie_rating = MovieRating(movie_id=rating[1],rating=rating[2],user_id="database" + rating[0])
                    db.session.add(movie_rating)

                    db.session.commit()

                except IntegrityError:
                    print("\nIgnoring duplicate rating for movie: ")
                    print("userId: ", rating[0])
                    print("movieId: ", rating[1])

                    db.session.rollback()
                    pass

            count += 1
            if count % 100 == 0:
                print(count, " ratings read")