from pprint import pprint

class TagAnalyzer:
    """
    Functionality for analyzing tags of the mapathon
    """

    def __init__(self):
        self.results = {}

    def analyze_tags(self, project_number, date, min_hour_utz, data):

        self.results[project_number] = {
            'date': date,
            'min_hour_utz': min_hour_utz,
            'tags': {}
        }

        for key, features in data.items():
            for feature in features:
                for key, value in feature['properties']['tags'].items():             
                    if key not in self.results[project_number]['tags']:
                        self.results[project_number]['tags'][key] = {}
                        self.results[project_number]['tags'][key][value] = 1
                    else:
                        if value not in self.results[project_number]['tags'][key]:
                            self.results[project_number]['tags'][key][value] = 1
                        else:
                            self.results[project_number]['tags'][key][value] += 1

        pprint(self.results)