# Authentication definitions.

import bs4
import requests

USER_AGENT = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}

def log_in(session, target: str, username: str, password: str) -> bool:
	"""
	Log into the target and return True if successful.
	"""

	# Get the login page.
	res = session.get(target+"/login", headers=USER_AGENT)
	if res.status_code != 200:
		return False

	# Get the XSRF token from the login page.
	soup = bs4.BeautifulSoup(res.text, "html.parser")
	xsrf = soup.find("input", attrs={"name": "xsrf_token"})["value"]

	# Attempt a login by POSTing to /api.
	res = session.post(target+"/api", data={
		"action": "login",
		"email": username,
		"password": password,
		"xsrf_token": xsrf
	})
	if res.status_code != 200:
		return False

	return True

