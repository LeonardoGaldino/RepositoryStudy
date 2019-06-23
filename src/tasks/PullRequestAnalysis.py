from sys import stdout
import json
from typing import List
from datetime import datetime
import time

import requests

from .AnalysisBase import AnalysisBase
from .CommitAnalysis import CommitAnalysis
from .utils import AUTH, OBJECT


class PullRequestAnalysis(AnalysisBase):

    GET_PULL_URI = 'https://api.github.com/repos/{}/{}/pulls/{}'
    LIST_COMMITS_URI = 'https://api.github.com/repos/{}/{}/pulls/{}/commits'

    def __init__(self, repo_owner: str, repo_name: str, repo_data: OBJECT, pr_number: str, auth: AUTH=None):
        AnalysisBase.__init__(self, repo_owner, repo_name, auth)
        self.pr_number = pr_number
        self.pull_uri = self.GET_PULL_URI.format(self.repo_owner, self.repo_name, self.pr_number)
        self.commits_uri = self.LIST_COMMITS_URI.format(self.repo_owner, self.repo_name, self.pr_number)
        self.repo_data = repo_data
        self.state = 'unknown'

    def run_analysis(self) -> int:
        print("Starting to analyze PullRequest number {} from repository {}...".format(self.pr_number, self.repo_name), file=stdout)
        parent_commit = self.get_pull_parent_commit()
        parent_size = parent_commit.compute_commit_tree_blob_size()
        commits_generator = self.list_commits()
        pr_waste = 0 # -parent_commit.compute_commit_tree_blob_size()
        num_commits = 0
        while True:
            try:
                commits = list(next(commits_generator))
                num_commits += len(commits)
                pr_waste += self.compute_commits_waste(commits, parent_size)
            except StopIteration:
                break
        print("Finished analyzing PullRequest number {} from repository {}...".format(self.pr_number, self.repo_name), file=stdout)
        self.repo_data[self.pr_number] = {
            'waste': pr_waste,
            'num_commits': num_commits,
            'status': self.state,
        }
        return pr_waste

    def compute_commits_waste(self, commits: List[CommitAnalysis], parent_size: int) -> int:
        commits.sort(key=lambda commit: commit.commit_timestamp)
        sizes = []
        waste = 0
        for i in range(len(commits)):
            commit = commits[i]
            commit_size = commit.compute_commit_tree_blob_size()
            if i == 0:
                waste += abs(commit_size - parent_size)
            else:
                waste += abs(commit_size - sizes[i-1])
            sizes.append(commit_size)
        return waste

    def list_commits(self) -> List[CommitAnalysis]:
        page_num = 1
        while True:
            res = requests.get(self.commits_uri, params={'page': page_num}, auth=self.auth)

            if res.headers.get('Retry-After', None) is not None:
                time.sleep(int(res.headers['Retry-After']))
                continue

            commits = json.loads(res.content)
            try:
                yield map(lambda commit: CommitAnalysis(self.repo_owner, self.repo_name, commit['sha'], 
                    commit['commit']['committer']['date'], self.auth), commits)
            except KeyError as e:
                print(e)
                print('Problematic commit {}. Payload as follow:')
                for commit in commits:
                    print(commit)
                return []

            pagination_info = res.headers.get('Link', None)
            if pagination_info is None or not ('rel="next"' in pagination_info):
                break
            page_num += 1

    def get_pull_parent_commit(self) -> CommitAnalysis:
        res = requests.get(self.pull_uri, auth=self.auth)

        if res.headers.get('Retry-After', None) is not None:
            time.sleep(int(res.headers['Retry-After']))
            return self.get_pull_parent_commit()

        pull = json.loads(res.content)
        if pull.get('base', None) is None:
            print('Problematic pull number {}. Payload follows:'.format(self.pr_number))
            print(pull)

        if pull['state'] == 'open':
            self.state = 'open'
        elif pull['state'] == 'closed':
            self.state = 'abandoned' if pull['merged_at'] is None else 'merged'

        print("Pull {}. Status {}. MergedAt {}.".format(self.pr_number, pull['state'], pull['merged_at']))

        # Date of this commit doesn't really matter since it is not being sorted
        now_iso = datetime.now().isoformat().split('.')[0]+'Z'
        return CommitAnalysis(self.repo_owner, self.repo_name, pull['base']['sha'], now_iso, auth=self.auth)
    