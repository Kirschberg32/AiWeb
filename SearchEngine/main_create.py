import website_dicts
import crawler

def main():

    # choose a website to use
    v = website_dicts.vm009
    #v = website_dicts.uos

    # create new crawler and let is crawl
    mycrawler = crawler.Crawler(v["custom_header_name"], v["index_path"])
    mycrawler.crawl(v["start_url"])

if __name__ == "__main__":
    main()