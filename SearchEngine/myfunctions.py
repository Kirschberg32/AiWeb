import crawler

def create_crawler(header, index_path):
    mycrawler = crawler.Crawler(header, index_path)
    return mycrawler

def create_and_crawl(header, index_path, start_url):
    mycrawler = create_crawler(header, index_path)
    mycrawler.crawl(start_url)
    return mycrawler

def print_total(number, search_line):
    print(f"\nFound {number} total hits for '{search_line}'.")

def print_results(search_line, total_hits, results):
    # print a line with search line and total hits
    print_total(total_hits, search_line)
    # if there are hits, print title, url and a highlight
    if results:
        for t,url, high in results:
            print(f"\n{t}: {url}")
            print(high)