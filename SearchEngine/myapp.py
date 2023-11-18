# myapp.py

from flask import Flask, request, render_template
from crawler import Crawler
from index import Index
import website_dicts
from daemon import MyDaemon

app = Flask(__name__, static_url_path='/static')

# choose a website to use
v = website_dicts.vm009

# if you need to create a new index by crawling from the start page (same as main_create!)
# Crawler(v["custom_header_name"], v["index_path"]).crawl(v["start_url"])

# create index for searching
index = Index(v["custom_header_name"],v["index_path"])

pagecount = 0
match = 0
all_matches = []
last_page = False
total = 0
q = ""

daemon = MyDaemon(v).start()

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

    all_matches = []
    q = request.args.get('q')

    total, pagecount, current_page,last_page, result = index.search(q) #p.total, p.pagecount, p.pagenum, p.is_last_page(), self.convert_results(p.results)
    all_matches.append(result) # (title, url, highlights, favicon_url) # ! favicon_url might be None!
    #print("\n\nresult:\n",all_matches)
    
    if result:
        match = str(total) + " matches estimated!"
    else:
        match = "No matches found!"
        current_page = 1 # needed so html for "load_more" button works

    # try to correct the string, and suggest the correction if there is one
    corrected_q = index.correct_string(q)

    return render_template("search.html", req = q, req_corrected = corrected_q, match = match, result = all_matches, pagecount = pagecount, num = current_page)

@app.route('/load_more/Page-<int:num>', methods=['POST'])
def load_more(num):
    global all_matches
    global last_page
    global pagecount
    # global total je nachdem ob wir das aktualisieren wollen

    if (len(all_matches) < num):
        _, pagecount, _,last_page,result = index.search(q, page = num)
        all_matches.append(result)
    
    return render_template('search.html', req = q,match = str(total) + " matches estimated!", result=all_matches, pagecount = pagecount, num = num)
    