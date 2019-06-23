import json
from functools import reduce
from datetime import datetime
from sys import stdout
import time

import requests

from .AnalysisBase import AnalysisBase
from .utils import AUTH, JSON_GIT_TREE


class CommitAnalysis(AnalysisBase):

    GET_TREE_URI = 'https://api.github.com/repos/{}/{}/git/trees/{}'
    
    # How many nested folders will be included in the analysis
    # Usually some big enough number to guarantee 
    MAX_RECURSION_DEPTH = 3000

    def __init__(self, repo_owner: str, repo_name: str, commit_sha: str, commit_datetime: str, auth: AUTH=None):
        AnalysisBase.__init__(self, repo_owner, repo_name, auth)
        self.commit_sha = commit_sha
        self.commit_uri = self.GET_TREE_URI.format(self.repo_owner, self.repo_name, self.commit_sha)
        self.commit_timestamp = datetime.strptime(commit_datetime, '%Y-%m-%dT%H:%M:%SZ').timestamp()

    def compute_tree_blob_size(self, tree: JSON_GIT_TREE) -> int:
        return reduce(lambda acumul, obj: acumul + obj.get('size', 0), tree.get('tree', []), 0)

    def compute_commit_tree_blob_size(self) -> int:
        res = requests.get(self.commit_uri, params={'recursive': self.MAX_RECURSION_DEPTH}, auth=self.auth)
        
        if res.headers.get('Retry-After', None) is not None:
            time.sleep(int(res.headers['Retry-After']))
            return self.compute_commit_tree_blob_size()

        tree = json.loads(res.content)
        isTruncated = tree.get('truncated', None)
        if isTruncated:
            print('Commit {} tree payload truncated'.format(self.commit_sha), file=stdout)
        return self.compute_tree_blob_size(tree)
