# myapp.py

from flask import Flask, request, render_template
import main_create
import myfunctions
import website_dicts
from urllib.parse import unquote

app = Flask(__name__, static_url_path='/static')

#main_create.main()


# choose a website to use
v = website_dicts.vm009
# create crawler
mycrawler = myfunctions.create_crawler(v["custom_header_name"],v["index_path"])
pagecount = 0
match = 0
all_matches = []
last_page = False
total = 0
q = ""


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

    total, pagecount, current_page,last_page, result = mycrawler.search(q) #p.total, p.pagecount, p.pagenum, p.is_last_page(), self.convert_results(p.results)
    all_matches.append(result)
    #print("\n\nresult:\n",all_matches)

    
    if result:
        match = str(total) + " matches estimated!"
    else:
        match = "No matches found!"
        current_page = 1 # needed so html for "load_more" button works

    # try to correct the string, and suggest the correction if there is one
    corrected_q = mycrawler.correct_string(q)
    if corrected_q:
        match += f" Do you mean {corrected_q}?" # start Search for corrected_q when clicking on it

    return render_template("search.html", req = q , match = match, result = all_matches, pagecount = pagecount, num = current_page)

@app.route('/load_more/Page-<int:num>', methods=['POST'])
def load_more(num):
    global all_matches
    global last_page
    global pagecount
    # global total je nachdem ob wir das aktualisieren wollen

    if (len(all_matches) < num):
        _, pagecount, _,last_page,result = mycrawler.search(q, page = num)
        all_matches.append(result)
    
    return render_template('search.html', req = q,match = str(total) + " matches estimated!", result=all_matches, pagecount = pagecount, num = num)
    

    
    
    

    