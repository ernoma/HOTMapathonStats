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
                    if key not in self.results['projects'][project_key]['areas'][area_name]['tags']:
                        self.results['projects'][project_key]['areas'][area_name]['tags'][key] = {}
                        self.results['projects'][project_key]['areas'][area_name]['tags'][key][value] = 1
                    else:
                        if value not in self.results['projects'][project_key]['areas'][area_name]['tags'][key]:
                            self.results['projects'][project_key]['areas'][area_name]['tags'][key][value] = 1
                        else:
                            self.results['projects'][project_key]['areas'][area_name]['tags'][key][value] += 1

        pprint(self.results)

    def get_analysis_results(self, project_number):
        project_key = 'p' + str(project_number)
        return self.results['projects'][project_key]

    def get_all_tags(self):
        return self.results
