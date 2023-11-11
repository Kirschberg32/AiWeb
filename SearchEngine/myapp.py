# myapp.py

from flask import Flask, request, render_template
import main
import crawler

app = Flask(__name__)
mycrawler = main.create_crawler()

@app.route("/")
def start():
    
    return render_template("start.html")

@app.route("/search")
def search():
    
    q = request.args.get('q')
    results = mycrawler.search(mycrawler.string_to_tokens(q))
    if results:
        match = str(len(results))+" matches!"
    else:
        match = "No matches found! Try again!"
    

    return render_template("search.html", req = q, match = match, result = results)
    
    

    