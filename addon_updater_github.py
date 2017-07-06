class GithubEngine(object):

	def __init__(self):
		self.api_url = 'https://api.github.com'

	def form_repo_url(self, updater):
		return self.api_url+"/repos/"+updater.user+"/"+updater.repo

	def form_tags_url(self, updater):
		return self.form_repo_url(updater) + "/tags"

	def form_branch_url(self, branch, updater):
		return self.form_repo_url(updater)+"/zipball/"+branch
		
	def parse_tags(self, resp, updater):
		return resp

Engine = GithubEngine()