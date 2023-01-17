#!/usr/bin/env python3

import argparse
import os
import requests
import shutil

from modules.auth import USER_AGENT, log_in
from modules.validation import validate_url

OUTPUT_DIR = "_build/"
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

		# Test login success.
		print(s.get(args.target+"/profile", headers=USER_AGENT).text)

if __name__ == "__main__":
	main()
