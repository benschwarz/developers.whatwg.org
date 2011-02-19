#! /bin/sh
echo "Deploying…"
rsync --delete -aze ssh ./public/ benschwarz@developers.whatwg.org:developers.whatwg.org