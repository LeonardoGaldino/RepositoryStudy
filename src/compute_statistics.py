from os import listdir
from json import loads as loads_json
from functools import reduce

# Pair (total_waste, num_commits)
def sum_by_status(data, status):
    return reduce(lambda acumul, pr_num: acumul if data[pr_num]['status'] != status else (acumul[0]+data[pr_num]['waste'], acumul[1]+data[pr_num]['num_commits']), data.keys(), (0,0)) 

def print_stats(json, repo_owner, repo_name):
    data_open = sum_by_status(json, 'open')
    data_merged = sum_by_status(json, 'merged')
    data_abandoned = sum_by_status(json, 'abandoned')

    print('For {} from {}:'.format(repo_name, repo_owner))
    print('Open - total_waste: {}, total_commits {}.'.format(data_open[0], data_open[1]))
    print('Merged - total_waste: {}, total_commits {}.'.format(data_merged[0], data_merged[1]))
    print('Abandoned - total_waste: {}, total_commits {}.'.format(data_abandoned[0], data_abandoned[1]))

def t(json, repo_owner, repo_name):
    commits_open = [json[k]['num_commits'] for k in json.keys() if json[k]['status'] == 'open']
    commits_open_avg = sum(commits_open) / (len(commits_open) if len(commits_open) != 0 else 1)

    commits_merged = [json[k]['num_commits'] for k in json.keys() if json[k]['status'] == 'merged']
    commits_merged_avg = sum(commits_merged) / (len(commits_merged) if len(commits_merged) != 0 else 1)

    commits_abandoned = [json[k]['num_commits'] for k in json.keys() if json[k]['status'] == 'abandoned']
    commits_abandoned_avg = sum(commits_abandoned) / (len(commits_abandoned) if len(commits_abandoned) != 0 else 1)

    print('For {} from {} - Open commit number average: {}'.format(repo_name, repo_owner, commits_open_avg))
    print('For {} from {} - Merged commit number average: {}'.format(repo_name, repo_owner, commits_merged_avg))
    print('For {} from {} - Abandoned commit number average: {}'.format(repo_name, repo_owner, commits_abandoned_avg))

def compute_statistics():
    data = {}

    data_file_names = listdir('collected_data')
    for data_file_name in data_file_names:
        with open('collected_data/' + data_file_name, 'r') as _file:
            repo_owner, repo_name = data_file_name.split('_')
            content = _file.read()
            json = loads_json(content)
            print_stats(json, repo_owner, repo_name)
            t(json, repo_owner, repo_name)

            


if __name__ == '__main__':
    compute_statistics()