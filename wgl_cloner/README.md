Rather than changing the main script, I just copied it and modded it to clone
only the WebGL version. After running `./ctfx-archivist.py`, run `./patch.sh`.
`./patch.sh` assumes that you've already run the parent script and haven't
changed the directory structure. It will merge the output of this script into
the main `../_site` after applying some patches.
