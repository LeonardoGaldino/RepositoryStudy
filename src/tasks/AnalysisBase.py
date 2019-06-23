from .utils import AUTH

class AnalysisBase:

    def __init__(self, repo_owner, repo_name, auth: AUTH=None):
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.auth = auth