HG=hg
SVN=svn
CURL=curl
PYTHON=python
RUBY=ruby
PATCH=patch
SPLITTER=html5-tools/spec-splitter/spec-splitter.py
SPLITTERFLAGS=--html5lib-serialiser

postprocess: LOG
	rake postprocess:execute

LOG: index.html $(SPLITTER)
	$(PYTHON) $(SPLITTER) $(SPLITTERFLAGS) $< ./public > LOG

index.html: html5-full.html anolis/anolis
	$(RUBY) tidy.rb $<
	$(PYTHON) anolis/anolis \
	  --parser=lxml.html \
	  --filter=.impl \
	  --output-encoding="ascii" \
	  $< $@

html5-full.html:
	$(CURL) --compressed http://www.whatwg.org/specs/web-apps/current-work/dev-index > $@

clean:
	$(RM) -r public/**/*.html
	$(RM) LOG
	$(RM) html5-full.html

anolis/anolis:
	$(HG) clone http://hg.hoppipolla.co.uk/anolis/
	$(PATCH) -p1 -d anolis < patch.anolis

$(SPLITTER):
	$(SVN) checkout http://html5.googlecode.com/svn/trunk/ html5-tools
