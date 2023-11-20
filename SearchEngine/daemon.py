import time
import threading
import crawler
import schedule

class MyDaemon:
    """
    A daemon that runs crawler.Crawler.crawl_updates() once a day at update_time (default 1 am)

    Attributes:
        info_dict (dict): a dict containing the keys: "start_url", "custom_header_name" and "index_path"
        update_time (str): The time at which the deamon should update ("hh:mm")
        T (threading.Thread): The Thread that is used
    """

    def __init__(self,info_dict,update_time = "01:00"):

        self.info_dict = info_dict
        self.update_time = update_time

        self.T = threading.Thread(target=self.the_daemon,daemon=True,name="updating-daemon")# so the thread stops when the main program stops T.setDaemon(True) is deprecated

    def start(self):
        """
        starts the daemon

        Returns:
            daemon (MyDaemon): returns itself
        """

        self.T.start()
        return self

    def the_daemon(self):
        """
        The function that is runs continuesly
        """

        # create schedule plan
        #schedule.every().tuesday.at(self.update_time).do(self.daily_daemon_function,'It is ' + self.update_time)
        schedule.every().second.do(self.daily_daemon_function)

        while True:
            schedule.run_pending() # only one running at a time
            time.sleep(1)

    def daily_daemon_function(self):
        """
        Runs the crawl_updates, is supposed to be run at the scheduled times. 
        """
        print("daily_daemon_function is running")
        mycrawler = crawler.Crawler(self.info_dict["custom_header_name"],self.info_dict["index_path"])
        mycrawler.crawl_updates()
        time.sleep(10)
        print("daily_daemon_function ends")

def main():
    import website_dicts
    v = website_dicts.test

    MyDaemon(v).start()

    while True:
        continue

if __name__ == "__main__":
    main()