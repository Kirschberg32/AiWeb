import time
import threading
import schedule
import logging

import mylib.crawler

# Logging
logging.basicConfig(filename='gugel.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IndexUpdateDaemon(threading.Thread):
    """
    A daemon that runs crawler.Crawler.crawl_updates() once a day at update_time (default 1 am)

    Attributes:
        info_dict (dict): a dict containing the keys: "start_url", "custom_header_name" and "index_path"
        update_time (str): The time at which the deamon should update ("hh:mm")
    """

    def __init__(self,info_dict,update_time = "01:00"):

        super().__init__(target=self._the_daemon,daemon=True,name="updating-daemon")

        self.info_dict = info_dict
        self.update_time = update_time

        logger.info('Initialized Daemon')

    def _the_daemon(self):
        """
        The function that runs continuesly
        """

        # create schedule plan
        schedule.every().tuesday.at(self.update_time).do(self._daily_daemon_function,'It is ' + self.update_time)
        #schedule.every().second.do(self._daily_daemon_function)

        while True:
            schedule.run_pending() # only one running at a time
            time.sleep(1)

    def _daily_daemon_function(self):
        """
        Runs the crawl_updates, is supposed to be run at the scheduled times. 
        """
        print("daily_daemon_function is running")
        mycrawler = crawler.Crawler(self.info_dict["custom_header_name"],self.info_dict["index_path"])
        mycrawler.crawl_updates()
        print("daily_daemon_function ends")

def main():
    import mylib.website_dicts
    v = website_dicts.test

    IndexUpdateDaemon(v).start()

    while True:
        continue

if __name__ == "__main__":
    main()