# Cloning functions.

import bs4
import os
import requests

from modules.validation import validate_filename

USER_AGENT = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}
EXCLUDE = ["/profile", "/logout", "/login", "/user.php"]

def make_parent_dirs(target: str):
	"""
	Make the parent directories for a file.
	"""

	dirs = target.split("/")[:-1]

	# No parent directories needed. Root-level.
	if len(dirs) == 1:
		return

	os.makedirs("/".join(dirs), exist_ok=True)

def postprocess_html(html) -> str:
	"""
	Postprocess some HTML so that all links abide by the rules in validate_filename.
	Also, remove all references to profile and logout.
	"""

	soup = bs4.BeautifulSoup(html, "html.parser")

	# Remove "Profile"
	try:
		soup.find("a", attrs={"href": "/profile"}).clear()
	except:
		pass

	# Remove "Logout"
	try:
		soup.find("form", attrs={"action": "/api"}).clear()
	except:
		pass

	# meta image content
	for meta in soup.find_all("meta"):
		if meta.has_key("property") and "image" in meta["property"]:
			meta["content"] = validate_filename(meta["content"], removeLeadingSlash=False)

	# link icon/css href
	for link in soup.find_all("link"):
		if link.has_key("rel") and ("icon" in link["rel"] or "stylesheet" in link["rel"]):
			link["href"] = validate_filename(link["href"], removeLeadingSlash=False)

	# script src
	for script in soup.find_all("script"):
		if script.has_key("src"):
			script["src"] = validate_filename(script["src"], removeLeadingSlash=False)

	# a href
	for a in soup.find_all("a"):
		if a.has_key("href") and len(a["href"]) > 1 and not a["href"].startswith("http"):
			if "user.php" in a["href"]:
				a["href"] = a["href"].replace(".php", "")
			a["href"] = validate_filename(a["href"], isHTML=True, removeLeadingSlash=False)

	# img src
	for img in soup.find_all("img"):
		if img.has_key("src") and img["src"].startswith("/"):
			# Special exception is applied for flags. CTFx uses relative paths
			# for them sometimes.
			img["src"] = validate_filename(img["src"].replace("/static/img/icons/../", "/static/img/"), removeLeadingSlash=False)

	# audio src
	for audio in soup.find_all("audio"):
		if audio.has_key("src"):
			audio["src"] = validate_filename(audio["src"], removeLeadingSlash=False)

	return soup.prettify("utf-8")

def scrape_for_links_html(html) -> list:
	"""
	Scrape for links in some HTML. Only return non-external links.
	"""

	links = []
	soup = bs4.BeautifulSoup(html, "html.parser")

	# meta image content
	for meta in soup.find_all("meta"):
		if meta.has_key("property") and "image" in meta["property"]:
			links.append(meta["content"])

	# link icon/css href
	for link in soup.find_all("link"):
		if link.has_key("rel") and ("icon" in link["rel"] or "stylesheet" in link["rel"]):
			links.append(link["href"])

	# script src
	for script in soup.find_all("script"):
		if script.has_key("src"):
			links.append(script["src"])

	# a href
	for a in soup.find_all("a"):
		if a.has_key("href") and len(a["href"]) > 1 and not a["href"].startswith("http"):
			if not a["href"].startswith("/"):
				links.append("/"+a["href"])
			else:
				links.append(a["href"])

	# img src
	for img in soup.find_all("img"):
		if img.has_key("src") and img["src"].startswith("/"):
			# Special exception is applied for flags. CTFx uses relative paths
			# for them sometimes.
			src = img["src"].replace("/static/img/icons/../", "/static/img/")
			links.append(src)

	# audio src
	for audio in soup.find_all("audio"):
		if audio.has_key("src"):
			links.append(audio["src"])

	# div style background-image url
	for div in soup.find_all("div"):
		if div.has_key("style") and "background-image" in div["style"]:
			links.append(div["style"].split("'")[1])

	return links

def clone(session, target: str, outputDir: str) -> list:
	"""
	Clone the target and write everything to outputDir. Return a list of error
	messages and alerts, if any.
	"""

	# Output alerts log.
	alerts = []

	# To-do and done buffers to prevent double-doing.
	todo = ["/home"]
	completed = []

	while len(todo) > 0:

		item = todo[0]

		# Other pages, images, JavaScript, CSS, etc. but only if they aren't
		# external. This is so we don't accidentally spider the Internet.
		links = []

		res = None
		failed = False

		for i in range(5):

			res = session.get(target+item, headers=USER_AGENT)

			if res.status_code == 200:
				break

			if i == 4:
				alerts.append(f"GET {target+item} returned {res.status_code} after 5 attempts.")
				failed = True
				break

		if failed:
			continue

		print(f":: Archiving {target+item}")
		make_parent_dirs(outputDir[:-1] + item)

		content = res.content

		# HTML special case: scrape for more links. Also, change URLs in the
		# content to be saved to abide by the rules in validate_filename.
		if "text/html" in res.headers["Content-Type"]:
			links = scrape_for_links_html(res.text)
			content = postprocess_html(content)

		# If any links were scraped, add them to the todo list if they're not
		# already completed or if they're not already in the todo list.
		for link in links:
			if link not in completed and link not in todo:
				skip = False
				for e in EXCLUDE:
					if e in link:
						skip = True
						break
				if skip:
					continue
				todo.append(link)

		# Save the resource.
		filename = validate_filename(item, "text/html" in res.headers["Content-Type"])
		with open(outputDir+filename, "wb") as f:
			f.write(content)

		# Move this item from todo to completed.
		completed.append(item)
		del todo[0]

	return alerts

