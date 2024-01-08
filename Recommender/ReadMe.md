Movie Recommender by Eosandra Grund and Fabian Kirsch

# Our Movie Recommender System
We created a Movie Recommender for the course "Artificial Intelligence and the Web"(WS23/24). It consists of SQL data management a recommendation algorithm and a flask web app. The Movie Recommender is running on an university server. 

![Example screenshot of page ](Examples/ExampleSearch.png)
Example screenshot of page 2 

## The algorithm
We decided for a user-centered algorithm, as it is known to create more personalized recommendations. The data is saved in a matrix movie x user.

Pseudocode for finding recommendations for given_user (Each user being a vector of ratings for each movie, 0 if not rated)
```
calculate distance of given_user and other_users only using values where given_user != 0
sort users by distance and take k (= 10) closest users
calculate predictions for ratings for each movie that was not rated by given_user using only the closest users. 
Return movies with the highest prediction first. 

```
Note: These predictions have to be seen in relationship to other predictions. They are not a prediction of the expected rating of given_user.
We used Euclidian distance for distance calculation and the following formula to calculate the predictions: 

``` math
p = \sum_{over movies} (users - 6 where u > 0 else 0) d
```
Where u is a list containing the k closest user vectors and d a list containg their distances to the given_user. 

## Usage
Install the requirements. Then run `flask --app recommender.py initdb` to create a sql database (Note: this might take several hours). Use `flask --app recommender.py run` to start a developmental flask server. 

## Files: 
### Folders:
* [data](data): Contains the dataset in csv files, that is used as a starting point for the sql database.
* [instance](instance): Contains the sql database. 
* [static](static): ???
* [templates](templates): Contains the html templates for the app. 

### Files:
* [algorithm.py](algorithm.py): Contains a class RecommenderAlgorithm with all methods that are needed for the recommendation algorithm (also data preprocessing etc. ).
* [movels.py](movels.py): Contains all classes used for the SQL database. 
* [read_data.py](read_data.py): Contains all functions for creating the SQL database from the csv files. 
* [recommender.py](recommender.py): Contains the flask web app. 
* [requirements.txt](requirements.txt): list of dependencies for our flask app