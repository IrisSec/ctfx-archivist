# Input validation and standardization.

def validate_url(url: str):
	"""
	Standardize a URL to https://some.domain. No trailing slash.
	"""

	if not (url.startswith("https://") or url.startswith("http://")):
		url = "https://" + url

	if url.endswith("/"):
		url = url[:-1]

	return url
