#!/usr/bin/env python3

import argparse
import os
import requests
import shutil

from modules.auth import USER_AGENT, log_in
from modules.clone import clone
from modules.validation import validate_url

OUTPUT_DIR = "_site/"
FORCE_OVERWRITE = True

def main():

	# Argument parser.
	parser = argparse.ArgumentParser(
		prog="ctfx-archivist.py",
		description="Archive tool for CTFx that generates a GitHub pages compatible static site.",
		epilog="Created by the team at IrisSec. irissec.xyz"
	)
	parser.add_argument("target", help="Domain of the CTFx instance to be archived.")
	parser.add_argument("username", help="Dummy account username.")
	parser.add_argument("password", help="Dummy account password.")
	args = parser.parse_args()

	args.target = validate_url(args.target)

	if os.path.exists(OUTPUT_DIR):
		if FORCE_OVERWRITE:
			shutil.rmtree(OUTPUT_DIR)
		elif input(f"A built {OUTPUT_DIR} exists. Overwrite? [y/N] ").lower() != "y":
			print("Quitting.")
			return -1
		else:
			print(f"{OUTPUT_DIR} will be overwritten.")
			shutil.rmtree(OUTPUT_DIR)

	os.mkdir(OUTPUT_DIR)

	print(":: Beginning archive operations.")
	print(":: Attempting to log in as the dummy user.")

	with requests.Session() as s:
		if not log_in(s, args.target, args.username, args.password):
			print("Login failed.")
			return -1
		else:
			print(":: Successful login.")

		# Begin to iteratively clone every page.
		alerts = clone(s, args.target, OUTPUT_DIR)
		for alert in alerts:
			print(":: Alert:", alert)

	print(":: Creating index page that redirects to home.html.")
	with open(OUTPUT_DIR+"index.html") as f1:
		with open("redirect.html") as f2:
			f1.write(f2.read())

	print(f":: All operations complete. Site saved to {OUTPUT_DIR}")

if __name__ == "__main__":
	main()
