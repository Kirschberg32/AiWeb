import time
import requests
from bs4 import BeautifulSoup

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

def thread_highlights(index, results, all_matches):
    """
    The thread function that gets highlights and favicon in the background when given to a thread. Appends the results to global all_matches

    Args:
        index (index.Index): The index to use the get_highlights_and_favicon from
        results (list): The results of Index.search [(title, url, SeparatTextHighlighter), ...]
    """

    print("Started highlights thread")

    results_with_hf = index.get_highlights_and_favicon(results)

    all_matches.append(results_with_hf)

    print("End highlights thread")

def get_page(url, timeout_in_seconds, custom_headers, printing = True):
        """
        retrieves a webpage given an url

        Args in one tuple:
            url (str): The url to retrieve from
            timeout_in_seconds (int): used for requests timeout
            custom_headers (dict): Object used for header in requests
            printing (bool): Whether to print the result

        Returns:
            code (int): 1 for successful, 0 for was not html or not ok, -1 for server is too slow, 503 for 503
            soup (bs4.BeautifulSoup): The content of the webpage if code = 1
        """

        try:
            response = requests.get(url, timeout=timeout_in_seconds, headers=custom_headers)

            if printing:
                print("\n",response.status_code, url)
            
            # if no error message and it is an html response
            if response.ok and "text/html" in response.headers["content-type"]:

                # analyse it and update index
                soup = BeautifulSoup(response.content, 'html.parser') 
                if soup and soup.text and soup.title:
                    return 1, soup
            
            if response.status_code == 503: # Service Unavailable
                return 503, None
            return 0, None
            
        except requests.exceptions.Timeout:

            if timeout_in_seconds > 20:
                return -1, None
            
            # the server seems to be too slow, give more time
            timeout_in_seconds += 1

            # Need to try again.
            time.sleep(timeout_in_seconds / 2)
            return get_page(url,timeout_in_seconds,custom_headers)
        
        except requests.exceptions.ConnectionError:

            if timeout_in_seconds > 20:
                return -1, None
            
            # the server seems to be too slow, give more time
            timeout_in_seconds += 1

            # Need to try again.
            time.sleep(timeout_in_seconds / 2)
            return get_page(url,timeout_in_seconds,custom_headers)

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return -1, None