HG=hg
SVN=svn
CURL=curl
PYTHON=python
RUBY=ruby
PATCH=patch
SPLITTER=html5-tools/spec-splitter/spec-splitter.py
SPLITTERFLAGS=--html5lib-serialiser

postprocess: clean-output process_assets LOG
	bundle exec rake postprocess:execute

LOG: index.html $(SPLITTER)
	$(PYTHON) $(SPLITTER) $(SPLITTERFLAGS) $< ./public > LOG

index.html: html5-full.html anolis/anolis
	$(PYTHON) anolis/anolis \
	  --parser=lxml.html \
	  --filter=.impl \
	  --output-encoding="ascii" \
	  --allow-duplicate-dfns \
	  $< $@

html5-full.html:
	$(CURL) --compressed https://html.spec.whatwg.org > $@
	$(RUBY) tidy.rb $@

process_assets:
	$(RUBY) assets.rb

clean: clean-output
	$(RM) html5-full.html

clean-output:
	$(RM) LOG
	$(RM) -r public/**/*.html
	$(RM) -r public/css/*.css
	$(RM) -r public/javascript/*.js
	$(RM) -r public/*.manifest

anolis/anolis:
	$(HG) clone http://hg.hoppipolla.co.uk/anolis/
	$(PATCH) -p1 -d anolis < patch.anolis

$(SPLITTER):
	$(SVN) checkout http://html5.googlecode.com/svn/trunk/ html5-tools
