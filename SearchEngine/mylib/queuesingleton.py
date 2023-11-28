import queue
import threading
import time
import logging

from mylib.myfunctions import create_logger

# Logging
logger = create_logger(folder = 'logs',filename = 'gugel.log', level=logging.INFO, format = '%(asctime)s - %(levelname)s - %(message)s')

class ThreadQueueSingleton(threading.Thread):
    """
    A Thread, that controls, that always only one with giver gets the wish granted at a time. 

    Attributes:
        _instance (ThreadQueueSingleton): The one instance of the singleton is saved here if created
    """

    _instance = None

    def __init__(self): # TODO improve has each time a new object is created, just not saved
        """
        Creates the first and only instance of this Class and starts the thread
        """
        if self._instance != None:
            raise Exception("This is a singleton, use get_instance instead.")
        
        # create new instance
        super().__init__(target=self._write_thread, daemon=True, name = "queue-singleton_daemon")
        self.queue = queue.PriorityQueue()
        self.running = True
        self.start()
        logger.info('Initialized and started ThreadQueueSingleton')
    
    @classmethod
    def get_instance(cls):
        """
        Get the instance of the Singleton
        """
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def add_wish(self, wish):
        """
        Add one wish to the Queue, make sure the wish has a wish_granted attribute and is comparable

        Args:
            wish (e.g. index.Index): meant to be an Index
        """
        self.queue.put_nowait(wish)

    def grant_and_wait(self, wish):
        """
        Notify the wish that it is granted. Wait until the allowed process is done until continue

        Args:
        wish (e.g. index.Index): The wish to grant
        """
        wish.wish_granted = True
        while not wish.wish_granted:
            time.sleep(0.1)

    def _write_thread(self):
        """
        The thread method runs as long as self.running is true. 
        """
        while self.running:
            try:
                wish = self.queue.get_nowait()
                self.grant_and_wait(wish)
            except queue.Empty:
                time.sleep(0.1)