""" A crawler build for a simple search engine"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
import os
from whoosh.index import create_in, exists_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh import scoring, qparser

class Crawler:
    """
    A crawler object that is able to crawl one server's html pages. 

    Attributes: 
        url_stack_same_server (list): a list containing all the found urls on the same server to visit next during crawling
        url_stack (list): a list of all urls found on different servers we want to visit (stays empty after the start_url is removed at the 
            moment because we only want to crawl one server)
        urls_visited (list): a list with all the urls that where visited already by this crawler object
        index_path (str): A directory of where to save or load the whoosh index
        preliminary_index (list): A temporary database for index information before saving it in the whoosh index. Each element has the structure (soup (bs4.BeautifulSoup), url (string))
        custom_headers (dict): Used as the header for requests
        timeout_default (int): The default value for timeout to reset timeout when switching to crawl a different server
        timeout_in_seconds (int): The timeout value, that can increase if the server is too slow (each time by 1). 
            If it reaches 20, the crawler will stop crawling the server. 
        scheme_list (list): A list containing all the url schemes we want to visit
    """

    def __init__(self, name, index_path : str, start_url : str = ""):
        """

        Args: 
            name (str): The name used for custom_headers, 
            index_path (str): A directory of where to save or load the whoosh index
            start_url (str): The url to start crawling from, if "" you have to give it to crawl() as an argument before you can start crawling
        """

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
        Opens or creates the index of this crawler

        returns:
            index (whoosh.index.Index): The index to use for creating writer and searcher
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
        Adds one single element to the whoosh index

        Args: 
            soup (bs4.BeautifulSoup): The object containing the information about the webpage
            url (string): The url where the data of the soup was found
        """

        index = self.open_index()
        with index.writer() as writer:
            writer.add_document(title=soup.title.text, content=soup.text, url=url)

    def pre_to_Index(self):
        """
        Adds all elements in self.preliminary_index to the whoosh index with title, text and url
        the preliminary_index will be emptied afterwards
        """

        index = self.open_index()

        # automatically committed and closed writer
        with index.writer() as writer:
            for soup, url in self.preliminary_index:
                writer.add_document(title=soup.title.text, content=soup.text, url=url)

        self.preliminary_index = []

    def __del__(self):
        """
        Should 
        """
        self.pre_to_Index()

    def append_same_server(self,url):
        """
        Appends a new url to the same server list. Please check beforehand if it really is the same server. 
        It only checks whether the url already is in the list and whether it was already visited. Then it does not append it. 

        Args:
            url (string): The url to append
        """

        if (not url in self.url_stack_same_server) and (not url in self.urls_visited):
            self.url_stack_same_server.append(url)

    
    def find_url(self,soup, original_url, original_url_parsed = None):
        """
        Finds all urls in a given soup object

        Args:
            soup (bs4.BeautifulSoup): the data to search in
            original_url (string): the url where the data is from (used to create full urls from relative ones)
            original_url_parsed (urllib.parse.ParseResult): the same url as in original_url but already parsed (if not given it is created)
        """

        if not original_url_parsed:
            original_url_parsed = urlparse(original_url)

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
        Crawls everything it finds (not recommended)
        Only works when a start url is given when the crawler was created. 
        At the moment the crawler does not append new urls to url_stack by itself, as the task is to only crawl one server
        """
        
        while self.url_stack:
            # take next url to crawl next server
            self.crawl(self.url_stack.pop(0))
            self.timeout_in_seconds = self.timeout_default

    def crawl(self, start_url, batch = 20):
        """
        crawls all websites that can be reached from a start_url

        Args:
            start_url (str): a string containing an url
            batch (int): After how many webpages to update the index
        """

        # check time to give an estimation of time left
        start = time.time()

        self.timeout_in_seconds = self.timeout_default

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
            print(f"Estimated time left for {len_togo} pages: {self.convert_time(time_estimation)}")

            # if not visited recently
            if next_url not in self.urls_visited:

                # to not overwhelm the server wait before request again (politeness)
                time.sleep(self.timeout_in_seconds / 2)

                # get page
                code, soup = self.get_page(next_url)

                if code == -1: # if the server is too slow
                    print("The server of: ", next_url, " is too slowly.")
                    print("The crawler will stop to crawl this server now.")
                    self.url_stack_same_server = []
                elif code ==1: # if 0 then the returns where not html or not ok code
                    # update index
                    self.preliminary_index.append((soup,next_url))
                    
                    # finds all urls and saves the ones we want to visit in the future
                    self.find_url(soup,next_url,urlparse(next_url))

                # update visited list
                # add also errors and not html so they are not visited again. 
                self.urls_visited.append(next_url)

                if len(self.preliminary_index) >= batch:
                    self.pre_to_Index()

        self.pre_to_Index()
        self.timeout_in_seconds = self.timeout_default

    def search(self, input_string, limit = 15, page = 1):
        """
        Searches in the index for a search term.
        It searches in the title and content and is a default OR search. It uses BM25F as a scoring algorithm. 
        If there are no matches the input_string will be corrected. Then it will be searched again. 

        Args: 
            input_string (str): A string containing the search term
            limit (int): How many results to return for each page
            page (int>0): results for which page to load

        Returns:
            total_hits (int): The estimated number of total hits
            pagecount (int): How many pages exist
            pagenum (int): Which page this is
            is_last_page (bool): whether this is the last page
            results (list): A list containing sets for each hit [(title, url, highlights), ...]
        """

        # helpful: https://whoosh.readthedocs.io/en/latest/searching.html

        index = self.open_index()

        # use MultifieldParser to search in different fields at once. 
        query = MultifieldParser(["title", "content"], index.schema, group=qparser.OrGroup).parse(input_string)

        # scoring BM25F takes frequency in a document in the whole index as well as length of documents into account
        with index.searcher(weighting = scoring.BM25F()) as searcher:

            # find entries with all words in the content!!!
            p = searcher.search_page(query,page,limit) # search_page(query,1,pagelen=10)

            # have to extract all important information here before searcher is closed
            #total_hits = resultspage.total

            # use highlightes to have text around the results. but content is not stored
            # taking too much space if 
            return p.total, p.pagecount, p.pagenum, p.is_last_page(), self.convert_results(p.results)

    def correct_string(self,input_string):
        """
        Checks if a search_input can be corrected

        Args:
            input_string (str): The string to correct

        Returns:
            corrected.string (str): The corrected input
        """

        index = self.open_index()

        query = MultifieldParser(["title", "content"], index.schema, group=qparser.OrGroup).parse(input_string)

        with index.searcher() as searcher:
            corrected = searcher.correct_query(query, input_string)
            if corrected.query != query: # if query changed
                return corrected.string
            
        return ""
    
    def get_page(self,url):
        """
        retrieves a webpage given an url

        Args: 
            url (str): The url to retrieve from

        Returns:
            code (int): 1 for successful, 0 for was not html or not ok, -1 for server is too slow
            soup (bs4.BeautifulSoup): The content of the webpage if code = 1
        """
        try:
            response = requests.get(url, timeout=self.timeout_in_seconds, headers=self.custom_headers)

            print("\n",response.status_code, url)
            
            # if no error message and it is an html response
            if response.ok and "text/html" in response.headers["content-type"]:

                # analyse it and update index
                soup = BeautifulSoup(response.content, 'html.parser') 
                return 1, soup
            return 0, None
            
        except requests.exceptions.Timeout:

            if self.timeout_in_seconds > 20:
                return -1, None
            
            # the server seems to be too slow, give more time
            self.timeout_in_seconds += 1

            # Need to try again.
            time.sleep(self.timeout_in_seconds / 2)
            return self.get_page(url)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

    def convert_results(self,results):
        """
        converts the search results into a usable format. Also reretrieves the webpages to create highlights

        Args:
            results (whoosh.searching.Results): An object retrieved by doing a search in a whoosh index
        
        Returns:
            output (list): A list containing sets for each hit [(title, url, highlights), ...]
        """
        output = []

        for r in results:
            code, soup = self.get_page(r["url"]) # this does take a little longer than using the stored information

            if code == 1: # only use new info if the server is reachable
                self.update_index(r["url"],soup)
                output.append((r["title"], r["url"], r.highlights("content", text = soup.text )))

        return output
    
    def update_index(self,url,new_soup):
        """
        delete old entry for url and save a new one given new content

        Args: 
            url (str): the entry with this url will be updated if it exists, else just added
            new_soup (bs4.BeautifulSoup): content for the new entry
        """
        index = self.open_index()

        # check if old entry exists
        query = QueryParser("url", index.schema, group=qparser.OrGroup).parse(url)
        with index.searcher() as searcher:
            results = searcher.search(query)
            if len(results)> 0:

                # delete old entry
                with index.writer() as writer:
                    writer.delete_by_term("url", url)

                # add new entry
                self.add_to_Index(new_soup,url)

    def convert_time(self,time):
        """
        A method to convert a time in seconds into a readable string

        Args:
            time (int): time in seconds to convert

        Returns:
            string (str): The pretty string for printing readable time
        """
        hours = int(time/60/60)
        minutes = int((time/60)%60)
        seconds = int(time%60)
        
        # convert to having a a zero in front
        minutes_str = f"0{minutes}" if minutes < 10 else str(minutes)
        seconds_str = f"0{seconds}" if seconds < 10 else str(seconds)

        if hours > 0:
            return f"{hours}:{minutes_str}:{seconds_str} h"
        if minutes > 0:
            return f"{minutes_str}:{seconds_str} min"
        return f"{seconds_str} sec"