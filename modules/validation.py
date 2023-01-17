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

def validate_filename(name: str, isHTML: bool=False, removeLeadingSlash: bool=True):
	"""
	Standardize a filename to replace all "?" and "=" with "-". If it is of type
	html, then end with ".html". Remove the leading slash if there is one. So
	something like "/user?id=559" will turn into "user-id-559.html". Also, if
	it ended in ".css?v=xxx" or ".js?v=xxx" originally, re-append the extension.
	"""

	if ".css?v=" in name:
		name += ".css"
	elif ".js?v=" in name:
		name += ".js"

	if removeLeadingSlash and name.startswith("/"):
		name = name[1:]
	if isHTML and not name.endswith(".html"):
		name += ".html"

	return name.replace("?", "-").replace("=", "-")

