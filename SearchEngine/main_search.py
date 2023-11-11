import myfunctions
import website_dicts

def main():

    # choose a website to use
    v = website_dicts.vm009
    #v = website_dicts.uos

    # create crawler
    mycrawler = myfunctions.create_crawler(v["custom_header_name"],v["index_path"])
    
    # choose a search line
    search_line = "The Platypus ANDNOT Australia"

    # search
    value, total_hits, results = mycrawler.search(search_line)

    # if no results for search line but correctable
    if value: 
        myfunctions.print_total(0, search_line)
        print(f"Did you mean: {value}?\n")
        myfunctions.print_results(value, total_hits,results)
    else: # if normal result
        myfunctions.print_results(search_line, total_hits,results)

if __name__ == "__main__":
    main()