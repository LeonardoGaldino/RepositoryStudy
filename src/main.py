from sys import argv, stderr, exit
from os import getenv

from tasks.RepositoryAnalysis import RepositoryAnalysis

def validate_configs():
	if len(argv) != 3:
		print('You should provide exactly 2 command-line arguments: repository owner and repository name.', file=stderr)
		exit(1)
		
	repo_owner = argv[1]
	repo_name = argv[2]
	username = getenv('GITHUB_USERNAME')
	password = getenv('GITHUB_PASS')
	num_threads = int(getenv('NUM_THREADS'))
	max_prs = int(getenv('MAX_PRS'))

	if(username is None):
		print('GITHUB_USERNAME environment variable not set. Set it to increase Github API request limit', file=stderr)
		exit(0)
	if(password is None):
		print('GITHUB_PASS environment variable not set. Set it to increase Github API request limit', file=stderr)
		exit(0)

	return repo_owner, repo_name, username, password, num_threads, max_prs

def main():
	repo_owner, repo_name, username, password, num_threads, max_prs = validate_configs()
	
	# Start script
	RepositoryAnalysis(repo_owner, repo_name, num_threads, max_prs, (username, password)).run_analysis()

if __name__ == '__main__':
	main()
