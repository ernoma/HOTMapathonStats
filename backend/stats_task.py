
from threading import Thread, Condition
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

        self.state = {
            'name': 'initialized',
            'state_progress': 100
        }

    def get_state(self):
        return self.state

    def start_task(self):

        self.thread = Thread(target=self.run_stats_creation, args=())
        self.thread.start()

        #self.run_stats_creation()

    def run_stats_creation(self):
        print(self.stat_task_uuid)
        print(self.client_data)

        self.state = {
            'name': 'getting_project_data',
            'state_progress': 0
        }

        status_code = self.get_project_data()

        if status_code != 200:
            self.state = 'error'
            return

        self.state = {
            'name': 'finding_project_countries',
            'state_progress': 0
        }

        success = self.find_countries()

        if not success:
            self.state = 'error'
            return

        self.state = {
            'name': 'creating_mapathon_changes',
            'state_progress': 0
        }

        self.create_mapathon_changes()

        self.state = {
            'name': 'creating_users_list',
            'state_progress': 0
        }

        self.create_users_list()

        self.state = {
            'name': 'creating_statistics_web_page',
            'state_progress': 0
        }

        self.create_statistics_web_page()

        self.state = {
            'name': 'storing_to_page_list',
            'state_progress': 0
        }

        self.store_to_page_list()

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

        self.countries_of_interest = set()
        for index, project_task in project_tasks.iterrows():
            for index2, country in countries.iterrows():
                if project_task['geometry'].intersects(country['geometry']):
                    if country['SOVEREIGNT'] not in self.countries_of_interest:
                        self.countries_of_interest.add(country['SOVEREIGNT'])
                        print(country['SOVEREIGNT'])

        # TODO modify to work with the create_mapathon_changes function
        cond = Condition()
        cond.acquire()
        while True:
            cond.wait()

        if len(self.countries_of_interest) == 0:
            return False

        return True

    def create_mapathon_changes(self):
        # TODO find changes and store the changes to the json files
        pass

    def create_users_list(self):
        # TODO find users who made changes for the mapathon area during the mapathon and store users to a json file
        pass

    def create_statistics_web_page(self):
        # TODO create a web page that visualizes the mapathon statistics
        # TODO make sure that the web client has the URL to the page available after this function finishes
        pass

    def store_to_page_list(self):
        # TODO store the created statistics web page to the list that can be shown for the users on the web
        pass
