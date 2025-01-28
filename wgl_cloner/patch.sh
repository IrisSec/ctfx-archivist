#!/bin/bash

echo ":: Removing unnecessary UI."
# -R because oops lol
patch -R -u ./_site/static/bg/f.min.js < ./remove_ui.patch

echo ":: Fixing redirect."
patch -u ./_site/static/bg/f.min.js < ./fix_redirect.patch

echo ":: Hardcoding API responses."
cat wgl_api_schema.js >> ./_site/static/bg/f.min.js

echo ":: Merging into ../_site/."
rsync -a _site/ ../_site/

echo ":: Done."
