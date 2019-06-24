from os import listdir
from json import loads as loads_json
import csv

def load_file_json(file_path):
   with open(file_path, 'r') as _file:
        content = _file.read()
        json = loads_json(content)
        return json

def generate_table():
    data_file_names = listdir('collected_data')
    with open('generated_table.csv', 'w') as out_table:
        fields = ['repository_owner', 'repository_name', 'pr_number', 'waste', 'num_commits', 'status']
        writer = csv.DictWriter(out_table, fieldnames=fields)
        writer.writeheader()
        for data_file_name in data_file_names:
            if data_file_name == '.gitignore':
                continue

            repo_owner, repo_name = data_file_name.split('_')
            file_path = 'collected_data/' + data_file_name
            json = load_file_json(file_path)
            for pr_num in json:
                writer.writerow({'repository_owner': repo_owner, 'repository_name': repo_name, 'pr_number': pr_num, **json[pr_num]})

if __name__ == '__main__':
    generate_table()