# Cloning functions.

import bs4
import os
import requests

USER_AGENT = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}

def make_parent_dirs(target: str):
	"""
	Make the parent directories for a file.
	"""

	dirs = target.split("/")[:-1]

	# No parent directories needed. Root-level.
	if len(dirs) == 1:
		return

	os.makedirs("/".join(dirs), exist_ok=True)

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
		if a.has_key("href") and len(a["href"]) > 1 and a["href"].startswith("/"):
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

		res = session.get(target+item, headers=USER_AGENT)

		if res.status_code != 200:
			alerts.append(f"GET {target+item} returned {res.status_code}.")
			continue

		print(f":: Archiving {target+item}")
		make_parent_dirs(outputDir[:-1] + item)

		# HTML special case: scrape for more links.
		if "text/html" in res.headers["Content-Type"]:
			links = scrape_for_links_html(res.text)

		# If any links were scraped, add them to the todo list if they're not
		# already completed or if they're not already in the todo list.
		for link in links:
			if link not in completed and link not in todo:
				todo.append(link)

		# Save the resource.
		filename = item
		if item.startswith("/"):
			filename = filename[1:]
		with open(outputDir+filename, "wb") as f:
			f.write(res.content)

		# Move this item from todo to completed.
		completed.append(item)
		del todo[0]

	return alerts

