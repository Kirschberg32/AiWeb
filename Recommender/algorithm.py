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
    def _recommender_algorithm(cls, df, username, k = 10):
        """
        Calculates the best recommendations for a user using a user-centered algorithm.

        Pseudocode:
            1. distances = [(user, euclidian_distance(user[given_user != 0], given_user[given_user != 0])) for user in other_users if user is not given_user]
            2. k_user, d = sort_by_distance_ascending(distances)[:k=10]
            3. k_values_scaled = k_user[given_user == 0]^(-1) / sum(k_user[given_user == 0]) if sum != 0 else skip division
            4. k_values_weighted = k_values_scaled * d[given_user == 0]
            5. predictions = sum (k_values_weighted, axis = movies)
            6. return sort_descending(predictions)
        
        Args:
            df (pd.DataFrame): the dataframe to use for calculations (a copy of cls._dframe_matrix)
            username (str): The username of the user to recommend for
            k (int>0): The number of users to use for the predictions

        Returns:
            recommendations (list): A sorted list of movie_ids
        """

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
            if len(k_nearest) > k:
                k_nearest = k_nearest[:k]

        # k_nearest contains k tuples
        # k_names contains k names
        k_names = [n for d,n in k_nearest]
        distances = np.array([d + 1 for d,n in k_nearest])
            
        # for all not rated movies derive prediction from ratings of similar users
            
        df_not_rated = df[df[username] == 0][k_names]

        # scale distances so higher value is closer and then let them sum up to 1
        distances = (np.power(distances,-1) )
        if np.sum(distances) != 0:
            distances = distances/np.sum(distances) 

        # weighted by distance, highest is best
        df_not_rated = df_not_rated.mul(distances, axis='columns')
        prediction = df_not_rated.sum(axis='columns')

        df_not_rated['prediction'] = prediction

        # sort predictions best on top
        sorted = df_not_rated.sort_values(by='prediction', ascending=False)

        return list(sorted.index)
    
    @classmethod
    def test_recommender(cls):
        """
        A test for _recommender_algorithm
        """

        # create a test dataframe
        usernames = ["user1","user2","user3", "user4"]
        all_movies = [1,2,3,4,5,6,7,8,9,10]
        ratings = [[(1,5),(2,5),(3,5)],[(2,3),(3,5),(4,5)],[(8,5),(9,5),(10,5)],[(2,5)]]
        expectation = [3,1,4,5,6,7,8,9,10]

        df = pd.DataFrame(0, columns = usernames,index = [id for id in all_movies],dtype = float)

        for u,r in zip(usernames,ratings):
            for id,val in r:
                if id in df.index:
                    df.loc[id, u] = val

        print("Test Dataframe: \n", df)

        # run a recommendation test
        results = cls._recommender_algorithm(df, "user4", k = 2)

        print("\nTest 1:")
        if (results == expectation):
            print("successful")
        else:
            print("not successful")
            print("Result: ", results)
            print("Expectation: ", expectation)

if __name__ == "__main__":
    
    RecommenderAlgorithm.test_recommender()