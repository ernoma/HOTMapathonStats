
import threading

class MapathonStatistics(object):
    """
    Functionality for the statistics creation task run as a thread.
    """

    def start_task(self, uuid):

        self.uuid = uuid

        self.thread = threading.Thread(target=self.run_stats_creation, args=())
        self.thread.start()

    def run_stats_creation(self):
        print(self.uuid)
