def main():
    mycrawler = create_crawler()
    print()
    search_line = "The Platypus"
    results = mycrawler.search(mycrawler.string_to_tokens(search_line))
    print(results)


def create_crawler():
    import crawler
    start_url = "https://vm009.rz.uos.de/crawl/index.html"
    custom_header_name = 'CrawlerForSearchEngine/1.0 (myemail@uos.de)'
    mycrawler = crawler.Crawler(start_url, custom_header_name)
    mycrawler.crawl()
    return mycrawler

if __name__ == "__main__":
    main()