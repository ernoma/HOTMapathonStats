
import threading
import requests
import geopandas as gpd
from geojson import FeatureCollection, MultiPolygon
from shapely.geometry import shape
from shapely.ops import unary_union
import os

class MapathonStatistics(object):
    """
    Functionality for the statistics creation task run as a thread.
    """

    def __init__(self, stat_task_uuid, client_data):
        self.stat_task_uuid = stat_task_uuid
        self.client_data = client_data

        self.state = 'ok'

    def start_task(self):

        self.thread = threading.Thread(target=self.run_stats_creation, args=())
        self.thread.start()

        #self.run_stats_creation()


    def run_stats_creation(self):
        print(self.stat_task_uuid)
        print(self.client_data)

        status_code = self.get_project_data()

        if status_code != 200:
            self.state = 'error'
            return

        success = self.find_countries()

        if not success:
            self.state = 'error'
            return

    def get_project_data(self):

        resp = requests.get('https://tasks.hotosm.org/api/v1/project/' + self.client_data['project_number'])

        if resp.status_code == 200:
            self.project_data = resp.json()

            #print(self.project_data)

        return resp.status_code

    def find_countries(self):
        collection = FeatureCollection(self.project_data['tasks']['features'])
        project_tasks = gpd.GeoDataFrame.from_features(collection)
        #print(project_tasks.head(1))
        project_multipolygon = MultiPolygon(self.project_data['areaOfInterest']['coordinates'])
        shapely_multipolygon = shape(project_multipolygon)
        project_tasks_shapely_union = unary_union(shapely_multipolygon)
        #print(project_union)
        #project_tasks_union = gpd.GeoSeries(project_tasks_shapely_union)
        #project_tasks_union.plot(color='red')

        countries = gpd.read_file(os.path.join(os.getcwd(), 'ne_10m_admin_0_countries', 'ne_10m_admin_0_countries.shp'))
        #print(countries.head(2))
        #countries.plot(figsize=(8, 8))
        #import matplotlib.pyplot as plt
        #plt.show()

        countries_of_interest = set()
        for index, project_task in project_tasks.iterrows():
            for index2, country in countries.iterrows():
                if project_task['geometry'].intersects(country['geometry']):
                    if country['SOVEREIGNT'] not in countries_of_interest:
                        countries_of_interest.add(country['SOVEREIGNT'])
                        print(country['SOVEREIGNT'])

