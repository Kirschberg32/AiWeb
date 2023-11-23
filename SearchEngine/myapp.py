# myapp.py

from flask import Flask, request, render_template
import threading
import time
from index import Index
import website_dicts
from updatedaemon import IndexUpdateDaemon
from myfunctions import thread_highlights

app = Flask(__name__, static_url_path='/static')

# choose a website to use
v = website_dicts.uos
#v = website_dicts.test

# if you need to create a new index by crawling from the start page (same as main_create!)
#Crawler(v["custom_header_name"], v["index_path"]).crawl(v["start_url"])

# create index for searching
index = Index(v["custom_header_name"],v["index_path"])

pagecount = 0
match = 0
all_matches = []
last_page = False
total = 0
q = ""
pagelen = 15

#IndexUpdateDaemon(v).start()

@app.route("/")
def start():
    
    return render_template("search.html", pagecount = 0, result = [], num = 1)

@app.route("/search")
def search():
    global all_matches
    global pagecount
    global last_page
    global total
    global q
    global result

    all_matches = []
    q = request.args.get('q')

    # only 100k to not overwhelm RAM
    total, result = index.search(q,limit = 1000000) #p.total, p.pagecount, p.pagenum, p.is_last_page(), self.convert_results(p.results)
    pagecount = int(total/pagelen) + (0 if total%pagelen else 1)
    # get highlights and favicon
    end = pagelen if pagelen <= total else total
    all_matches.append(index.get_highlights_and_favicon(result[:end])) # (title, url, highlights, favicon_url) # ! favicon_url might be None!
    #print("\n\nresult:\n",all_matches)
    
    if result:
        match = str(total) + " matches estimated!"
    else:
        match = "No matches found!"
        current_page = 1 # needed so html for "load_more" button works

    # try to correct the string, and suggest the correction if there is one
    corrected_q = index.correct_string(q)

    # start a thread in the background to load highlights and favicon for page 2
    if (len(result) > pagelen*2): # is there another page
        end = pagelen*2 if pagelen*2 <= total else total
        T = threading.Thread(target = thread_highlights, args=(index, result[pagelen:end],all_matches) ,name="background load highlights and favicon")
        T.start()

    return render_template("search.html", req = q, req_corrected = corrected_q, match = match, result = all_matches, pagecount = pagecount, num = 1)

@app.route('/load_more/Page-<int:num>', methods=['POST'])
def load_more(num):
    global all_matches
    global last_page
    global pagecount

    while (len(all_matches) < num): # while page not already in all_matches wait
        time.sleep(0.1)

    if (len(result) > pagelen*num): # is there another page
        end = pagelen*num + pagelen if len(result) >= pagelen*num + pagelen else len(result) # check how long page is
        if (len(all_matches) < num + 1): # do have the next page already?
            T = threading.Thread(target = thread_highlights, args=(index, result[pagelen*num:end], all_matches) ,name="background load highlights and favicon")
            T.start()
    
    return render_template('search.html', req = q,match = str(total) + " matches estimated!", result=all_matches, pagecount = pagecount, num = num)
    