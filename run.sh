#!/usr/bin/env bash

set -e

if [[ $LOGNAME != "www-data" ]]; then
        echo "Run as www-data, not $LOGNAME"
fi

cd /home/dave/web-to-rss/

source .venv/bin/activate

python screenshot.sh
