#!/usr/bin/env python3

import stats_task
import uuid

client_data = {
    'project_number': 3567,
    'mapathon_date': '2018-01-06',
    'mapathon_time_utc': 16,
    'types_of_mapping': ["building_yes", "landuse_residential", "highway"]
}

# Uniquely dentifies the statistics creation task
stat_task_uuid = uuid.uuid1()

new_stat_task = stats_task.MapathonStatistics(stat_task_uuid, client_data)

# country = {
#     'name': 'central-african-republic',
#     'continent_name': 'africa'
# }

country = {
    'name': 'germany',
    'continent_name': 'europe'
}

new_stat_task.find_osc_file(country)

