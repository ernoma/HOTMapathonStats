#!/usr/bin/env python3

import unittest
import stats_task
import uuid

class StatsTaskTest(unittest.TestCase):

    def setUp(self):
        self.client_data = {
            'project_number': '3567',
            'mapathon_date': '2018-01-06',
            'mapathon_time_utc': 16,
            'types_of_mapping': ["building_yes", "landuse_residential", "highway"]
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
        status_code = self.new_stat_task.get_project_data()
        self.assertEqual(status_code, 200)
        project_feature_collection = self.new_stat_task.createProjectPolygonFeatureCollection()
        # TODO

if __name__ == '__main__':
    unittest.main()
