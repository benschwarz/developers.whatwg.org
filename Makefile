HG=hg
SVN=svn
CURL=curl
PYTHON=python
PATCH=patch
SPLITTER=html5-tools/spec-splitter/spec-splitter.py
SPLITTERFLAGS=--w3c --html5lib-serialiser

LOG: spec.html
	$(PYTHON) $(SPLITTER) $(SPLITTERFLAGS) $< > LOG

spec.html: complete.html
	$(PYTHON) anolis/anolis \
	  --parser=lxml.html \
	  --filter=.impl \
	  --output-encoding="ascii" \
	  $< $@

complete.html:
	$(CURL) http://www.whatwg.org/specs/web-apps/current-work/complete.html > $@

clean:
	$(RM) LOG
	$(RM) spec.html

anolis/anolis:
	$(HG) clone http://hg.hoppipolla.co.uk/anolis/
	$(PATCH) -p1 -d anolis < patch.anolis

$(SPLITTER):
	$(SVN) checkout http://html5.googlecode.com/svn/trunk/ html5-tools