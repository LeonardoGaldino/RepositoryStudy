from sys import stdout
from typing import List
from concurrent.futures import ThreadPoolExecutor
import json
import time

import requests

from .AnalysisBase import AnalysisBase
from .PullRequestAnalysis import PullRequestAnalysis
from .utils import AUTH


'''
    | repository_owner | repository | pr_number | waste_in_size | num_commits | status |

    * Status can be: abandoned, merged, open
'''


class RepositoryAnalysis(AnalysisBase):

    LIST_PRS_URI = 'https://api.github.com/repos/{}/{}/pulls'

    def __init__(self, repo_owner: str, repo_name: str, max_threads: int, max_prs: int, auth: AUTH=None):
        AnalysisBase.__init__(self, repo_owner, repo_name, auth)
        self.max_threads = max_threads
        self.max_prs = max_prs
        self.pulls_uri = self.LIST_PRS_URI.format(self.repo_owner, self.repo_name)
        self.repo_data = {}

    def run_analysis(self):
        print("Starting to analyze {} repository from {}...".format(self.repo_name, self.repo_owner), file=stdout)
        prs_generator = self.list_pull_requests()
        repo_waste = 0
        pr_count = 0
        while True:
            with ThreadPoolExecutor(max_workers=self.max_threads-1) as executor:
                try:
                    prs = list(next(prs_generator))
                    computations = [executor.submit(pr.run_analysis) for pr in prs]
                    repo_waste += sum([computation.result() for computation in computations])

                    print('Processed {} pulls, from pull {} to {}'.format(len(prs), pr_count, pr_count+len(prs)), file=stdout)
                    pr_count += len(prs)
                    if pr_count >= self.max_prs:
                        break
                except StopIteration:
                    break
        print("Finished analyzing {} repository from {}...".format(self.repo_name, self.repo_owner), file=stdout)
        with open(self.repo_owner + '_' + self.repo_name, 'w') as f:
            f.write(json.dumps(self.repo_data, indent=4))
        print(repo_waste)
        
    def list_pull_requests(self) -> List[PullRequestAnalysis]:
        page_num = 1
        while True:
            res = requests.get(self.pulls_uri, params={'page': page_num, 'state': 'all'}, auth=self.auth)

            if res.headers.get('Retry-After', None) is not None:
                time.sleep(res.headers['Retry-After'])
                continue

            pulls = json.loads(res.content)
            yield map(lambda pull: PullRequestAnalysis(self.repo_owner, self.repo_name, self.repo_data, pull['number'], self.auth), pulls)

            pagination_info = res.headers.get('Link', None)
            if pagination_info is None or not ('rel="next"' in pagination_info):
                break
            page_num += 1

