
from threading import Thread, Condition
import requests
import geopandas as gpd
from geojson import Feature, FeatureCollection, MultiPolygon
import shapely.geometry as sgeom
from shapely.ops import unary_union
from shapely.geometry import shape
from shapely.geometry import Polygon
from shapely.geometry import MultiPolygon as ShapelyMultiPolygon
import os
from lxml import html, etree
import dateutil
import traceback
from pprint import pprint

from mapathon_analyzer import MapathonChangeCreator
from user_list import UserList
from mapathons_storage import MapathonsStorage

class MapathonStatistics(object):
    """
    Functionality for the statistics creation task run as a thread.
    """

    def __init__(self, stat_task_uuid, client_data):
        self.mapathons_storage = MapathonsStorage()
        self.stat_task_uuid = stat_task_uuid
        self.client_data = client_data
        self.mapathon_change_creator = MapathonChangeCreator()
        self.mapathon_changes = []
        self.mapathon_users = []
        self.mapathon_tags = None


        self.state = {
            'name': 'initialized',
            'state_progress': 100
        }

    def get_state(self):

        if self.state['name'] == 'creating_mapathon_changes':
            self.state['state_progress'] = self.mapathon_change_creator.get_analysis_progress()

        return self.state

    def start_task(self):

        self.thread = Thread(target=self.run_stats_creation, args=())
        self.thread.start()

        #self.run_stats_creation()

    def run_stats_creation(self):
        try:
            print(self.stat_task_uuid)
            print(self.client_data)

            for project_number in self.client_data['project_numbers']:

                print(project_number)

                self.state = {
                    'name': 'getting_project_data',
                    'state_progress': 0
                }

                status_code = self.get_project_data(project_number)

                if status_code != 200:
                    self.state = {
                        'name': 'error',
                        'state_progress': 0
                    }
                    return

                self.state = {
                    'name': 'finding_project_countries',
                    'state_progress': 0
                }

                success = self.find_countries()

                if not success:
                    self.state = {
                        'name': 'error',
                        'state_progress': 0
                    }
                    return

                self.state = {
                    'name': 'finding_geofabrik_areas',
                    'state_progress': 0
                }

                success = self.find_geofabrik_areas()

                if not success:
                    self.state = {
                        'name': 'error',
                        'state_progress': 0
                    }
                    return

                self.state = {
                    'name': 'creating_mapathon_changes',
                    'state_progress': 0
                }

                project_changes = self.create_project_changes(project_number)

                self.mapathon_changes.append(project_changes)

            self.mapathon_tags = self.get_mapathon_tags()

            self.store_changes()

            self.state = {
                'name': 'storing_osm_changes',
                'state_progress': 0
            }

            self.store_to_page_list()

            self.state = {
                'name': 'storing_to_page_list',
                'state_progress': 0
            }
        except KeyboardInterrupt:
            raise
        except (KeyboardInterrupt, SystemExit):
            raise
        except:
            self.state = {
                'name': 'error',
                'state_progress': 0
            }
            print("Unexpected error: {}".format(traceback.format_exc()))

    def get_project_data(self, project_number):
        resp = requests.get('https://tasks.hotosm.org/api/v1/project/' + str(project_number))

        if resp.status_code == 200:
            self.project_data = resp.json()

            #print(self.project_data)

        return resp.status_code

    def find_countries(self):
        self.countries_of_interest = set()

        collection = FeatureCollection(self.project_data['tasks']['features'])
        project_tasks = gpd.GeoDataFrame.from_features(collection)
        #print(project_tasks.head(1))
        project_multipolygon = MultiPolygon(self.project_data['areaOfInterest']['coordinates'])
        shapely_multipolygon = sgeom.shape(project_multipolygon)

        countries = gpd.read_file(os.path.join(os.getcwd(), 'ne_10m_admin_0_countries', 'ne_10m_admin_0_countries.shp'))
        
        for index, project_task in project_tasks.iterrows():
            for index2, country in countries.iterrows():
                if project_task['geometry'].intersects(country['geometry']) and country['SOVEREIGNT'] not in self.countries_of_interest:
                    self.countries_of_interest.add(country['SOVEREIGNT'])
                    print(country['SOVEREIGNT'])

        # cond = Condition()
        # cond.acquire()
        # while True:
        #     cond.wait()

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
                    shapely_polygons = self.parse_polygon(lines)
                    #print(shapely_polygons[0])

                    self.find_areas_of_interest(subdir, file, project_tasks, shapely_polygons)

        max_dir_level = -1

        self.areas_for_osc_file_retrieval = []

        #print(self.areas_of_interest)
        # Retrieve osc file(s) only for the areas that are at the deepest level in the area hierarchy
        for key, item in self.areas_of_interest.items():
            dir_level = len(item['subdir'].split('/'))
            print(dir_level)
            if dir_level > max_dir_level:
                max_dir_level = dir_level
                self.areas_for_osc_file_retrieval = [item]
            elif dir_level == max_dir_level:
                self.areas_for_osc_file_retrieval.append(item)

        print('areas_for_osc_file_retrieval', self.areas_for_osc_file_retrieval)

        return True

    def find_areas_of_interest(self, subdir, file, project_tasks, shapely_polygons):
        for index, project_task in project_tasks.iterrows():
            if project_task['geometry'].intersects(shapely_polygons) and file not in self.areas_of_interest:
                self.areas_of_interest[file] = {
                    'subdir': subdir,
                    'file': file
                }
                print("Project tasks intersercing polygon: " + file)

    def create_project_changes(self, project_number):
        # find changes for the mapathon area during the mapathon

        self.project_feature_collection = self.create_project_polygon_feature_collection()

        self.osc_file_download_urls = []

        project_changes_for_all_areas = []

        for osc_area in self.areas_for_osc_file_retrieval:
            osc_file_download_url = self.find_osc_file(osc_area)
            print('osc_file_download_url', osc_file_download_url)
            self.osc_file_download_urls.append(osc_file_download_url)
            
            ######
            #self.mapathon_changes = self.mapathon_change_creator.create_mapathon_changes_from_URL(self.project_feature_collection, osc_file_download_url, self.client_data['mapathon_date'], self.client_data['mapathon_time_utc'])
            #print(self.mapathon_changes)
            #####

            area_name = osc_area['file'].split('.')[0]

            project_changes_for_all_areas.append(self.mapathon_change_creator.create_mapathon_changes_from_URL(area_name, project_number, self.project_feature_collection, osc_file_download_url, self.client_data['mapathon_date'], self.client_data['mapathon_time_utc']))
        #     for types_key in self.client_data['types_of_mapping']:
        #         for result_key, result_json in result.items():
        #             if result_key.startswith(types_key):
        #                 mapathon_changes_for_all_areas.append(result_json)

        return self.mapathon_change_creator.filter_same_changes(project_changes_for_all_areas)

    def create_project_polygon_feature_collection(self):
        #pprint(shape(self.project_data['areaOfInterest']).buffer(0))
        tasks = self.project_data['tasks']
        shape_tasks = [] 
        for feature in tasks['features']:
            shape_tasks.append(shape(feature['geometry']))

        project_tasks_shapely_union = unary_union(shape_tasks)
        if type(project_tasks_shapely_union) is sgeom.collection.GeometryCollection:
            print('GeometryCollection')
            geoms = [x.buffer(0) for x in shape(project_tasks_shapely_union).geoms]
        else:
            print('not GeometryCollection')
            geoms = [project_tasks_shapely_union.buffer(0)]
        print(geoms)

        geojson_features = []
        for geom in geoms:
            geojson_feature = Feature(geometry=geom, properties={})
            geojson_features.append(geojson_feature)
        feature_collection = FeatureCollection(geojson_features)
        #print(feature_collection)

        return feature_collection

    def get_analysis_results(self, project_number):
        return self.mapathon_change_creator.get_analysis_results(project_number)

    def get_mapathon_tags(self):
        return self.mapathon_change_creator.get_all_tags()

    def create_users_list(self):
        # find users who made changes for the mapathon area during the mapathon

        user_list = UserList()
        self.mapathon_users = user_list.find_users(self.mapathon_changes)

    def store_changes(self):
        # store found OSM changes and usernames of those who did the changes for the project area to a data store
        mapathon_data = {
            'stat_task_uuid': self.stat_task_uuid,
            'mapathon_info': self.client_data,
            'mapathon_changes': self.mapathon_changes,
            'mapathon_tags': self.mapathon_tags
            #'mapathon_users': self.mapathon_users
        }
        self.mapathon_id = self.mapathons_storage.store_mapathon(mapathon_data)

    def create_statistics_web_page(self):
        # TODO create a web page that visualizes the mapathon statistics
        # TODO use only the self.client_data.types_of_mapping
        # TODO make sure that the web client has the URL to the page available after this function finishes
        self.mapathon_webpage.create_mapathon_web_page(self.mapathon_id)

    def store_to_page_list(self):
        # TODO store the created statistics web page to the list that can be shown for the users on the web
        pass

    def find_osc_file(self, osc_area):
        """
        Find the osc file from Geofabrik that contains the changes for the mapathon day.
        """

        print(osc_area)

        geofabrik_base_dir = osc_area['subdir'].split('Geofabrik/')[1] + '/' + osc_area['file'].split('.poly')[0]
        print(geofabrik_base_dir)

        mapathon_timestamp_string = self.client_data['mapathon_date'] + 'T' + str(self.client_data['mapathon_time_utc']) + ':00:00Z'
        #print(mapathon_timestamp_string)
        mapathon_timestamp = dateutil.parser.parse(mapathon_timestamp_string) #datetime.datetime object

        download_url = 'http://download.geofabrik.de/' + geofabrik_base_dir + '-updates'
        print(download_url)

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


    def parse_polygon(self, lines):
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