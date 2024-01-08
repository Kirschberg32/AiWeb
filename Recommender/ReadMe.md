Movie Recommender by Eosandra Grund and Fabian Kirsch

# Our Movie Recommender System
We created a Movie Recommender for the course "Artificial Intelligence and the Web"(WS23/24). It consists of SQL data management a recommendation algorithm and a flask web app. The Movie Recommender is running on an university server. 

![Example screenshot of the page showing movie recommendations. At the top is a head area having a link to the homepage a "sign_out" link and shows the current authenticated user. In the middle are the Movie recommendations, a reload link, and three movies. One shows a rating of 2/5 stars. For each movie there is the titel, the genres, user generated tags, the average user rating as well as a field to rate in stars. ](Examples/Example_Screenshot_Movies.png)
Example screenshot of the page showing movie recommendations. The Reload link lets the recommendations be calculated newly after the user rated some. If you scroll to the bottom there is a load more button to show more recommendations. 
The recommender also as a similar page showing all the movies you rated in the past with your rating. You can remove a rating by clicking on the same rating again. 

## The algorithm
We decided for a user-centered algorithm, as it is known to create more personalized recommendations. The data is saved in a matrix movie x user.

Pseudocode for finding recommendations for given_user (Each user being a vector of ratings for each movie, 0 if not rated)
``` plaintext
1. distances = [(user, euclidian_distance(user[given_user != 0], given_user[given_user != 0])) for user in other_users if user is not given_user]
2. k_user, d = sort_by_distance_ascending(distances)[:k=10]
3. k_values_weighted = rescale( k_user[given_user == 0], 0 to -5) * d # with -5 being worst, -1 best and 0 not rated
4. predictions = sum (k_values_weighted, axis = movies)
5. return sort_descending(predictions)
```

Note: These predictions have to be seen in relationship to other predictions. They are not a prediction of the expected rating of given_user.

## Usage
Install the requirements. Then run `flask --app recommender.py initdb` to create a sql database (Note: this might take several hours). Use `flask --app recommender.py run` to start a developmental flask server. 

## Files: 
### Folders:
* [data](data): Contains the dataset in csv files, that is used as a starting point for the sql database.
* [instance](instance): Contains the sql database. 
* [static](static): Contains static files, like images or .css files
* [templates](templates): Contains the html templates for the app. 

### Files:
* [algorithm.py](algorithm.py): Contains a class RecommenderAlgorithm with all methods that are needed for the recommendation algorithm (also data preprocessing etc. ).
* [movels.py](movels.py): Contains all classes used for the SQL database. 
* [read_data.py](read_data.py): Contains all functions for creating the SQL database from the csv files. 
* [recommender.py](recommender.py): Contains the flask web app. 
* [requirements.txt](requirements.txt): list of dependencies for our flask app