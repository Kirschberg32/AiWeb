""" Index using whoosh """

import os
import re
from datetime import datetime, timedelta
from concurrent import futures
from urllib.parse import urljoin, urlparse
from whoosh.index import create_in, exists_in, open_dir
from whoosh.fields import Schema, TEXT, ID, DATETIME
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh import scoring, qparser
from whoosh.writing import IndexingError

from myfunctions import get_page

class Index:
    """

    Attributes:
        index_path (str): A directory of where to save or load the whoosh index
        custom_headers (dict): Used as the header for requests when searching
        timeout_default (int): The default value for timeout before retrying the same server
    """

    def __init__(self,name, index_path, timeout_default : int = 2):
        """
        Args:
            index_path (str): A directory of where to save or load the whoosh index
            name (str): The name used for custom_headers
            timeout_default (int): The default value for timeout before retrying the same server
        """

        self.index_path = index_path

        self.custom_headers = {'User-Agent': "SearchEnginge Gugel/" + name}

        self.timeout_default = timeout_default

    def open_index(self):
        """
        Opens or creates the whoosh index

        returns:
            index (whoosh.index.Index): The index to use for creating writer and searcher
        """
        # create folders if they do not exist
        if not os.path.isdir(self.index_path):
            os.makedirs(self.index_path)

        # if there is no existing index create a new one
        if not exists_in(self.index_path):
            # stored content to do easy highlights
            schema = Schema(title=TEXT(stored=True), content=TEXT, url=ID(stored=True), date=DATETIME(stored=True))
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
        date = datetime.utcnow()

        with index.writer() as writer:
            writer.add_document(title=soup.title.text, content=soup.text, url=url, date=date)

    def list_to_Index(self,input_list):
        """
        Adds all elements in self.preliminary_index to the whoosh index with title, text and url
        the preliminary_index will be emptied afterwards

        Args:
            input_list (list): containing elements to save in the format (bs4.BeautifulSoup,str), where the string is meant to be an url
        """

        index = self.open_index()
        date = datetime.utcnow()

        # automatically committed and closed writer
        with index.writer() as writer:
            for soup, url in input_list:
                writer.add_document(title=soup.title.text, content=soup.text, url=url, date=date)

        self.preliminary_index = []

    def update_index(self,url,new_soup): # TODO lock
        """
        delete old entry for url and save a new one given new content

        Args: 
            url (str): the entry with this url will be updated if it exists, else just added
            new_soup (bs4.BeautifulSoup): content for the new entry
        """
        # self.is_in_index(url,delete=True)
        index = self.open_index()
        date = datetime.utcnow()

        # delete old entry
        try:
            with index.writer() as writer:
                writer.delete_by_term("url", url)
                writer.add_document(title=new_soup.title.text, content=new_soup.text, url=url, date=date)
        except IndexingError as e:
            # does not exists, so just add the new one
            with index.writer() as writer:
                writer.add_document(title=new_soup.title.text, content=new_soup.text, url=url, date=date)

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
        
    def find_old(self, age_in_days : int = 30):
        """
        Finds old entries in the index, that are older than age_in_days days

        Args:
            age_in_days (int): Information that is older than that will be updated
        """

        # create input_string without using DateParserPlugin
        threshold_date = str(datetime.utcnow() - timedelta(days=age_in_days)).split()[0]
        input_string = f"date:[20000101 to {re.sub(r'[^0-9]', '', threshold_date)}]"

        # find all pages that are older than x
        # helpful: https://whoosh.readthedocs.io/en/latest/dates.html
        index = self.open_index()
        query = QueryParser("date", index.schema)

        # query.add_plugin(DateParserPlugin)()
        query = query.parse(input_string)

        with index.searcher() as searcher:
            results = searcher.search(query,limit=None) # do this in batches if working with more data using search_page

            return [r["url"] for r in results]
        
    def convert_results(self,results):
        """
        converts the search results into a usable format. Also reretrieves the webpages to create highlights and finds the favicon link if it exists

        Args:
            results (whoosh.searching.Results): An object retrieved by doing a search in a whoosh index
        
        Returns:
            output (list): A list containing sets for each hit [(title, url, highlights, favicon_url), ...]
        """
        output = []

        # ask for new content parallel for all results
        with futures.ThreadPoolExecutor(max_workers=15) as executor:
            res = executor.map(lambda p: get_page(*p),[(r["url"],self.timeout_default,self.custom_headers) for r in results])
        responses_new = list(res)

        for r,code_soup in zip(results,responses_new):

            if code_soup[0] == 1: # only use new info if the server is reachable

                # get favicons of the pages
                favicon_url = self.find_favicon(r["url"],code_soup[1])

                output.append((r["title"], r["url"], r.highlights("content", text = code_soup[1].text ), favicon_url))

        return output
    
    def find_favicon(self, url,soup):
        """
        gets an url and a soup and returns the full urls to the favicon. If non found then the entry is None

        Args:
            url (str): The original url
            soup (bs4.BeautifulSoup): The html code in a soup to search in for the favicon links

        Returns:
            favicon_url (str): The url for the favicon
        """

        # get favicons of the pages
        favicon_link = soup.find("link", attrs={'rel': re.compile("^(shortcut icon|icon)$", re.I)})

        # try in case favicon_link does not have an href, is is None already
        try:
            favicon_url = favicon_link['href']

            # check wether the link is a relative link
            parsed_link = urlparse(favicon_url)
            if (not parsed_link.scheme) and (not parsed_link.netloc):
                favicon_url = urljoin(url,favicon_url)

            return favicon_url
        except:
            return None

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
    
    def is_in_index(self,url, delete = False):
        """ 
        checks whether there is an entry with url = url in the index

        Args:
            url (str): the url to look for
            delete (bool): True -> delete entry if it is found in index

        Returns:
            value (bool): True if is in index, False if not; or if always is False and self.check_index is True value is False
        """

        index = self.open_index()

        # check if old entry exists
        query = QueryParser("url", index.schema, group=qparser.OrGroup).parse(url)
        with index.searcher() as searcher:
            results = searcher.search(query)
            if len(results)> 0 and results[0]["url"]==url:
                if delete:
                    # delete old entry
                    with index.writer() as writer:
                        writer.delete_by_term("url", url)
                return True
        return False

    
