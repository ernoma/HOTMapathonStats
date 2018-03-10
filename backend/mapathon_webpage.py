
import os
from pprint import pprint

class MapathonWebPage(object):
    """
    Functionality for
    - creating mapathon web page (HTML) and corresponding js and css files
    - storing the created HTML, js and css files.
    """

    STORE_BASE_PATH = "mapathon_stats"
    MAPATHON_TEMPLATE_BASE_PATH = "templates"

    def __init__(self, mapathons_storage):
        self.mapathons_storage = mapathons_storage

    def create_mapathon_web_page(self, mapathon_id):
        # TODO use the mapathon_id to retrieve mapathon data from the MapathonsStorage defined in the
        # mapathons_storage.py and create mapathon web page (HTML) and corresponding js and css files
        # based on the data
        self.mapathon_data = self.mapathons_storage.get_mapathon_by_ID(mapathon_id)

        self.mapathon_base_filename = 'mapathon_' + \
            self.mapathon_data['mapathon_info']['mapathon_date'] + '_' + \
            str(self.mapathon_data['mapathon_info']['mapathon_time_utc']) + '_' + \
            self.mapathon_data['mapathon_info']['project_number']

        with open(os.path.join(MapathonWebPage.MAPATHON_TEMPLATE_BASE_PATH, 'mapathon.html')) as template_html_file:
            self.template_html = template_html_file.read()
            pprint(self.template_html)
        with open(os.path.join(MapathonWebPage.MAPATHON_TEMPLATE_BASE_PATH, 'mapathon.css')) as template_css_file:
            self.template_css = template_css_file.read()
            pprint(self.template_css)
        with open(os.path.join(MapathonWebPage.MAPATHON_TEMPLATE_BASE_PATH, 'mapathon.js')) as template_js_file:
            self.template_js = template_js_file.read()
            pprint(self.template_js)

    def store_mapathon_web_page(self):
        # TODO store the created HTML, js and css files
        # TODO make name safe
        # TODO use mapathon end_time (optional)
        self.mapathon_base_path = os.path.join(
            MapathonWebPage.STORE_BASE_PATH,
            self.mapathon_base_filename)

        print(self.mapathon_base_path)
