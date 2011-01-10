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

Run `make clean` then `make` to produce the required contents (final output is written to the `public` directory)
The contents of `public` are exactly what I have deployed to developers.whatwg.org.

If you're hoping to contribute to spec content, you'll need to talk to [Hixie](http://twitter.com/Hixie), as for styling and display of this content, I'm your man… and this is the repo.

## Want to get involved? 

Fork this project on Github, use detailed commit messages and ensure that you provide enough detail in your pull request that I can understand what you're doing and why. 