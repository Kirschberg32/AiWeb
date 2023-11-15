# myapp.py

from flask import Flask, request, render_template
import main_create
import myfunctions
import website_dicts


app = Flask(__name__, static_url_path='/static')

#main_create.main()
# choose a website to use
v = website_dicts.vm009
# create crawler
mycrawler = myfunctions.create_crawler(v["custom_header_name"],v["index_path"])
match = 0
all_matches = []
offset = 15


@app.route("/")
def start():
    
    return render_template("search.html")

@app.route("/search")
def search():
    global all_matches
    
    q = request.args.get('q')
    value, total_hits, results = mycrawler.search(q)
    all_matches = results
    
    if results:
        match = str(total_hits) + " matches!"
    else:
        match = "No matches found! Try again!"

    return render_template("search.html", req = q, match = match, result = results[:15], all_matches = all_matches, offset = offset)

@app.route('/load_more/<offset_range>', methods=['POST'])
def load_more(offset_range):
    global all_matches
    global offset

    offset_start, offset_end = map(int, offset_range.split('-'))
    
    offset += int(request.form.get('offset', 0))
    
    #Upper and lower bound for the Offset
    if (offset < 15):
        offset = 15     
    if (offset_end > len(all_matches)):
        offset = len(all_matches) - len(all_matches) % 15
        
    next_matches = all_matches[offset_start:offset_end]  # get the next 15 matches
    
    return render_template('search.html', match = str(len(all_matches)) + " matches!", result=next_matches, all_matches = all_matches, offset = offset)
    

    
    
    

    