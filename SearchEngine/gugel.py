# myapp.py

from flask import Flask, request, render_template, session #add abort for testing
from werkzeug.exceptions import HTTPException
import threading
import time
import secrets
import logging

from mylib.index import Index
from mylib import website_dicts
from mylib.updatedaemon import IndexUpdateDaemon
from mylib.myfunctions import thread_highlights

# Logging
logging.basicConfig(filename='gugel.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.info('Start gugel engine')

app = Flask(__name__, static_url_path='/static')
app.secret_key = secrets.token_hex()

# choose a website to use
v = website_dicts.uos
#v = website_dicts.test

# if you need to create a new index by crawling from the start page (same as main_create!)
#Crawler(v["custom_header_name"], v["path"]).crawl(v["start_url"])

# create index for searching
index = Index(v["custom_header_name"],v["path"])

pagelen = 15

all_search_results_dict = {}

IndexUpdateDaemon(v).start()
logger.info('Started Daemon')

def prepare():
    """
    prepare by checking whether this user already has a user_id so we can use it as key for the search results
    """

    if not 'user_id' in session:
        session['user_id'] = secrets.token_hex(16)
        all_search_results_dict[session['user_id']] = {"pagecount": 0, "match": 0, "all_matches": [], "result": [], "user_id" : session['user_id'], "last_page": False, "total":0, "q":""}
    return all_search_results_dict[session['user_id']]

@app.route("/")
def start():
    prepare()
    return render_template("search.html", pagecount = 0, result = [], num = 1)

@app.route("/search")
def search():
    """
    Do a search using argument q. Get 1 million results max (if you want to have more make sure the server can handle more). The results of the search are savid in all_search_results_dict with the user_id as key. 
    Load highlights and favicon for first page. 
    Try to correct string. 
    Finally load highlights and favicons for next page in a thread. 
    """

    g = prepare()

    g["q"] = request.args.get('q')

    # only 1m to not overwhelm RAM
    g["total"], g["result"] = index.search(g["q"],limit = 1000000) #p.total, p.pagecount, p.pagenum, p.is_last_page(), self.convert_results(p.results)
    g["pagecount"] = int(g["total"]/pagelen) + (0 if g["total"]%pagelen else 1)
    # get highlights and favicon
    end = pagelen if pagelen <= g["total"] else g["total"]
    g["all_matches"] = []
    g["all_matches"].append(index.get_highlights_and_favicon(g["result"][:end])) # (title, url, highlights, favicon_url) # ! favicon_url might be None!
    #print("\n\nresult:\n",all_matches)
    
    if g["result"]:
        match_string = str(g["total"]) + " matches estimated!"
    else:
        match_string = "No matches found!"

    # try to correct the string, and suggest the correction if there is one
    corrected_q = index.correct_string(g["q"])

    # start a thread in the background to load highlights and favicon for page 2
    reached_limit = False
    if (len(g["result"]) > pagelen): # is there a page 2
        end = pagelen*2 if pagelen*2 <= len(g["result"]) else len(g["result"])
        T = threading.Thread(target = thread_highlights, args=(index, g["result"][pagelen:end],g["all_matches"]) ,name="background load highlights and favicon")
        T.start()
    elif 1 < g["pagecount"]: # If there is no more page, even though pagecount is not reached (limit is reached)
        reached_limit = True

    return render_template("search.html", req = g["q"], req_corrected = corrected_q, match = match_string, result = g["all_matches"], pagecount = g["pagecount"], num = 1, reached_limit = reached_limit)

@app.route('/search-<q>/Page-<int:num>', methods=['POST']) # TODO find out how to have search q with ? as in
def load_page(num,q):
    """
    When user wants more results
    Wait until highlights and favicon for this page are done. Then start a thread to load them for the next page before rendering the template. 
    Also checks whether there is another page of results (when there are more than 1 million results, total can be bigger than len(results))

    Args: 
        num (int): The page to load
        q (str): The search query
    """

    g = prepare()

    reached_limit = False

    while (len(g["all_matches"]) < num): # while page not already in all_matches wait
        time.sleep(0.1)

    if (len(g["result"]) > pagelen*num): # is there another page
        end = pagelen*num + pagelen if len(g["result"]) >= pagelen*num + pagelen else len(g["result"]) # check how long page is
        if (len(g["all_matches"]) < num + 1): # do have the next page already?
            T = threading.Thread(target = thread_highlights, args=(index, g["result"][pagelen*num:end], g["all_matches"]) ,name="background load highlights and favicon")
            T.start()
    elif num < g["pagecount"]: # If there is no more page, even though pagecount is not reached (limit is reached)
        reached_limit = True

    
    return render_template('search.html', req = g["q"],match = str(g["total"]) + " matches estimated!", result=g["all_matches"], pagecount = g["pagecount"], num = num, reached_limit = reached_limit)

@app.errorhandler(Exception)
def handle_exception(e):
    # pass through HTTP errors
    logger.error(f'{e} occured') 
    if isinstance(e, HTTPException):
        return e    
    # now you're handling non-HTTP exceptions only
    return """
        <pre>Something went wrong! Try reloading the start page<br />
        <a href="{{ url_for('/') }}">Gugel</a></pre>
        """