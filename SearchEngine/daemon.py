import time
import threading
import crawler
import schedule

class MyDaemon:

    def __init__(self,info_dict,update_time = "01:00"):

        self.info_dict = info_dict
        self.update_time = update_time

        self.T = threading.Thread(target=self.the_daemon)
        self.T.setDaemon(True)# so the thread stops when the main program stops

    def start(self):

        self.T.start()
        return self

    def the_daemon(self):

        # create schedule plan
        #schedule.every().tuesday.at(self.update_time).do(self.daily_daemon_function,'It is ' + self.update_time)
        schedule.every().second.do(self.daily_daemon_function)

        while True:
            schedule.run_pending() # only one running at a time
            time.sleep(1)

    def daily_daemon_function(self):
        print("daily_daemon_function is running")
        mycrawler = crawler.Crawler(self.info_dict["custom_header_name"],self.info_dict["index_path"])
        # mycrawler.crawl_update()
        time.sleep(10)
        print("daily_daemon_function ends")

