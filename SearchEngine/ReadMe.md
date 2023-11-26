Search Engine by Eosandra Grund and Fabian Kirsch



## Files: 
### Folders:
* [Code](Code): Folder with different Plots from runs and tests
  * [crawler.py](Code/crawler.py): The web crawler to gather information from websites
  * [index.py](Code/index.py): The index writer and searcher
  * [myfunctions.py](Code/myfunctions.py):
  * [myhighlighter.py](Code/myhighlighter.py):
  * [queuethread.py](Code/queuethread.py):
  * [updatedaemon.py](Code/updatedaemon.py):
  * [website_dicts.py](Code/website_dicts.py):
* [Index](Index): contains the index for different Websites
* [static](static): contains the static files
  * [images](static/images): folder for saved images
  * [mystyle.css](static/mystyle.css): css file used in html templates	
* [templates](templates): contains the html templates for the search engine

* [gugel.py](gugel.py): contains the flask app
* [gugel.wsgi](gugel.wsgi): wsgi file to run our gugel.py on the server
* [main_create.py](main_create.py): Creates a crawler and crawls given page to add it into the index
* [requirements.txt](requirements.txt): list of dependencies for our flask app
