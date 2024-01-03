from models import Movie, MovieGenre, MovieLink, MovieTag, MovieRating, User

import pandas as pd
import numpy as np

#  | username 1 | username 2 | ...
# 9869869  |   3        |   0        | ... 

def create_data_matrix(): # user x movies
    Movie.query.filter(Movie.genres.any(MovieGenre.genre == 'Romance')).limit(10).all()
    all_movies = Movie.query.all()

    all_users = User.query.all()
    usernames = [u.username for u in all_users]

    df = pd.DataFrame(0, columns = usernames,index = [m.id for m in all_movies])

    for u in all_users:
        for r in u.ratings:
            df[u.username][r.movie_id] = r.rating

    return df

def recommender_algorithm(username):
    
    df = create_data_matrix()

    k = 10

    # find similar users based on rated movies

    # drop all movies that are not rated by user
    df_rated = df[df[username] != 0]

    k_nearest = []

    # for each user calc distance, only keep 10 best
    for c in df_rated.columns:
        if c == username:
            continue
        distance = np.linalg.norm(df_rated[c]-df_rated[username])
        k_nearest.append((distance,c))
        k_nearest.sort()
        if len(k_nearest) > 10:
            k_nearest = k_nearest[:k]

    # k_nearest contains k tuples
    # k_names contains k names
    k_names = [n for d,n in k_nearest]
    distances = [d for d,n in k_nearest]
        
    # for all not rated movies derive prediction from ratings of similar users
        
    df_not_rated = df[df[username] == 0][k_names]

    # weighted by distance, then added up -> closest to zero is best
    df_not_rated = (df_not_rated - 6).where(df_not_rated <= -6, 0).mul(distances, axis='columns')
    prediction = df_not_rated.sum(axis='columns')

    df_not_rated['prediction'] = prediction

    # sort predictions best on top
    sorted = df_not_rated.sort_values(by='prediction', ascending=True)

    return list(sorted.index)