import sys
from .PullRequestAnalysis import PullRequestAnalysis
from typing import List


class RepositoryAnalysis:

    def __init__(self, repo_owner: str, repo_name: str):
        self.repo_owner = repo_owner
        self.repo_name = repo_name

    def run_analysis(self):
        self.list_pull_requests()
        print("Starting to analyze %s repository from %s..." % (self.repo_name, self.repo_owner), file=sys.stderr)

    def list_pull_requests(self) -> List[PullRequestAnalysis]:
        return []

