
import os
from pymongo import MongoClient
import urllib.parse

class MapathonsStorage(object):
    """
    Functionality for storing and retrieving mapathons data including
    - Changes done during a mapathon
    - Usernames of those who did the changes during the mapathon
    - List of all mapathons that have a statistics page
    """

    MONGODB_URL = "mongodb+srv://admin:" + urllib.parse.quote(os.environ['MONGODB_ATLASS_PW']) + "@hotmapathonstatistics-wn09a.mongodb.net/mapathons"

    def __init__(self):
        self.initialize()

    def initialize(self):
        self.mongo_client = MongoClient(MapathonsStorage.MONGODB_URL)
        self.db = self.mongo_client.test

        #serverStatusResult = self.db.command("serverStatus")
        #print(serverStatusResult)

    def store_mapathon(self, mapathon_data):
        # TODO store found OSM changes and usernames of those who did the changes for the project area to a data store
        pass

    def get_all_mapathons(self):
        pass

    def get_mapathon_by_ID(self, mapathon_id):
        pass

