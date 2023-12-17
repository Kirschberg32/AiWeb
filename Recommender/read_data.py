import csv
from sqlalchemy.exc import IntegrityError
from models import Movie, MovieGenre, MovieLink, MovieTag

def check_and_read_data(db):
    # check if we have movies in the database
    # read data if database is empty
    if Movie.query.count() == 0:
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

                            # find all tags
                            with open('data/tags.csv', newline='', encoding='utf8') as csvtagsfile:
                                reader_tags = csv.reader(csvtagsfile, delimiter=',')
                                all_tags = [tag for tag in reader_tags if tag[1] == id]
                                for tag in all_tags:
                                    movie_tag = MovieTag(movie_id=id,tag=tag[2])
                                    db.session.add(movie_tag)

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