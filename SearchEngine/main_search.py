import myfunctions
import website_dicts
from index import Index

def main():

    # choose a website to use
    v = website_dicts.vm009
    #v = website_dicts.uos

    # create crawler
    index = Index(v["custom_header_name"],v["index_path"])
    
    # choose a search line
    search_line = "The Platypus ANDNOT Australia"

    corrected = index.correct_string(search_line)
    if corrected:
        print("Results for: ", corrected)
        search_line = corrected

    # search
    # total_hits, total_pages, pagenumber, last_page, results = mycrawler.search(search_line)
    results = index.search(search_line)
    print(results)
"""

    # if no results for search line but correctable
    if value: 
        myfunctions.print_total(0, search_line)
        print(f"Did you mean: {value}?\n")
        myfunctions.print_results(value, total_hits,results)
    else: # if normal result
        myfunctions.print_results(search_line, total_hits,results)
"""

if __name__ == "__main__":
    main()