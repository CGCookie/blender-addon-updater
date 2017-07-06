class BitbucketEngine(object):

	def __init__(self):
		self.api_url = 'https://api.bitbucket.org'

	def form_repo_url(self, updater):
		return self.api_url+"/2.0/repositories/"+updater.user+"/"+updater.repo

	def form_tags_url(self, updater):
		return self.form_repo_url(updater) + "/refs/tags?sort=-name"

	def form_branch_url(self, branch, updater):
		return self.get_zip_url(branch, updater)

	def get_zip_url(self, name, updater):
		return "https://bitbucket.org/{user}/{repo}/get/{name}.zip".format(
			user = updater.user,
			repo = updater.repo,
			name = name)

	def parse_tags(self, resp, updater):
		return [{"name": tag["name"], "zipball_url": self.get_zip_url(tag["name"], updater)} for tag in resp["values"]]

Engine = BitbucketEngine()