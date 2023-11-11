import myfunctions
import website_dicts

def main():

    # choose a website to use
    v = website_dicts.vm009
    #v = website_dicts.uos

    # create new crawler and let is crawl
    myfunctions.create_and_crawl(v["custom_header_name"],v["index_path"], v["start_url"])

if __name__ == "__main__":
    main()