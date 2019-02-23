
import os
from pymongo import MongoClient
import urllib.parse
import json
from bson.objectid import ObjectId
import uuid

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

    def store_mapathon(self, mapathon_data):
        # Store mapathon details, found OSM changes and usernames of those who did the changes for the project area to a data store
        # Return mapathon_id

        mapathon = {
            'stat_task_uuid': mapathon_data['stat_task_uuid'],
            'mapathon_info': mapathon_data['mapathon_info'],
            #'mapathon_users': mapathon_data['mapathon_users'],
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

        self.store_mapathon_changes(result.inserted_id, mapathon_data['mapathon_info'], mapathon_data['mapathon_changes'])
        #self.store_mapathon_users(result.inserted_id, mapathon_data['mapathon_users'])

        return result.inserted_id

    def get_all_mapathons(self):
        mapathons = self.db.mapathons.find({})
        return mapathons

    def get_mapathon_by_ID(self, mapathon_id):
        return self.db.mapathons.find_one({'_id': ObjectId(mapathon_id)})

    def get_mapathon_by_stat_task_id(self, stat_task_id):
        return self.db.mapathons.find_one({'stat_task_uuid': uuid.UUID(stat_task_id)})

    def store_mapathon_changes(self, mapathon_id, mapathon_info, mapathon_changes):
        # Store only those types of changes (residential areas, buildings, roads, ...) chosen by the user

        if (len(mapathon_changes) == 1):
            output_dir = os.path.join(MapathonsStorage.OUTPUT_BASE_PATH, str(mapathon_id))
            os.makedirs(output_dir, exist_ok=True)

            self.store_project_changes(output_dir, mapathon_info, mapathon_changes[0])
        else:
            for index, project_changes in enumerate(mapathon_changes):
                output_dir = os.path.join(MapathonsStorage.OUTPUT_BASE_PATH, str(mapathon_id), str(mapathon_info['project_numbers'][index]))
                os.makedirs(output_dir, exist_ok=True)
                self.store_project_changes(output_dir, mapathon_info, project_changes)

    def store_project_changes(self, output_dir, mapathon_info, project_changes):
        if "building" in mapathon_info['types_of_mapping']:
            with open(os.path.join(output_dir, 'buildings.json'), 'w') as outfile:
                json.dump(project_changes['building'], outfile)

        if "landuse_residential" in mapathon_info['types_of_mapping']:
            with open(os.path.join(output_dir, 'residential_areas.json'), 'w') as outfile:
                json.dump(project_changes['landuse_residential'], outfile)

        if "landuse_any_other" in mapathon_info['types_of_mapping']:
            with open(os.path.join(output_dir, 'landuse_farmland.json'), 'w') as outfile:
                json.dump(project_changes['landuse_farmland'], outfile)
            with open(os.path.join(output_dir, 'landuse_orchard.json'), 'w') as outfile:
                json.dump(project_changes['landuse_orchard'], outfile)
            with open(os.path.join(output_dir, 'landuse_any_other.json'), 'w') as outfile:
                json.dump(project_changes['landuse_any_other'], outfile)

        if "highway" in mapathon_info['types_of_mapping']:
            with open(os.path.join(output_dir, 'highways_path.json'), 'w') as outfile:
                json.dump(project_changes['highway_path'], outfile)
            # print(len(highways_primary))
            with open(os.path.join(output_dir, 'highways_primary.json'), 'w') as outfile:
                json.dump(project_changes['highway_primary'], outfile)
            # print(len(highways_residential))
            with open(os.path.join(output_dir, 'highways_residential.json'), 'w') as outfile:
                json.dump(project_changes['highway_residential'], outfile)
            # print(len(highways_secondary))
            with open(os.path.join(output_dir, 'highways_secondary.json'), 'w') as outfile:
                json.dump(project_changes['highway_secondary'], outfile)
            # print(len(highways_service))
            with open(os.path.join(output_dir, 'highways_service.json'), 'w') as outfile:
                json.dump(project_changes['highway_service'], outfile)
            # print(len(highways_tertiary))
            with open(os.path.join(output_dir,'highways_tertiary.json'), 'w') as outfile:
                json.dump(project_changes['highway_tertiary'], outfile)
            # print(len(highways_track))
            with open(os.path.join(output_dir, 'highways_track.json'), 'w') as outfile:
                json.dump(project_changes['highway_track'], outfile)
            # print(len(highways_unclassified))
            with open(os.path.join(output_dir, 'highways_unclassified.json'), 'w') as outfile:
                json.dump(project_changes['highway_unclassified'], outfile)
            # print(len(highways_road))
            with open(os.path.join(output_dir, 'highways_road.json'), 'w') as outfile:
                json.dump(project_changes['highway_road'], outfile)
            # print(len(highways_footway))
            with open(os.path.join(output_dir, 'highways_footway.json'), 'w') as outfile:
                json.dump(project_changes['highway_footway'], outfile)

    def convert_mapathon_id(self, mapathon_id):
        if '-' in mapathon_id:
            mapathon = self.get_mapathon_by_stat_task_id(mapathon_id)
            #print(mapathon)
            mapathon_id = str(mapathon['_id'])

        return mapathon_id

    def get_mapathon_changes(self, mapathon_id, type_of_mapping):

        mapathon_id = self.convert_mapathon_id(mapathon_id)

        input_dir = os.path.join(MapathonsStorage.OUTPUT_BASE_PATH, mapathon_id)

        sub_dirs = self.get_immediate_subdirectories(input_dir)

        data = {}

        if (len(sub_dirs) == 0):
            return self.get_mapathon_changes_from_dir(input_dir, type_of_mapping)
        else:
            for sub_dir in sub_dirs:
                data[sub_dir] = self.get_mapathon_changes_from_dir(os.path.join(input_dir, sub_dir), type_of_mapping)
            return data
    
    def get_mapathon_changes_from_dir(self, input_dir, type_of_mapping):
        if type_of_mapping == "building":
            with open(os.path.join(input_dir, 'buildings.json'), 'r') as infile:
                data = json.load(infile)

        elif type_of_mapping == "landuse_residential":
            with open(os.path.join(input_dir, 'residential_areas.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "landuse_farmland":
            with open(os.path.join(input_dir, 'landuse_farmland.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "landuse_orchard":
            with open(os.path.join(input_dir, 'landuse_orchard.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "landuse_any_other":
            with open(os.path.join(input_dir, 'landuse_any_other.json'), 'r') as infile:
                data = json.load(infile)

        elif type_of_mapping == "highways_primary":
            with open(os.path.join(input_dir, 'highways_primary.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_secondary":
            with open(os.path.join(input_dir, 'highways_secondary.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_tertiary":
            with open(os.path.join(input_dir, 'highways_tertiary.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_unclassified":
            with open(os.path.join(input_dir, 'highways_unclassified.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_residential":
            with open(os.path.join(input_dir, 'highways_residential.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_service":
            with open(os.path.join(input_dir, 'highways_service.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_track":
            with open(os.path.join(input_dir, 'highways_track.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_path":
            with open(os.path.join(input_dir, 'highways_path.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_footway":
            with open(os.path.join(input_dir, 'highways_footway.json'), 'r') as infile:
                data = json.load(infile)
        elif type_of_mapping == "highways_road":
            with open(os.path.join(input_dir, 'highways_road.json'), 'r') as infile:
                data = json.load(infile)

        return data

    def store_mapathon_users(self, mapathon_id, mapathon_users):
        output_dir = os.path.join(MapathonsStorage.OUTPUT_BASE_PATH, str(mapathon_id))
        os.makedirs(output_dir, exist_ok=True)

        # "'mapathon_users': self.mapathon_users
        with open(os.path.join(output_dir, 'usernames.json'), 'w') as outfile:
            json.dump(mapathon_users, outfile)

    def get_immediate_subdirectories(self, a_dir):
        return [name for name in os.listdir(a_dir) if os.path.isdir(os.path.join(a_dir, name))]
