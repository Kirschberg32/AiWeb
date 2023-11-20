import queue
import threading
import time

class ThreadQueueSingleton(threading.Thread):
    """
    A Thread, that controls, that always only one with giver gets the wish granted at a time. 

    Attributes:
        _only_instance (ThreadQueueSingleton): The one instance of the singleton is saved here if created
    """

    _instance = None

    def __init__(self): # TODO improve has each time a new object is created, just not saved
        if self._instance != None:
            raise Exception("This is a singleton, use get_instance instead.")
        
        # create new instance
        super().__init__(target=self._write_thread, daemon=True, name = "queue-singleton_daemon")
        self.queue = queue.PriorityQueue()
        self.running = True
        self.start()
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance

    def add_wish(self, wish):
        self.queue.put_nowait(wish)

    def grant_and_wait(self, wish):
        wish.wish_granted = True
        while not wish.wish_granted:
            time.sleep(0.1)

    def _write_thread(self):
        while self.running:
            try:
                wish = self.queue.get_nowait()
                self.grant_and_wait(wish)
            except queue.Empty:
                time.sleep(0.1)