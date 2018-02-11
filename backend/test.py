#!/usr/bin/env python3

import unittest
import uuid

import stats_task
import mapathon_analyzer
from mapathons_storage import MapathonsStorage

class StatsTaskTest(unittest.TestCase):

    def setUp(self):
        self.client_data = {
            'project_number': '3567',
            'mapathon_date': '2018-01-26',
            'mapathon_time_utc': 16,
            'types_of_mapping': ["building", "landuse_residential", "highway"]
        }

        # self.country = {
        #     'name': 'central-african-republic',
        #     'continent_name': 'africa'
        # }

        # self.country = {
        #     'name': 'germany',
        #     'continent_name': 'europe'
        # }

        # Uniquely dentifies the statistics creation task
        self.stat_task_uuid = uuid.uuid1()

        self.new_stat_task = stats_task.MapathonStatistics(self.stat_task_uuid, self.client_data)

        self.mapathon_change_creator = mapathon_analyzer.MapathonChangeCreator()

    def test_find_osc_file(self):
        pass
        #osc_file_download_url = self.new_stat_task.find_osc_file(self.country)
        #self.assertEqual(osc_file_download_url, 'http://download.geofabrik.de/europe/germany-updates/000/001/755.osc.gz')

    def test_find_geofabrik_areas(self):
        pass
        # status_code = self.new_stat_task.get_project_data()
        # self.assertEqual(status_code, 200)
        # self.new_stat_task.find_geofabrik_areas()
        # self.new_stat_task.create_mapathon_changes()
        # self.assertEqual(self.new_stat_task.osc_file_download_urls[0], 'http://download.geofabrik.de/north-america/mexico-updates/000/001/754.osc.gz')

    def test_create_project_polygon_feature_collection(self):
        pass
        #status_code = self.new_stat_task.get_project_data()
        #self.assertEqual(status_code, 200)
        #project_feature_collection = self.new_stat_task.create_project_polygon_feature_collection()
        # TODO

    def test_filter_same_changes(self):
        # use the filter_same_changes function in the mapathon_analyzer.py
        # for the two osc files that are actually same file twice
        # and assert that the result is changes from only the other osc file
        pass
        # downloadURL = 'http://download.geofabrik.de/north-america/mexico-updates/000/001/774.osc.gz'
        # status_code = self.new_stat_task.get_project_data()
        # self.assertEqual(status_code, 200)
        # project_polygons = self.new_stat_task.create_project_polygon_feature_collection()
        # mapathon_changes = self.mapathon_change_creator.create_mapathon_changes_from_URL(project_polygons, downloadURL, self.client_data['mapathon_date'], self.client_data['mapathon_time_utc'])
        # filtered_mapathon_changes = self.mapathon_change_creator.filter_same_changes([mapathon_changes, mapathon_changes])
        # self.assertSequenceEqual(mapathon_changes, filtered_mapathon_changes)

    def test_mongodb_atlas_connect(self):
        mapathons_storage = MapathonsStorage()
        mapathons_storage.initialize()
        self.assertIsNotNone(mapathons_storage.mongo_client)
        self.assertIsNotNone(mapathons_storage.db)
        serverStatusResult = mapathons_storage.db.command("serverStatus")
        self.assertIsNotNone(serverStatusResult['opcounters'])

if __name__ == '__main__':
    unittest.main()
