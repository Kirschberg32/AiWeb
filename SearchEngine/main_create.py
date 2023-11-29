from  mylib import website_dicts
from mylib.crawler import Crawler

import sys

def main():

    # get the website to use
    try:
        v = website_dicts.find_dict(sys.argv[1])
    except IndexError:
        print("You need to enter a short term for which page to crawl out of website_dicts.py")
        exit(-1)

    if v == None:
        print(f"No entry for {sys.argv[1]}.")
    else:
        print(f"Creating the index for {v['path']}")

        mycrawler = Crawler(v["custom_header_name"], v["path"])
        mycrawler.crawl(v["start_url"])

if __name__ == "__main__":
    main()