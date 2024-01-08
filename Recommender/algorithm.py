from models import Movie, MovieGenre, MovieLink, MovieTag, MovieRating, User

import pandas as pd
import numpy as np

#  | username 1 | username 2 | ...
# 9869869  |   3        |   0        | ... 

class RecommenderAlgorithm:
    """
    A class containing all methods to preprocess data for the recommender algorithm. 

    Attributes:
        _dframe_matrix (pd.DataFrame): A pandas Dataframe having all usernames as column names and movie_ids as indices. 
        _genres (list): A list of strings containing all genres. This is used to give best predictions for each genre. 
        _best_recommendations (list): A list of movie_ids that are the best recommendations for all genres.
    """

    _dframe_matrix = None

    _genres = ['Action', 'Adventure', 'Animation', 'Children', 'Comedy', 'Crime', 
               'Documentary', 'Drama', 'Fantasy', 'Film-Noir', 'Horror', 'Musical', 
               'Mystery', 'Romance', 'Sci-Fi', 'Thriller', 'War', 'Western']
    
    # _best_recommendations = [] # to calculate new each start with current data
    # This is using the base dataset from the csv files, so you do not have to let it be calculated each time you start the program
    _best_recommendations = [318, 356, 296, 2571, 593, 260, 110, 2959, 527, 480, 
                             1196, 589, 50, 1, 2858, 4993, 1210, 47, 2028, 7153, 457, 608, 
                             2762, 588, 364, 4306, 590, 380, 1214, 595, 1073, 1617, 32587, 1201, 5669, 8464]

    @classmethod
    def create_df_matrix(cls): # user x movies
        """
        creates the cls_dframe_matrix when it is not created yet by reading in data from the SQL database. 
        """

        if cls._dframe_matrix == None:
            all_movies = Movie.query.all()

            all_users = User.query.all()
            usernames = [u.username for u in all_users]

            df = pd.DataFrame(0, columns = usernames,index = [m.id for m in all_movies],dtype = float)

            for u in all_users:
                for r in u.ratings:
                    if r.movie_id in df.index:
                        df.loc[r.movie_id, u.username] = r.rating
            cls._dframe_matrix = df

    @classmethod
    def get_df_matrix(cls):
        """
        Returns:
            A deepcopy of the matrix for usage, so the original one is not changed by accident.
        """
        if not isinstance(cls._dframe_matrix, pd.DataFrame):
            cls.create_df_matrix()
        return cls._dframe_matrix.copy(deep=True)

    @classmethod
    def add_user(cls, username):
        """
        adds a column named username to the matrix with default values 0.

        Args:
            username (str): The username of the user to add
        """
        if not isinstance(cls._dframe_matrix, pd.DataFrame):
            cls.create_df_matrix()
        cls._dframe_matrix = cls._dframe_matrix.assign(**{username: 0.0})

    @classmethod
    def user_rated(cls, username):
        """
        Checks whether there are any ratings in the dataframe for username. 
        
        Args:
            username (str): The username of the user to check

        Returns:
            truth (bool): True if rated before else False
        """
        if not isinstance(cls._dframe_matrix, pd.DataFrame):
            cls.create_df_matrix()
        if username not in cls._dframe_matrix.columns:
            return False
        if cls._dframe_matrix.loc[:,(username)].any():
            return True
        return False

    @classmethod
    def add_rating(cls, username, movie_id, rating):
        """
        Adds a rating to the matrix by changing a certain value. Users are usually added with their first rating, or after a restart.
        
        Args:
            username (str): The username of the user to add the rating for (column)
            movie_id (int): The movie_id of the movie that was rated (index)
            rating (0<=int<=5): The rating that was given (value)
        """
        if not isinstance(cls._dframe_matrix, pd.DataFrame):
            cls.create_df_matrix()
        if username not in cls._dframe_matrix.columns:
            cls.add_user(username)
        cls._dframe_matrix.loc[movie_id, username] = rating

    @classmethod
    def recommend(cls, username):
        """
        Recommend something for a user. Checks whether there are ratings for the user. Recommends best for each genre if there are no ratings. 
        
        Args:
            username (str): The username of the user to recommend for

        Returns:
            recommendations (list): A sorted list of movie_ids
        """

        df = cls.get_df_matrix()

        if cls.user_rated(username):
            return cls._recommender_algorithm(df, username)
        
        # recommend best rated movies
        return cls._recommend_best(df)
    
    @classmethod
    def _recommend_best(cls, df):
        """
        Calculates the 2 best recommendations for each genre (no duplicates), or returns them if they are saved.
        
        Args:
            df (pd.DataFrame): the dataframe to use for calculations (a copy of cls._dframe_matrix)
        
        Returns:
            recommendations (list): A sorted list of movie_ids
        """

        if cls._best_recommendations:
            return cls._best_recommendations

        sum_rating = df.sum(axis=1)
        df['Sum'] = sum_rating
        best = []

        for g in cls._genres:
            movies = [ m.id for m in Movie.query.filter(Movie.genres.any(MovieGenre.genre == g)).all()]
            # choose most rated movies and best rated movies
            df_genre = df.loc[movies,('Sum')]
            genre_list = list(zip(df_genre.index, df_genre.tolist()))
            genre_list.sort(key=lambda x: x[1], reverse = True) # [[id1, sum1], [id2, sum2], ...]

            # find 2 best sum movies that are not yet in best
            count = 0
            for id, sum in genre_list:

                # check whether this movie is already in best
                found = False
                for idb, _ in best:
                    if id == idb:
                        found = True
                        break
                if found:
                    continue

                else:
                    best.append([id,sum])
                    count += 1
                if count >= 2:
                    break
            
        # remove sum value from best
        best.sort(key=lambda x: x[1], reverse=True)
        only_id = [id for id, _ in best]

        cls._best_recommendations = only_id
        return only_id

    @classmethod
    def _recommender_algorithm(cls, df, username):
        """
        Calculates the best recommendations for a user using a user-centered algorithm.

        Pseudocode:
            calculate distance of given_user and other_users only using values where given_user != 0
            sort users by distance and take k (= 10) closest users
            calculate predictions for ratings for each movie that was not rated by given_user using only the closest users. 
            Return movies with the highest prediction first. 

        Formula predictions:
            p = \sum_{over movies} (users - 6 where u > 0 else 0) d
        
        Args:
            df (pd.DataFrame): the dataframe to use for calculations (a copy of cls._dframe_matrix)
            username (str): The username of the user to recommend for

        Returns:
            recommendations (list): A sorted list of movie_ids
        """

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
        df_not_rated = (df_not_rated - 6).where(df_not_rated <= -6, 0).mul(distances, axis='columns') # TODO
        prediction = df_not_rated.sum(axis='columns')

        df_not_rated['prediction'] = prediction

        # sort predictions best on top
        sorted = df_not_rated.sort_values(by='prediction', ascending=False)

        return list(sorted.index)