#!/bin/bash
set -e -u
cd "$(dirname "$0")"
rsync -av web_scripts/ /mit/javsolis/web_scripts/
#chmod 0777 /mit/hwops/web_scripts/robots.txt
#rsync -av manuals/ /mit/hwops/web_scripts/manuals/
