#! /bin/sh
echo "Deploying…"
rsync -ave ssh ./public/ benschwarz@developers.whatwg.org:developers.whatwg.org