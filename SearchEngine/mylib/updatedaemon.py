import time
import threading
import schedule
import logging

from mylib.crawler import Crawler
from mylib.myfunctions import create_logger

# Logging
logger = create_logger(folder = 'logs',filename = 'gugel.log', level=logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

class IndexUpdateDaemon(threading.Thread):
    """
    A daemon that runs crawler.Crawler.crawl_updates() once a day at update_time (default 1 am)

    Attributes:
        info_dict (dict): a dict containing the keys: "start_url", "custom_header_name" and "index_path"
        update_time (str): The time at which the deamon should update ("hh:mm")
    """

    def __init__(self,info_dict,update_time = ""):

        if update_time:
            super().__init__(target=self._the_scheduled_daemon,daemon=True,name="updating-daemon")
        else:
            super().__init__(target=self._the_direct_daemon,daemon=True,name="updating-daemon")

        self.info_dict = info_dict
        self.update_time = update_time

        logger.info('Initialized Daemon')

    def _the_scheduled_daemon(self):
        """
        The function that runs continuesly, when the daemon is scheduled
        """

        # create schedule plan
        schedule.every().day.at(self.update_time).do(self._daily_daemon_function,'It is ' + self.update_time)
        # schedule.every().second.do(self._daily_daemon_function)

        while True:
            schedule.run_pending() # only one running at a time
            time.sleep(1)

    def _the_direct_daemon(self):
        """
        The function that runs once if the daemon is restarted each time it is supposed to run. 
        """

        # just run once because the server restarts once a day. 
        self._daily_daemon_function()

    def _daily_daemon_function(self):
        """
        Runs the crawl_updates, is supposed to be run at the scheduled times. 
        """
        logger.info('Update Daemon started working routine')
        mycrawler = Crawler(self.info_dict["custom_header_name"],self.info_dict["path"])
        mycrawler.crawl_updates(age_in_days=30)
        logger.info('Update Daemon is done')