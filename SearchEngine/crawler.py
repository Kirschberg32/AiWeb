""" A crawler build for a simple search engine"""
from urllib.parse import urljoin, urlparse
import time

from myfunctions import get_page
from index import Index

class Crawler:
    """
    A crawler object that is able to crawl one server's html pages. 

    Attributes: 
        url_stack_same_server (list): a list containing all the found urls on the same server to visit next during crawling
        url_stack (list): a list of all urls found on different servers we want to visit (stays empty after the start_url is removed at the 
            moment because we only want to crawl one server)
        urls_visited (list): a list with all the urls that where visited already by this crawler object
        preliminary_index (list): A temporary database for index information before saving it in the whoosh index. Each element has the structure (soup (bs4.BeautifulSoup), url (string))
        custom_headers (dict): Used as the header for requests
        timeout_default (int): The default value for timeout to reset timeout when switching to crawl a different server
        timeout_in_seconds (int): The timeout value, that can increase if the server is too slow (each time by 1). 
            If it reaches 20, the crawler will stop crawling the server. 
        scheme_list (list): A list containing all the url schemes we want to visit
    """

    def __init__(self, name, index_path : str, start_url : str = "",timeout_default : int = 2):
        """

        Args: 
            name (str): The name used for custom_headers
            start_url (str): The url to start crawling from, if "" you have to give it to crawl() as an argument before you can start crawling
            timeout_default (int): The default value for timeout to reset timeout when switching to crawl a different server
        """

        self.url_stack_same_server = []
        if start_url:
            self.url_stack = [start_url,] # only used when crawling different servers too
        else:
            self.url_stack = []
        self.urls_visited = []

        self.timeout_default = timeout_default
        self.timeout_in_seconds = self.timeout_default

        self.index = Index(name,index_path,self.timeout_default)
        self.preliminary_index = []

        # custom headers to indicate, that I am a crawler (politeness)
        self.custom_headers = {'User-Agent': "CrawlerforSearchEnginge/" + name}

        self.scheme_list = ["https", "http"] # requests only works with these

    def __del__(self):
        """
        Should 
        """
        self.index.list_to_Index(self.preliminary_index)

    def append_same_server(self,url):
        """
        Appends a new url to the same server list. Please check beforehand if it really is the same server. 
        It only checks whether the url already is in the list, whether it was already visited, or is in index or preliminary_index before appending it.

        Args:
            url (string): The url to append
        """

        if (not url in self.url_stack_same_server) and (not url in self.urls_visited)and not self.is_in_preliminary(url) and not self.index.is_in_index(url):
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
                    if (not parsed_link.scheme) and (not parsed_link.netloc):

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
            self.crawl(self.url_stack.pop(-1))
            self.timeout_in_seconds = self.timeout_default

    def crawl(self, start_url, batch = 20):
        """
        crawls all websites that can be reached from a start_url on the same server. 
        This is done so the list of webpages to go does not become too long. 

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
            next_url = self.url_stack_same_server.pop(-1)

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
            #if next_url not in self.urls_visited and not self.index.is_in_index(next_url) and not self.is_in_preliminary(next_url):

            # to not overwhelm the server wait before request again (politeness)
            time.sleep(self.timeout_in_seconds / 2)

            # get page
            code, soup = get_page(next_url,self.timeout_in_seconds,self.custom_headers)

            if code == -1: # if the server is too slow
                print("The server of: ", next_url, " is too slowly.")
                print("The crawler will stop to crawl this server now.")
                self.url_stack_same_server = []
            elif code ==1: # if 0 then the returns where not html or not ok code
                # update index
                self.preliminary_index.append((soup,next_url))
                
                # finds all urls and saves the ones we want to visit in the future
                self.find_url(soup,next_url,urlparse(next_url))
            else:
                # update visited list
                # add errors and not html so they are not visited again. 
                self.urls_visited.append(next_url)

            if len(self.preliminary_index) >= batch:
                self.index.list_to_Index(self.preliminary_index)
                self.preliminary_index = []

        self.index.list_to_Index(self.preliminary_index)
        self.preliminary_index = []
        self.timeout_in_seconds = self.timeout_default

    def crawl_updates(self, age_in_days : int = 30):
        """
        crawls pages again to get new information to make the index up to date
        https://docs.python.org/3/library/threading.html#rlock-objects

        Args:
            age_in_days (int): Information that is older than that will be updated
        """

        urls_to_update = self.index.find_old(age_in_days)

        # TODO
        # which order
        # how to reuse methods I already have
        # lock to make sure searching and updating do not collide
        # Welche listen mit URLs aus dem RAM wollen wir noch auf der Festplatte speichern?





    def is_in_preliminary(self,url):
        """
        checks whether there is a tuple with url in self.preliminary_index

        Args:
            url (str): The url to search for

        Returns:
            value (bool): True if url is in self.preliminary_index else False
        """

        for _, url2 in self.preliminary_index:
            if url == url2:
                return True
        return False

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