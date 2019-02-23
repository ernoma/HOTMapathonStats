import uuid


import stats_task

if __name__ == '__main__':
    client_data = {
        'project_numbers': '3160,4323',
        'mapathon_date': '2018-10-29',
        'mapathon_time_utc': 11,
        'mapathon_title': 'HOT Mapathon, Turku October 2018',
        'types_of_mapping': ["building", "landuse_residential", "highway"]
    }

    # Uniquely dentifies the statistics creation task
    stat_task_uuid = uuid.uuid1()

    new_stat_task = stats_task.MapathonStatistics(stat_task_uuid, client_data)
    new_stat_task.start_task()

    result = {
        'status': 'OK',
        'stat_task_uuid': stat_task_uuid,
        'client_data': client_data
    }
    
    print(result)