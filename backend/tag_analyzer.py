from pprint import pprint

class TagAnalyzer:
    """
    Functionality for analyzing tags of the mapathon
    """

    def __init__(self):
        self.results = {
            'projects': {}
        }

    def analyze_tags(self, area_name, project_number, date, min_hour_utz, data):
        
        project_key = 'p' + str(project_number)

        if project_key not in self.results['projects']:
            self.results['projects'][project_key] = {
                'date': date,
                'min_hour_utz': min_hour_utz,
                'areas': {}
            }

        if area_name not in self.results['projects'][project_key]['areas']:
            self.results['projects'][project_key]['areas'][area_name] = {
                'tags': {}
            }

        for key, features in data.items():
            for feature in features:
                for key, value in feature['properties']['tags'].items():
                    key_for_mongodb = key.replace(".", "[dot]")
                    key_for_mongodb = key_for_mongodb.replace("$", "[dollar]")
                    if key_for_mongodb not in self.results['projects'][project_key]['areas'][area_name]['tags']:
                        value_for_mongodb = value.replace(".", "[dot]")
                        value_for_mongodb = value_for_mongodb.replace("$", "[dollar]")
                        self.results['projects'][project_key]['areas'][area_name]['tags'][key_for_mongodb] = {}
                        self.results['projects'][project_key]['areas'][area_name]['tags'][key_for_mongodb][value_for_mongodb] = 1
                    else:
                        value_for_mongodb = value.replace(".", "[dot]")
                        value_for_mongodb = value_for_mongodb.replace("$", "[dollar]")
                        if value_for_mongodb not in self.results['projects'][project_key]['areas'][area_name]['tags'][key_for_mongodb]:
                            self.results['projects'][project_key]['areas'][area_name]['tags'][key_for_mongodb][value_for_mongodb] = 1
                        else:
                            self.results['projects'][project_key]['areas'][area_name]['tags'][key_for_mongodb][value_for_mongodb] += 1

        pprint(self.results)

    def get_analysis_results(self, project_number):
        project_key = 'p' + str(project_number)
        return self.results['projects'][project_key]

    def get_all_tags(self):
        return self.results
