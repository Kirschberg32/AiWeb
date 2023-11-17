""" Index using whoosh """

import os
from concurrent import futures
from whoosh.index import create_in, exists_in, open_dir
from whoosh.fields import Schema, TEXT, ID
from whoosh.qparser import MultifieldParser, QueryParser
from whoosh import scoring, qparser

from myfunctions import get_page

class Index:
    """

    Attributes:
        index_path (str): A directory of where to save or load the whoosh index
        custom_headers (dict): Used as the header for requests when searching
        timeout_default (int): The default value for timeout before retrying the same server
    """

    def __init__(self,index_path, name, timeout_default : int = 2):
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

    def list_to_Index(self,input_list):
        """
        Adds all elements in self.preliminary_index to the whoosh index with title, text and url
        the preliminary_index will be emptied afterwards

        Args:
            input_list (list): containing elements to save in the format (bs4.BeautifulSoup,str), where the string is meant to be an url
        """

        index = self.open_index()

        # automatically committed and closed writer
        with index.writer() as writer:
            for soup, url in input_list:
                writer.add_document(title=soup.title.text, content=soup.text, url=url)

        self.preliminary_index = []

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
        
    def convert_results(self,results):
        """
        converts the search results into a usable format. Also reretrieves the webpages to create highlights

        Args:
            results (whoosh.searching.Results): An object retrieved by doing a search in a whoosh index
        
        Returns:
            output (list): A list containing sets for each hit [(title, url, highlights), ...]
        """
        output = []

        # ask for new content parallel for all results
        with futures.ThreadPoolExecutor(max_workers=15) as executor:
            res = executor.map(lambda p: get_page(*p),[(r["url"],self.timeout_default,self.custom_headers) for r in results])
        responses_new = list(res)

        for r,code_soup in zip(results,responses_new):

            if code_soup[0] == 1: # only use new info if the server is reachable
                output.append((r["title"], r["url"], r.highlights("content", text = code_soup[1].text )))

        return output

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
    
