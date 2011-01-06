# developers.whatwg.org

This repository contains scripts that will generate a pristine copy of [developers.whatwg.org](developers.whatwg.org). It uses a collection of arcane python scripts supplied by the W3C, and my own Ruby scripts that remove cruft. 

To build your own copy, checkout this repostory, you'll need:

* Ruby (any version)
  * rvm
  * bundler
  * nokogiri
* Python (2.4+)
  * lxml (`easy_install lxml`)
  * html5lib (`easy_install html5lib`)
* Mercurial
* SVN
* LibXML2

I didn't say it was pretty! – But it does indeed work.

Run `make clean` then `make` to produce the required contents (final output is written to the `output` directory)
The contents of `output` are exactly what I have deployed to developers.whatwg.org.

If you're hoping to contribute to spec content, you'll need to talk to [Hixie](twitter.com/Hixie), as for styling and display of this content, I'm your man… and this is the repo.