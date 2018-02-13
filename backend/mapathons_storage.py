
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

    MONGODB_URL = "mongodb+srv://admin:" + urllib.parse.quote(os.environ['MONGODB_ATLASS_PW']) + "@hotmapathonstatistics-wn09a.mongodb.net"

    def __init__(self):
        self.initialize()

    def initialize(self):
        self.mongo_client = MongoClient(MapathonsStorage.MONGODB_URL)
        self.db = self.mongo_client.hot_mapathon_stastistics

        #serverStatusResult = self.db.command("serverStatus")
        #print(serverStatusResult)

    def store_mapathon(self, mapathon_data):
        # Store mapathon details, found OSM changes and usernames of those who did the changes for the project area to a data store
        # Return mapathon_id

        mapathon = {
            'stat_task_uuid': mapathon_data['stat_task_uuid'],
            'mapathon_info': mapathon_data['mapathon_info']
            # mapathon_info example:
            # mapathon_info = {
            #   'project_number': '3567',
            #   'mapathon_date': '2018-01-26',
            #   'mapathon_time_utc': 16,
            #   'types_of_mapping': ["building", "landuse_residential", "highway"]
            # }
        }

        result = self.db.mapathons.insert_one(mapathon)

        # TODO store found OSM changes and usernames of those who did the changes for the project area to a data store

        self.store_mapathon_changes(result.inserted_id, mapathon_data['mapathon_changes'])
        self.store_mapathon_users(result.inserted_id, mapathon_data['mapathon_users'])

        return result.inserted_id

    def get_all_mapathons(self):
        mapathons = self.db.mapathons.find({})
        return mapathons

    def get_mapathon_by_ID(self, mapathon_id):
        pass

    def store_mapathon_changes(self, mapathon_id, mapathon_changes):
        pass

    def store_mapathon_users(self, mapathon_id, mapathon_users):
        pass
