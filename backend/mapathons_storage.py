
import os
from pymongo import MongoClient
import urllib.parse
import json
from bson.objectid import ObjectId

class MapathonsStorage(object):
    """
    Functionality for storing and retrieving mapathons data including
    - Changes done during a mapathon
    - Usernames of those who did the changes during the mapathon
    - List of all mapathons that have a statistics page
    """

    MONGODB_URL = "mongodb+srv://admin:" + urllib.parse.quote(os.environ['MONGODB_ATLAS_PW']) + "@hotmapathonstatistics-wn09a.mongodb.net"
    OUTPUT_BASE_PATH = os.path.join(os.getcwd(), 'mapathons_data')


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
            'mapathon_info': mapathon_data['mapathon_info'],
            'mapathon_users': mapathon_data['mapathon_users'],
            # mapathon_info example:
            # mapathon_info = {
            #   'project_number': '3567',
            #   'mapathon_date': '2018-01-26',
            #   'mapathon_time_utc': 16,
            #   'types_of_mapping': ["building", "landuse_residential", "highway"]
            # }
        }

        #self.db.mapathons.remove({})
        result = self.db.mapathons.insert_one(mapathon)

        # store found OSM changes and usernames of those who did the changes for the project area to a data store

        self.store_mapathon_changes(result.inserted_id, mapathon_data['mapathon_info']['types_of_mapping'], mapathon_data['mapathon_changes'])
        self.store_mapathon_users(result.inserted_id, mapathon_data['mapathon_users'])

        return result.inserted_id

    def get_all_mapathons(self):
        mapathons = self.db.mapathons.find({})
        return mapathons

    def get_mapathon_by_ID(self, mapathon_id):
        return self.db.mapathons.find_one({'_id': ObjectId(mapathon_id)})

    def store_mapathon_changes(self, mapathon_id, types_of_mapping, mapathon_changes):
        # Store only those types of changes (residential areas, buildings, roads) chosen by the user

        #import pprint
        #pprint(mapathon_changes)
        #'mapathon_changes': self.mapathon_changes
            # {
            #     "building": buildings,
            #     "landuse_residential": residential_areas,
            #     "highway_path": highways_path,
            #     "highway_primary": highways_primary,
            #     "highway_residential": highways_residential,
            #     "highway_secondary": highways_secondary,
            #     "highway_service": highways_service,
            #     "highway_tertiary": highways_tertiary,
            #     "highway_track": highways_track,
            #     "highway_unclassified": highways_unclassified,
            #     "highway_road": highways_road,
            #     "highway_footway": highways_footway
            # }

        output_dir = os.path.join(MapathonsStorage.OUTPUT_BASE_PATH, str(mapathon_id))

        os.makedirs(output_dir, exist_ok=True)

        if "building" in types_of_mapping:
            # print(len(mapathon_changes['building']))
            with open(os.path.join(output_dir, 'buildings.json'), 'w') as outfile:
                json.dump(mapathon_changes['building'], outfile)

        if "landuse_residential" in types_of_mapping:
            # print(len(mapathon_changes['landuse_residential']))
            # print(json.dumps(mapathon_changes['landuse_residential']))
            with open(os.path.join(output_dir, 'residential_areas.json'), 'w') as outfile:
                json.dump(mapathon_changes['landuse_residential'], outfile)

        if "highway" in types_of_mapping:
            # print(len(mapathon_changes['highway_path']))
            # print(json.dumps(mapathon_changes['highway_path']))
            with open(os.path.join(output_dir, 'highways_path.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_path'], outfile)
            # print(len(highways_primary))
            with open(os.path.join(output_dir, 'highways_primary.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_primary'], outfile)
            # print(len(highways_residential))
            with open(os.path.join(output_dir, 'highways_residential.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_residential'], outfile)
            # print(len(highways_secondary))
            with open(os.path.join(output_dir, 'highways_secondary.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_secondary'], outfile)
            # print(len(highways_service))
            with open(os.path.join(output_dir, 'highways_service.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_service'], outfile)
            # print(len(highways_tertiary))
            with open(os.path.join(output_dir,'highways_tertiary.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_tertiary'], outfile)
            # print(len(highways_track))
            with open(os.path.join(output_dir, 'highways_track.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_track'], outfile)
            # print(len(highways_unclassified))
            with open(os.path.join(output_dir, 'highways_unclassified.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_unclassified'], outfile)
            # print(len(highways_road))
            with open(os.path.join(output_dir, 'highways_road.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_road'], outfile)
            # print(len(highways_footway))
            with open(os.path.join(output_dir, 'highways_footway.json'), 'w') as outfile:
                json.dump(mapathon_changes['highway_footway'], outfile)


    def store_mapathon_users(self, mapathon_id, mapathon_users):
        output_dir = os.path.join(MapathonsStorage.OUTPUT_BASE_PATH, str(mapathon_id))
        os.makedirs(output_dir, exist_ok=True)

        # "'mapathon_users': self.mapathon_users
        with open(os.path.join(output_dir, 'usernames.json'), 'w') as outfile:
            json.dump(mapathon_users, outfile)