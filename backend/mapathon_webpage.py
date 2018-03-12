
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

            self.create_mapathon_html()

        with open(os.path.join(MapathonWebPage.MAPATHON_TEMPLATE_BASE_PATH, 'mapathon.css')) as template_css_file:
            self.template_css = template_css_file.read()
            pprint(self.template_css)
        with open(os.path.join(MapathonWebPage.MAPATHON_TEMPLATE_BASE_PATH, 'mapathon.js')) as template_js_file:
            self.template_js = template_js_file.read()
            pprint(self.template_js)

            self.create_mapathon_js()

    def create_mapathon_js(self):
        pass
        # TODO use reg expressions to create the final js

    def create_mapathon_html(self):
        # TODO Use Python string formatting or / flask templates to create the final html
        # {mapathon_title} = Monthly Missing Maps Mapathon at Finnish Red Cross HQ - September 2017
        # {mapathon_introduction_p1} = Data created on 14th of September 2017 from 17:00 to 23:44 (Finnish summer time).
        # {mapathon_introduction_p2} = Some statistics for our contributions on the <a href="http://tasks.hotosm.org/project/3453">#1880 - #3453 - Arua District Part 1</a> task in Uganda.
        '''
        {buildings_section} =

            <h3>Buildings</h3>

            <div class="row top-buffer bottom-buffer">
              <div class="col-md-3">Buildings, total count</div>
                  <div class="col-md-9"id="building_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
            </div>
            <hr>

        {residential_areas_section} =

            <h3>Residential Areas</h3>

            <div class="row top-buffer bottom-buffer">
              <div class="col-md-3">Residential areas, total count</div>
              <div class="col-md-9"id="res_area_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
            </div>
            <div class="row">
              <div class="col-md-3">Residential areas, total area</div>
              <div class="col-md-9" id="res_area_total_area_div"><i class="fa fa-spinner fa-pulse"></i></div>
            </div>
            <div class="row bottom-buffer">
              <div class="col-md-3">Residential areas, average area</div>
              <div class="col-md-9" id="res_area_avg_area_div"><i class="fa fa-spinner fa-pulse"></i></div>
            </div>
            <hr>

        {roads_section} =

            <h3>Roads and Paths</h3>

        <div class="row top-buffer bottom-buffer">
          <div class="col-md-3">Primary roads created, length</div>
          <div class="col-md-3" id="primary_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">Secondary roads created, length</div>
          <div class="col-md-3" id="secondary_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row">
          <div class="col-md-3">Tertiary roads created, length</div>
          <div class="col-md-3" id="tertiary_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">Unclassified roads created, length</div>
          <div class="col-md-3" id="un_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row">
          <div class="col-md-3">Residential roads created, length</div>
          <div class="col-md-3" id="res_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">Service roads created, length</div>
          <div class="col-md-3" id="service_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row">
          <div class="col-md-3">Tracks created, length</div>
          <div class="col-md-3" id="tracks_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">Paths created, length</div>
          <div class="col-md-3" id="paths_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row">
          <div class="col-md-3">Footways created, length</div>
          <div class="col-md-3" id="footway_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">(*) Other roads created, length</div>
          <div class="col-md-3" id="highway_road_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row top-buffer">
          <div class="col-md-3">Roads created, total length</div>
          <div class="col-md-9" id="roads_total_length_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row top-buffer">
          <div class="col-md-3">Primary roads, count</div>
          <div class="col-md-3" id="primary_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">Secondary roads, count</div>
          <div class="col-md-3" id="secondary_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row">
          <div class="col-md-3">Tertiary roads, count</div>
          <div class="col-md-3" id="tertiary_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">Unclassified roads, count</div>
          <div class="col-md-3" id="un_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row">
          <div class="col-md-3">Residential roads, count</div>
          <div class="col-md-3" id="res_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">Service roads, count</div>
          <div class="col-md-3" id="service_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row">
          <div class="col-md-3">Tracks, count</div>
          <div class="col-md-3" id="tracks_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">Paths, count</div>
          <div class="col-md-3" id="paths_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <div class="row">
          <div class="col-md-3">Footways created, count</div>
          <div class="col-md-3" id="footway_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
          <div class="col-md-3">(*) Other roads created, count</div>
          <div class="col-md-3" id="highway_road_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>

        <div class="row top-buffer bottom-buffer">
          <div class="col-md-3">Roads and paths, total count</div>
          <div class="col-md-3" id="roads_total_count_div"><i class="fa fa-spinner fa-pulse"></i></div>
        </div>
        <hr>
        <p id="data_note">(*) Other roads means ways that were tagged highway=road, highway=motorway, highway=trunk or highway=living_street. See the OSM <a href="https://wiki.openstreetmap.org/wiki/Highway_Tag_Africa">Highway Tag Africa wiki page</a> and the <a href="http://wiki.openstreetmap.org/wiki/Key:highway">highway tagging wiki</a> page for more information on the types.
		</p>
        '''
        pass

    def store_mapathon_web_page(self):
        # TODO store the created HTML, js and css files
        # TODO make name safe
        # TODO use mapathon end_time (optional)
        self.mapathon_base_path = os.path.join(
            MapathonWebPage.STORE_BASE_PATH,
            self.mapathon_base_filename)

        print(self.mapathon_base_path)
