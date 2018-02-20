
class MapathonWebPage(object):
    """
    Functionality for
    - creating mapathon web page (HTML) and corresponding js and css files
    - storing the created HTML, js and css files.
    """

    def __init__(self, mapathons_storage):
        self.mapathons_storage = mapathons_storage

    def create_mapathon_web_page(self, mapathon_id):
        # TODO use the mapathon_id to retrieve mapathon data from the MapathonsStorage defined in the
        # mapathons_storage.py and create mapathon web page (HTML) and corresponding js and css files
        # based on the data
        mapathon_data = self.mapathons_storage.get_mapathon_by_ID()

    def store_mapathon_web_page(self):
        pass
        # TODO store the created HTML, js and css files


