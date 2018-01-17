
from threading import Thread, Condition
import requests
import geopandas as gpd
from geojson import FeatureCollection, MultiPolygon
import shapely.geometry as sgeom
from shapely.ops import unary_union
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon as ShapelyMultiPolygon
import os
from lxml import html, etree
import dateutil
import mapathon_analyzer

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
            'name': 'finding_geofabrik_areas',
            'state_progress': 0
        }

        success = self.find_geofabrik_areas()

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
        shapely_multipolygon = sgeom.shape(project_multipolygon)
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
            country_of_interest = None
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

    def find_geofabrik_areas(self):
        # Find Geofabrik area(s) that contain wholly or partially the project area(s)

        # TODO check if there are updated areas on the server

        collection = FeatureCollection(self.project_data['tasks']['features'])
        project_tasks = gpd.GeoDataFrame.from_features(collection)

        self.areas_of_interest = {}

        cwd = os.getcwd()
        #print(cwd)
        geofabrik_dir = os.path.join(cwd, "Geofabrik")
        for subdir, dirs, files in os.walk(geofabrik_dir):
            #print(subdir)
            #print(dirs)
            #print(files)
            for file in files:
                with open(os.path.join(subdir, file), 'r') as poly_file:
                    lines = poly_file.readlines()
                    lines = [x.strip() for x in lines]
                    # TODO handle South Africa and Lesotho as special case.
                    # TODO Use south-africa-and-lesotho.poly and lesotho.poly and not south-africa.poly
                    #print(file)
                    shapely_polygons = self.parse_poly(lines)
                    #print(shapely_polygons[0])

                    for index, project_task in project_tasks.iterrows():
                        if project_task['geometry'].intersects(shapely_polygons):
                            if file not in self.areas_of_interest:
                                self.areas_of_interest[file] = {
                                    'subdir': subdir,
                                    'file': file
                                }
                                print("Project tasks intersercing poly: " + file)
                                #print(self.areas_of_interest)
                        #else:
                        #    print("Project tasks dows not interserct poly: " + file)

        max_dir_level = -1

        areas_for_osc_file_retrieval = []

        #print(self.areas_of_interest)
        # Retrieve osc file(s) only for the areas that are at the deepest level in the area hierarchy
        for key, item in self.areas_of_interest.items():
            dir_level = len(item['subdir'].split('/'))
            print(dir_level)
            if dir_level > max_dir_level:
                max_dir_level = dir_level
                areas_for_osc_file_retrieval = [item]
            elif dir_level == max_dir_level:
                areas_for_osc_file_retrieval.append(item)

        print(areas_for_osc_file_retrieval)

    def create_mapathon_changes(self):
        # TODO find changes and store the changes to the json files

        for country in self.countries_of_interest:
            osc_file_download_url = self.find_osc_file(country)
            # mapathon_analyzer.createMapathonChangesFromURL(osc_file_download_url, , self.client_data['mapathon_date'])

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

    def find_osc_file(self, country):
        """
        TODO Find the osc file from Geofabrik that contains the changes for the mapathon day.
        """

        mapathon_timestamp_string = self.client_data['mapathon_date'] + 'T' + str(self.client_data['mapathon_time_utc']) + ':00:00Z'
        #print(mapathon_timestamp_string)
        mapathon_timestamp = dateutil.parser.parse(mapathon_timestamp_string) #datetime.datetime object

        download_url = 'http://download.geofabrik.de/' + country['continent_name'] + '/' + country['name'] + '-updates'

        page = requests.get(download_url)
        webpage = html.fromstring(page.content)
        subpage_urls = webpage.xpath('//a/@href[substring-before(., "/")]')
        #print(subpage_urls)
        for subpage_url in subpage_urls:
            subpage_download_url = download_url + '/' + subpage_url
            subpage = requests.get(subpage_download_url)
            subwebpage = html.fromstring(subpage.content)
            subsubpage_urls = subwebpage.xpath('//a/@href[substring-before(., "/")]')
            #print(subsubpage_urls)
            for subsubpage_url in subsubpage_urls:
                osc_file_dir_page_download_url = subpage_download_url + subsubpage_url
                osc_file_dir_page = requests.get(osc_file_dir_page_download_url)
                osc_file_dir_webpage = html.fromstring(osc_file_dir_page.content)
                osc_state_file_urls = osc_file_dir_webpage.xpath('//a/@href[contains(., ".state.txt")]')
                #print(osc_state_file_urls)
                for osc_state_file_url in osc_state_file_urls:
                    osc_state_file_download_url = osc_file_dir_page_download_url + osc_state_file_url
                    osc_state_file = requests.get(osc_state_file_download_url)
                    lines = osc_state_file.text.splitlines()
                    #print(lines)
                    timestamp_string = lines[1].split('=')[1].replace('\\', '')
                    #print(timestamp_string) # 2017-10-03T20:43:03Z
                    osc_file_timestamp = dateutil.parser.parse(timestamp_string) #datetime.datetime object
                    if mapathon_timestamp.date() == osc_file_timestamp.date():
                        #print("osc file " + osc_state_file_url + " has date " + mapathon_timestamp_string)
                        osc_file_number = osc_state_file_url.split('.')[0]
                        osc_file_url = osc_file_number + '.osc.gz'
                        osc_file_download_url = osc_file_dir_page_download_url + osc_file_url
                        print(osc_file_download_url)
                        return osc_file_download_url


    def parse_poly(self, lines):
        # See also https://wiki.openstreetmap.org/wiki/Osmosis/Polygon_Filter_File_Format and
        # http://shapely.readthedocs.io/en/stable/manual.html#polygons
        shapely_polygons = []
        coords = []
        in_ring = False
        for (index, line) in enumerate(lines):
            if index == 0:
                continue
            elif in_ring and line.strip() == 'END':
                # we are at the end of a ring, perhaps with more to come.
                in_ring = False
                shapely_polygons.append(Polygon(coords))
                coords = []
            elif in_ring:
                # we are in a ring and picking up new coordinates.
                parts = line.split()
                #print(parts)
                coords.append((float(parts[0]), float(parts[1])))
            elif not in_ring and line.strip() == 'END':
                # we are at the end of the whole polygon.
                break
            elif not in_ring:
                # we are at the start of a polygon part.
                in_ring = True
                continue

        return ShapelyMultiPolygon(shapely_polygons)