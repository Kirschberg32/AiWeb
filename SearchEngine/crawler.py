import re

import requests
from bs4 import BeautifulSoup as bs


class MyCrawler():
    
    def __init__(self, url, html):
        try:
            self.url = url
            self.dict = {}
            self.temp = [html]
            
            while self.temp:
                self.__crawl__()
        except:
            print("Status: ", r.status_code, "! Try again!")

    def __href_search__(self, soup):
        
        for i in soup.find_all("a"):
            if 'html' in i['href']:
                self.temp.append(i['href'])

    def __crawl__(self):
        temp = self.temp.pop()
        r = requests.get(self.url + temp)
        if temp not in self.dict.keys() and r.ok:
            print(r.status_code)
            soup = bs(r.content,'html.parser')
            words = re.sub('[^A-Za-z0-9]+', ' ', soup.text).split()
            self.dict[temp] = self.url + temp ,list(set(words))
            self.__href_search__(soup)  

    def search(self):
        words = str(input("Please Enter! Example: Platypus, Australia\n").lower())
        words = words.split(",")
        #word_list = eingabe
        link_list = []
        hit_list = []
        miss_list = []
        for html, content in a.dict.items():
            temp_hit = []
            temp_miss = []
            for word in words:
                temp_hit.append(word) if word in list(content[1]) else temp_miss.append(word)
            link_list.append(content[0])
            hit_list.append(temp_hit)
            miss_list.append(temp_miss)
        search_list = link_list,hit_list,miss_list
        print(hit_list)
        if not any(hit_list):
            print("Nothing! Try again!")
            return self.search()
        else:
            print("Found something!")
            
            for i in range(len(search_list[0])):
                print("Url: ",search_list[0][i],"\nHits", len(search_list[1][i]), "of", len(words), "Found: ", hit_list[i], "\n\n")
            return search_list
        
            