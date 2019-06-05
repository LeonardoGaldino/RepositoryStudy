from sys import argv
import requests
import json
from functools import reduce
from typing import Any, Dict

from tasks.RepositoryAnalysis import RepositoryAnalysis

API_URL = 'https://api.github.com'
COMMIT_URL = API_URL + '/repos/{}/{}/git/trees/{}'

JSON_TYPE = Dict[str, Any]
'''
	Use pagination:
		1) per_page specifies size of a page to retrieve
		2) page specify the page number being fetched
		3) Link header gives information about the next page and the last
'''
def getURI(repo_owner: str, repo: str, commit_sha: str) -> str:
	return COMMIT_URL.format(repo_owner, repo, commit_sha) + '?recursive=1500'

def fetchData(repo_owner: str, repo: str, commit_sha: str) -> str:
	req = requests.get(getURI(repo_owner, repo, commit_sha))
	return req.content.decode('utf-8')

def computeCommitSize(tree: JSON_TYPE) -> float:
	return reduce(lambda acumul, obj: acumul + obj.get('size', 0), tree['tree'], 0)

def computeCommitDiff(tree1: JSON_TYPE, tree2: JSON_TYPE) -> float:
	return abs(computeCommitSize(tree1) -  computeCommitSize(tree2))

def fetchAndComputeCommitsDiff(repo_owner: str, repo: str, c1_sha: str, c2_sha: str) -> float:
	c1_raw = fetchData(repo_owner, repo, c1_sha)
	c2_raw = fetchData(repo_owner, repo, c2_sha)

	c1_content = json.loads(c1_raw)
	c2_content = json.loads(c2_raw)

	return computeCommitDiff(c1_content, c2_content)


def main():
	if len(argv) != 5:
		print('Expected four inputs: Repository owner, repository name, commit1 and commit2 SHA-1.')
		return
	RepositoryAnalysis(argv[1], argv[2]).run_analysis()
	print(fetchAndComputeCommitsDiff(argv[1], argv[2], argv[3], argv[4]))

if __name__ == '__main__':
	main()
