""" A crawler build for a simple search engine"""
from urllib.parse import urljoin, urlparse
import time
from datetime import datetime, timedelta
import os
import re

from mylib.myfunctions import get_page
from mylib.index import Index

class Crawler:
    """
    A crawler object that is able to crawl one server's html pages. 

    Attributes: 
        url_stack_same_server (list): a list containing all the found urls on the same server to visit next during crawling. contains tuples: (url (str), depth (int))
        url_stack (list): a list of all urls found on different servers we want to visit (stays empty after the start_url is removed at the 
            moment because we only want to crawl one server)
        urls_visited (list): a list with all the urls that where visited already by this crawler object and where not relevant for the index
        urls_visited_path (str):
        urls_to_visit_update (list): a list of tuples of urls to visit again next update and the date when the url was found for the first time(saved in file when crawler is not running)
        urls_to_visit_update_path (str): Where to save urls_to_visit_update
        url_stack_same_server_for_later (list): used during Crawler.crawl. contains tuples: (url (str), depth (int))
        preliminary_index (list): A temporary database for index information before saving it in the whoosh index. Each element has the structure (soup (bs4.BeautifulSoup), url (string))
        custom_headers (dict): Used as the header for requests
        timeout_in_seconds (int): The timeout value, that can increase during myfunctions.get_page if the server is too slow (each time by 1). 
            If it reaches 20, the crawler will stop crawling the server. 
        scheme_list (list): A list containing all the url schemes we want to visit
    """

    def __init__(self, name, path : str, start_url : str = "",timeout : int = 2):
        """

        Args: 
            name (str): The name used for custom_headers
            start_url (str): The url to start crawling from, if "" you have to give it to crawl() as an argument before you can start crawling
            timeout (int): The default value for timeout to reset timeout when switching to crawl a different server
        """

        #pattern to exclude in find_url
        self.find_re = re.compile(r'.*\.(img|jpg|png|pdf)')
        
        self.url_stack_same_server = []
        if start_url:
            self.url_stack = [start_url,] # only used when crawling different servers too
        else:
            self.url_stack = []

        if not os.path.isdir("Crawler/" + path):
            os.makedirs("Crawler/" + path)

        self.urls_visited_path = "Crawler/" + path + "/urls_visited.txt"
        self.urls_visited = []
        if os.path.isfile(self.urls_visited_path):
            with open(self.urls_visited_path) as file:
                for line in file:
                    self.urls_visited.append(line.replace("\n", ""))
        else:
            with open(self.urls_visited_path, 'w') as file:
                pass

        # load from file if exists
        # create folders if they do not exist
        self.urls_to_visit_update_path = "Crawler/" + path + "/urls_to_visit_update.txt"
        self.urls_to_visit_update = []
        if os.path.isfile(self.urls_to_visit_update_path):
            with open(self.urls_to_visit_update_path) as file:
                for line in file:
                    splitted = line.replace("\n", "").split(',')
                    self.urls_to_visit_update.append((splitted[0],datetime.strptime(splitted[1],'%y-%m-%d %H:%M:%S')))

        self.urls_to_visit_update = []
        self.url_stack_same_server_for_later = []

        self.timeout_in_seconds = timeout

        self.index = Index(name,"Index/" + path,timeout)
        self.preliminary_index = []

        # custom headers to indicate, that I am a crawler (politeness)
        self.custom_headers = {'User-Agent': "CrawlerforSearchEnginge/" + name}

        self.scheme_list = ["https", "http"] # requests only works with these

    def save_urls_to_visit_update(self):
        """
        Writes self.urls_to_visit_update in a txt
        """

        if self.urls_to_visit_update:

            list_to_save = [url + "," + date.strftime('%y-%m-%d %H:%M:%S') + "\n" for url, date in self.urls_to_visit_update]

            with open(self.urls_to_visit_update_path, 'w') as file:
                file.writelines(list_to_save)
                
                    
    def __del__(self):
        """
        Saves the preliminary_index to the real index incase this object is destroyed before saving it itself.
        """
        if self.preliminary_index:
            self.pre_to_Index()
        self.save_urls_to_visit_update()

    def append_same_server(self,url, depth):
        """
        Appends a new url to the same server list. Please check beforehand if it really is the same server. 
        It only checks whether the url already is in the list, whether it was already visited, or is in index or preliminary_index before appending it.

        Args:
            url (string): The url to append
            depth (int): Will be increased by one
        """

        if depth < 100: # depth limit
            if (all(url != tpl[0] for tpl in self.url_stack_same_server)) and (all(url != tpl[0] for tpl in self.url_stack_same_server_for_later)) and (not url in self.urls_visited) and (not self.is_in_preliminary(url)) and (all(url != tpl[0] for tpl in self.urls_to_visit_update)) and (not self.index.is_in_index(url)):
                self.url_stack_same_server.append((url, depth + 1))

    def append_url(self,url):
        """
        Appends a new url to the url_stack. 
        It only checks whether the url already is in the list, whether it was already visited, or is in index or preliminary_index before appending it.

        Args:
            url (string): The url to append
        """

        if (not url in self.url_stack) and (not url in self.urls_visited) and (not self.is_in_preliminary(url)) and (url != tpl[0] for tpl in  self.urls_to_visit_update) and (not self.index.is_in_index(url)):
            self.url_stack_.append(url)

    def pre_to_Index(self):
        """
        Add the preliminary_index to the index
        """

        self.index.list_to_Index(self.preliminary_index)
        self.preliminary_index = []
    
    def find_url(self,soup, original_url, depth, original_url_parsed = None,):
        """
        Finds all urls in a given soup object

        Args:
            soup (bs4.BeautifulSoup): the data to search in
            original_url (string): the url where the data is from (used to create full urls from relative ones)
            depth (int): 
            original_url_parsed (urllib.parse.ParseResult): the same url as in original_url but already parsed (if not given it is created)
        """

        if not original_url_parsed:
            original_url_parsed = urlparse(original_url)

        # analyse it to find other urls, 
        for l in soup.find_all("a"):

            # check if it is an linked image or does not contain an href
            if not self.find_re.search(l.get('href', '')):
                # print(l, "\n\n\n")
                try: # try if href
                    link = l['href'] # get just the href part
                    parsed_link = urlparse(link, allow_fragments=False)

                    # check wether the link is a relative link
                    if (not parsed_link.scheme) and (not parsed_link.netloc):

                        # join original url with relative one
                        full_url = urljoin(original_url,link)
                        self.append_same_server(full_url, depth)

                    # if not relative check whether kind of info we want
                    elif parsed_link.scheme in self.scheme_list:

                        # check whether it is from the same website
                        if parsed_link.netloc == original_url_parsed.netloc:
                            self.append_same_server(parsed_link.geturl(), depth)
                        else:
                            pass # because task is to crawl only one server
                            #self.append_url(parsed_link.geturl())

                except KeyError as e:
                    # does not have an href
                    print("KeyError, there was no href: ", l)

    def crawl_all(self, start_url = ""):
        """
        Crawls everything it finds (not recommended)
        Only works when a start url is given when the crawler was created or as parameter for this method
        At the moment the crawler does not append new urls to url_stack by itself, as the task is to only crawl one server

        Args:
            start_url (str): a string containing an url
        """

        counter = 0
        start = time.time()
        self.empty_crawling_lists()

        if start_url:
            self.url_stack.append(start_url)
        
        while self.url_stack:
            # take next url to crawl next server
            counter = self.crawl(self.url_stack.pop(-1),start, counter)
            self.timeout_in_seconds = self.timeout_default

    def crawl(self, start_url = "", batch = 20, start = time.time(), counter = 0):
        """
        crawls all websites that can be reached from a start_url on the same server. 
        This is done so the list of webpages to go does not become too long. 

        Args:
            start_url (str): a string containing an url
            batch (int): After how many webpages to update the index
            start (time.Time): The starting time to calculate the running time
            counter (int): How many webpages where already crawled in this run (will be increased during this method)
        """

        # self.url_stack_same_server = []
        if start_url:
            self.url_stack_same_server.append((start_url,0))
        self.url_stack_same_server_for_later = [] # used so save urls where the server is too slow or returns 503 to check again later

        # while the stack is not empty
        while self.url_stack_same_server:

            # take and remove first url from list
            next_url, depth = self.url_stack_same_server.pop(-1)

            # to not overwhelm the server wait before request again (politeness)
            time.sleep(self.timeout_in_seconds / 2)

            counter += self.crawl_page(next_url, depth, True, start,counter) # return 1 if added to index / preliminary index

            if len(self.preliminary_index) >= batch:
                self.pre_to_Index()

        self.url_stack_same_server.extend(self.url_stack_same_server_for_later)

        # crawl server one more time, then add rest of ...for_later to for next_update

        # while the stack is not empty
        while self.url_stack_same_server:

            # take and remove first url from list
            next_url = self.url_stack_same_server.pop(-1)

            # to not overwhelm the server wait before request again (politeness)
            time.sleep(self.timeout_in_seconds / 2)

            counter += self.crawl_page(True, next_url, depth, start,counter) # return 1 if added to index / preliminary index

            if len(self.preliminary_index) >= batch:
                self.pre_to_Index()

        self.pre_to_Index()

        # save rest for next index update
        date = datetime.utcnow()
        self.urls_to_visit_update.extend([(u,date) for u,_ in self.url_stack_same_server_for_later])
        self.save_urls_to_visit_update()

        return counter
    
    def crawl_page(self, next_url, depth, printing = True, start = time.time(), counter = 0):
        """
        Crawl one page. Used as the inner part of crawl

        Args:
            next_url (str): The url of the page to crawl
            depth (int): 
            printing (bool): Whether to print some information in the terminal
            start (time.Time): The start time of the crawling algorithm, used to calculate running time for printing
            counter (int): Used for printing only. How many webpages where already visited

        Returns:
            counter_add (int): 1 if new page added to index, else 0
        """

        # print information
        if printing:
            len_all_visited = len(self.urls_visited) + counter
            len_togo = len(self.url_stack_same_server) + len(self.url_stack_same_server_for_later)
            if len_all_visited > 0:
                time_estimation = ((time.time() - start ) /len_all_visited) * len_togo
            else: 
                time_estimation = self.timeout_in_seconds
            print(f"Total: {len_all_visited } from {len_all_visited+len_togo} of this server; {self.convert_time(time.time() - start)}")
            print(f"Estimated time left for {len_togo} pages: {self.convert_time(time_estimation)}")

        # if not visited recently
        #if next_url not in self.urls_visited and not self.index.is_in_index(next_url) and not self.is_in_preliminary(next_url):

        # get page
        code, soup = get_page(next_url,self.timeout_in_seconds,self.custom_headers, True)
        print("current depth: ", depth)

        if code == 1:
            # update index
            self.preliminary_index.append((soup,next_url))
            
            # finds all urls and saves the ones we want to visit in the future
            if depth < 100: # depth limit, do not even search for more links
                self.find_url(soup, next_url, depth, urlparse(next_url))
            return 1 
        elif code == -1: # if the server is too slow
            if printing:
                print("The server of: ", next_url, " is too slowly.")
                print("The crawler will stop to crawl this page now.")
            self.url_stack_same_server_for_later.append((next_url, depth))
        elif code == 503:
            self.url_stack_same_server_for_later.append((next_url, depth))
        else: # if 0 then the returns where not html or not ok code
            # update visited list
            # add errors and not html so they are not visited again. 
            self.urls_visited.append(next_url)
            with open(self.urls_visited_path, 'a') as file:
                file.write(next_url + "\n")

        return 0

    def crawl_updates(self, age_in_days : int = 30, limit = 2000):
        """
        crawls pages again to get new information to make the index up to date
        https://docs.python.org/3/library/threading.html#rlock-objects

        Args:
            age_in_days (int): Information that is older than that will be updated
        """

        urls_to_update = []
        limit_2 = int(limit/2)
        if len(self.urls_to_visit_update) < (limit_2):
            urls_to_update = self.urls_to_visit_update.copy() + self.index.find_old(age_in_days,int(limit-len(self.urls_to_visit_update)))
            self.urls_to_visit_update = []
        else:
            urls_to_update = self.urls_to_visit_update[:limit_2] + self.index.find_old(age_in_days,(limit_2))
            self.urls_to_visit_update = self.urls_to_visit_update[limit_2:]

        self.empty_crawling_lists()
        self.url_stack = []

        for next_url,next_date in urls_to_update:
            print(f"Page: {next_url} is from {next_date.date()}")
            code, soup = get_page(next_url,self.timeout_in_seconds,self.custom_headers, True)

            if code == 1:
                # update index
                self.index.update_index(next_url,soup)
                
                # finds all urls and saves the ones we want to visit in the future
                self.find_url(soup,next_url,0, urlparse(next_url))
                
            elif code == -1: # if the server is too slow

                # if older than half a year delete & forget
                if next_date < datetime.utcnow() - timedelta(days=183): # the older one is smaller
                    self.index.delete_from_index(next_url)

                # if not old, but not in index add to list to remember
                elif not self.index.is_in_index(next_url):
                    # save with the original date to check again next time
                    self.urls_to_visit_update.append((next_url,next_date))

            elif code == 503: # Service Unavailable

                self.index.delete_from_index(next_url)
                if next_date > datetime.utcnow() - timedelta(days=365): # if older than one year
                    self.urls_to_visit_update.append((next_url,next_date))
            
            else: # if not html or just not working forget
                self.urls_visited.append(next_url)
                with open(self.urls_visited_path, 'a') as file:
                    file.writelines([next_url])
                self.index.delete_from_index(next_url)

            # now do a quick crawl though the new urls that where found: 
            self.crawl()
            # self.crawl_all()

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
    
    def empty_crawling_lists(self):
        """ 
        Empty all lists that are used during one of the crawling algorithms
        """
        self.url_stack_same_server = []
        self.url_stack_same_server_for_later = []
        self.preliminary_index = []

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