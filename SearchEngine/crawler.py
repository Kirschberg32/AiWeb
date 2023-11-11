""" A crawler build for a simple search engine"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
from whoosh.index import create_in, exists_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser
from whoosh import scoring, qparser

class Crawler:
    """
    A crawler object that is able to crawl one server's html pages. 

    Attributes: 
        start_url (str): The url to start crawling from
        url_stack_same_server (list): a list containing all the found urls on the same server to visit next during crawling
        url_stack (list): a list of all urls found on different servers we want to visit (stays empty after the start_url is removed at the 
            moment because we only want to crawl one server)
        urls_visited (list): a list with all the urls that where visited already by this crawler object
        index_path (str): A directory of where to save or load the whoosh index
        preliminary_index (list): A temporary database for index information before saving it in the whoosh index
        custom_headers (dict): Used as the header for requests
        timeout_default (int): The default value for timeout to reset timeout when switching to crawl a different server
        timeout_in_seconds (int): The timeout value, that can increase if the server is too slow (each time by 1). 
            If it reaches 20, the crawler will stop crawling the server. 
        scheme_list (list): A list containing all the url schemes we want to visit
    """

    def __init__(self, name, index_path : str, start_url : str = ""):
        """

        Args: 
            start_url (str): The url to start crawling from
            name (str): The name used for custom_headers, 
        
        """

        self.start_url = start_url
        self.url_stack_same_server = []
        if start_url:
            self.url_stack = [start_url,] # only used when crawling different servers too
        else:
            self.url_stack = []
        self.urls_visited = []

        self.index_path = index_path
        self.preliminary_index = []

        # custom headers to indicate, that I am a crawler (politeness)
        self.custom_headers = {'User-Agent': name}

        self.timeout_default = 2
        self.timeout_in_seconds = self.timeout_default

        self.scheme_list = ["https", "http"] # requests only works with these

    def open_index(self):
        """
        
        """
        # create folders if they do not exist
        if not os.path.isdir(self.index_path):
            os.makedirs(self.index_path)

        # if there is no existing index create a new one
        if not exists_in(self.index_path):
            # stored content to do easy highlights
            schema = Schema(title=TEXT(stored=True), content=TEXT(stored=True), url=ID(stored=True))
            index = create_in(self.index_path, schema)
        else:
            # open the existing index
            index = open_dir(self.index_path)
        return index
    
    def add_to_Index(self,soup,url):
        """
        
        """

        index = self.open_index()
        with index.writer() as writer:
            writer.add_document(title=soup.title.text, content=soup.text, url=url)

    def pre_to_Index(self):
        """
        
        """

        index = self.open_index()

        # automatically committed and closed writer
        with index.writer() as writer:
            for soup, url in self.preliminary_index:
                writer.add_document(title=soup.title.text, content=soup.text, url=url)

        self.preliminary_index = []

    def __del__(self):
        """
        
        """
        self.pre_to_Index()

    def append_same_server(self,url):
        """
        
        """

        if (not url in self.url_stack_same_server) and (not url in self.urls_visited):
            self.url_stack_same_server.append(url)

    
    def find_url(self,soup, original_url, original_url_parsed):
        """
        
        """

        # analyse it to find other urls, 
        for l in soup.find_all("a"):

            # check if it is an linked image or does not contain an href
            if (not l.find('img')):
                # print(l, "\n\n\n")
                try: # try if href
                    link = l['href'] # get just the href part
                    parsed_link = urlparse(link)

                    # check wether the link is a relative link
                    if (not parsed_link.scheme and not parsed_link.netloc):

                        # join original url with relative one
                        full_url = urljoin(original_url,link)
                        self.append_same_server(full_url)

                    # if not relative check whether kind of info we want
                    elif parsed_link.scheme in self.scheme_list:

                        # check whether it is from the same website
                        if parsed_link.netloc == original_url_parsed.netloc:
                            self.append_same_server(link)
                        else:
                            pass # because task is to crawl only one server
                            #self.url_stack.append(link)

                except KeyError as e:
                    # does not have an href
                    print("KeyError, there was no href: ", l)

    def crawl_all(self):
        """
        
        """
        
        while self.url_stack:
            # take next url to crawl next server
            self.crawl(self.url_stack.pop(0))
            self.timeout_in_seconds = self.timeout_default

    def crawl(self, start_url):
        """
        
        """

        # check time to give an estimation of time left
        start = time.time()

        self.timeout_in_seconds = self.timeout_default
        parsed = urlparse(start_url)

        self.url_stack_same_server.append(start_url)

        # while the stack is not empty
        while self.url_stack_same_server:

            # take and remove first url from list
            next_url = self.url_stack_same_server.pop(0)

            # print information
            len_visited = len(self.urls_visited)
            len_togo = len(self.url_stack_same_server)
            if len_visited > 0:
                time_estimation = ((time.time() - start ) /len_visited ) * len_togo
            else: 
                time_estimation = self.timeout_in_seconds
            print(f"Total: {len_visited} from {len_visited+len_togo}; {self.convert_time(time.time() - start)}")
            print(f"Estimated time left for {len_togo}: {self.convert_time(time_estimation)}")

            # if not visited recently
            if next_url not in self.urls_visited:
                # get the content
                try:
                    # to not overwhelm the server wait before request again (politeness)
                    time.sleep(self.timeout_in_seconds / 2)

                    response = requests.get(next_url, timeout=self.timeout_in_seconds, headers=self.custom_headers)

                    print("\n",response.status_code, next_url)
                    
                    # if no error message and it is an html response
                    if response.ok and "text/html" in response.headers["content-type"]:

                        # analyse it and update index
                        soup = BeautifulSoup(response.content, 'html.parser')       

                        # update index
                        self.preliminary_index.append((soup,next_url))
                        
                        # finds all urls and saves the ones we want to visit in the future
                        self.find_url(soup,next_url,urlparse(next_url))

                    # update visited list
                    # add also errors and not html so they are not visited again. 
                    self.urls_visited.append(next_url)
                
                except requests.exceptions.Timeout:

                    if self.timeout_in_seconds > 20:
                        print("The server of: ", next_url, " is too slowly.")
                        print("The crawler will stop to crawl this server now.")
                        self.url_stack_same_server = []
                    
                    # the server seems to be too slow, give more time
                    self.timeout_in_seconds += 1

                    # Need to try again.
                    self.url_stack_same_server.append(next_url)

                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")

        self.pre_to_Index()

    def search(self, input_string):
        """
        
        """

        # helpful: https://whoosh.readthedocs.io/en/latest/searching.html

        index = self.open_index()

        # use MultifieldParser to search in different fields at once. 
        query = MultifieldParser(["title", "content"], index.schema, group=qparser.OrGroup).parse(input_string)

        # scoring BM25F takes frequency in a document in the whole index as well as length of documents into account
        with index.searcher(weighting = scoring.BM25F()) as searcher:

            # find entries with all words in the content!!!
            results = searcher.search(query) # search_page(query,1,pagelen=10)

            # have to extract all important information here before searcher is closed
            total_hits = results.estimated_length()

            if total_hits == 0:
                # try to correct the user input
                corrected = searcher.correct_query(query, input_string)
                if corrected.query != query:
                    results = searcher.search(corrected.query)
                    total_hits = results.estimated_length()

                    if total_hits > 0:
                        return corrected.string, total_hits, [(r["title"], r["url"], r.highlights("content")) for r in results]
                    else:
                        return corrected.string, 0, []

            # use highlightes to have text around the results. but content is not stored
            # taking too much space if 
            if total_hits > 0:
                return 0, total_hits, [(r["title"], r["url"], r.highlights("content")) for r in results]
            else:
                return 0,0,[]

    def convert_time(self,time):
        minutes = int(time/60)
        seconds = int(time%60)
        if minutes > 0:
            if seconds < 10:
                return f"{minutes}:0{seconds} min"
            return f"{minutes}:{seconds} min"
        return f"{seconds} sec"