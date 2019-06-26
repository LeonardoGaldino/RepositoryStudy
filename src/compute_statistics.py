from os import listdir
from json import loads as loads_json
from functools import reduce

# Pair (total_waste, num_commits)
def sum_by_status(data, status):
    return reduce(lambda acumul, pr_num: acumul if data[pr_num]['status'] != status else (acumul[0]+data[pr_num]['waste'], acumul[1]+data[pr_num]['num_commits']), data.keys(), (0,0)) 

def print_overall_stats(json, repo_owner, repo_name):
    data_open = sum_by_status(json, 'open')
    data_merged = sum_by_status(json, 'merged')
    data_abandoned = sum_by_status(json, 'abandoned')

    print('For {} from {}:'.format(repo_name, repo_owner))
    print('Open - total_waste: {}, total_commits {}.'.format(data_open[0], data_open[1]))
    print('Merged - total_waste: {}, total_commits {}.'.format(data_merged[0], data_merged[1]))
    print('Abandoned - total_waste: {}, total_commits {}.'.format(data_abandoned[0], data_abandoned[1]))

def print_field_stats(json, repo_owner, repo_name, field):
    stats_open = [json[k][field] for k in json.keys() if json[k]['status'] == 'open']
    stats_open_avg = sum(stats_open) / (len(stats_open) if len(stats_open) != 0 else 1)

    stats_merged = [json[k][field] for k in json.keys() if json[k]['status'] == 'merged']
    stats_merged_avg = sum(stats_merged) / (len(stats_merged) if len(stats_merged) != 0 else 1)

    stats_abandoned = [json[k][field] for k in json.keys() if json[k]['status'] == 'abandoned']
    stats_abandoned_avg = sum(stats_abandoned) / (len(stats_abandoned) if len(stats_abandoned) != 0 else 1)

    print('For {} from {} - Open {} average: {}'.format(repo_name, repo_owner, field, stats_open_avg))
    print('For {} from {} - Merged {} average: {}'.format(repo_name, repo_owner, field, stats_merged_avg))
    print('For {} from {} - Abandoned {} average: {}'.format(repo_name, repo_owner, field, stats_abandoned_avg))

def print_abandonment_percentage(json, repo_owner, repo_name):
    perc = reduce(lambda acumul, pr_num: acumul + 1 if json[pr_num]['status'] == 'abandoned' else acumul, json.keys(), 0) / len(json.keys())
    print('For {} from {}: {:.2f}% of PRs abandoned'.format(repo_name, repo_owner, 100*perc))

def compute_statistics():
    data = {}

    data_file_names = listdir('collected_data')
    for data_file_name in data_file_names:
        if data_file_name == '.gitignore':
            continue
            
        with open('collected_data/' + data_file_name, 'r') as _file:
            repo_owner, repo_name = data_file_name.split('_')
            content = _file.read()
            json = loads_json(content)
            print_overall_stats(json, repo_owner, repo_name)
            print_field_stats(json, repo_owner, repo_name, 'num_commits')
            print_field_stats(json, repo_owner, repo_name, 'waste')
            print_abandonment_percentage(json, repo_owner, repo_name)

if __name__ == '__main__':
    compute_statistics()