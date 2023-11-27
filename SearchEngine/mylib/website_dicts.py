custom_header_default_name = "2.0 (myemail@uos.de)"
# custom_header crawler = "CrawlerforSearchEnginge/" + name
# custom_header searcher = "SearchEnginge Gugel/" + name

vm009 = {
    "start_url" : "https://vm009.rz.uos.de/crawl/index.html",
    "custom_header_name" : custom_header_default_name,
    "path" : "vm009"
}

uos = {
    "start_url" : "https://www.uni-osnabrueck.de/",
    "custom_header_name" : custom_header_default_name,
    "path" : "uos"
}

test = {
    "start_url" : "https://vm009.rz.uos.de/crawl/index.html",
    "custom_header_name" : custom_header_default_name,
    "path" : "test"
}

my_dicts = [vm009, uos, test]

def find_dict(path):
    """ searches for a dict with "path" = path """

    for d in my_dicts:
        if d["path"] == path:
            return d
        
    return None