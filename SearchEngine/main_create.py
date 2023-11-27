from  mylib import website_dicts
from mylib.crawler import Crawler

def main():

    # choose a website to use
    v = website_dicts.test
    #v = website_dicts.uos

    # create new crawler and let is crawl
    mycrawler = Crawler(v["custom_header_name"], v["path"])
    mycrawler.crawl(v["start_url"])

if __name__ == "__main__":
    main()