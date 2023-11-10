""" A crawler build for a simple search engine"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import nltk
import re
from functools import reduce
import time

# Check whether the nltk punk tokenizer still has to be installed
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

class Crawler:

    def __init__(self,start_url, name):
        self.start_url = start_url
        self.url_stack_same_server = []
        self.url_stack = [start_url,] # only used when crawling different servers too
        self.urls_visited = []
        self.last_url_parsed = ""

        self.index = dict()

        # custom headers to indicate, that I am a crawler
        self.custom_headers = {'User-Agent': name}
        self.timeout_default = 2
        self.timeout_in_seconds = self.timeout_default

        self.scheme_list = ["https", "http", "ftps", "ftp", "data"]

    def get_Index(self):
        return self.index
    
    def add_to_Index(self,word,url):
        if word in self.index:
            self.index[word].append(url)
        else:
            self.index[word] = [url]
    
    def find_url(self,soup, original_url, original_url_parsed):

        # analyse it to find other urls, 
        for l in soup.find_all("a"):
            link = l['href'] # get just the href part
            parsed_link = urlparse(link)

            # check wether the link is a relative link
            if not (parsed_link.scheme and parsed_link.netloc):

                # join original url with relative one
                full_url = urljoin(original_url,link)
                self.url_stack_same_server.append(full_url)

            # if not relative check whether kind of info we want
            elif (parsed_link.scheme in self.scheme_list):

                # check whether it is from the same website
                if parsed_link.netloc == original_url_parsed.netloc:
                    self.url_stack_same_server.append(link)
                else:
                    pass # because task is to crawl only one server
                    #self.url_stack.append(link)

    def crawl(self):
        
        while self.url_stack:
            # take next url to crawl next server
            self.url_stack_same_server.append(self.url_stack.pop(0))
            self.crawl_server()
            self.timeout_in_seconds = self.timeout_default

    def crawl_server(self):
        # while the stack is not empty
        while self.url_stack_same_server:
            # take and remove first url from list
            next_url = self.url_stack_same_server.pop(0)
            parsed_url = urlparse(next_url) # used to check whether other urls are for the same server

            # if not visited recently
            if next_url not in self.urls_visited:
                # get the content
                try:
                    # to not overwhelm the server wait before request again (politeness)
                    time.sleep(self.timeout_in_seconds / 2)

                    response = requests.get(next_url, timeout=self.timeout_in_seconds, headers=self.custom_headers)

                    print("\n",response.status_code, next_url)
                    if response.ok:

                        # analyse it and update index
                        # if not html go into except
                        try:
                            soup = BeautifulSoup(response.content, 'html.parser')
                            page_content = soup.text # retrieve all the text

                            # create a set of only words and numbers
                            cleaned_words = self.string_to_tokens(page_content)               

                            # update index
                            for word in cleaned_words:
                                self.add_to_Index(word,next_url)
                            
                            self.find_url(soup,next_url,parsed_url)
    
                            # update visited list
                            self.urls_visited.append(next_url)
                        except:
                            # no html
                            print("content is not html")
                
                except requests.exceptions.Timeout:
                    # the server seems to be too slow, give more time
                    self.timeout_in_seconds += 1
                    # Need to try again.
                    self.url_stack.insert(0,next_url)
                except requests.exceptions.RequestException as e:
                    print(f"An error occurred: {e}")

                self.last_url_parsed = parsed_url

    def search(self, list_of_words):

        url_sets = [set(self.index[word]) if word in self.index else set() for word in list_of_words]

        # find common elements in all three sets
        common_urls = list(reduce(set.intersection, url_sets))
        return common_urls
    
    def string_to_tokens(self,string):

        words = set(nltk.word_tokenize(string.lower()))

        # now remove all non-alphabet and non-number characters
        cleaned_words = [re.sub(r'[^a-zA-Z0-9]', '', word) for word in words ]

        # remove empty words
        cleaned_words = [word for word in cleaned_words if word]
        return cleaned_words

