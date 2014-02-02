# developers.whatwg.org

This repository contains scripts that will generate a pristine copy of [developers.whatwg.org](developers.whatwg.org). It uses a collection of arcane python scripts supplied by the W3C, and my own Ruby scripts that remove cruft.

To build your own copy, checkout this repostory, you'll need:

* Ruby (any version)
* Python (2.4+)
* Subversion
* LibXML2

To install dependencies: 

```bash
bundle install
pip install -r requirements.txt
```

Run `make clean` then `make` to produce the required contents (final output is written to the `public` directory)
The contents of `public` are exactly what I have deployed to developers.whatwg.org.

If you're hoping to contribute to spec content, you'll need to talk to [Hixie](http://twitter.com/Hixie), as for styling and display of this content, I'm your man… and this is the repo.

## Want to get involved?

Fork this project on Github, use detailed commit messages and ensure that you provide enough detail in your pull request that I can understand what you're doing and why.


# Licence
<p xmlns:dct="http://purl.org/dc/terms/" xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
  <a rel="license"
     href="http://creativecommons.org/publicdomain/zero/1.0/">
    <img src="http://i.creativecommons.org/p/zero/1.0/88x31.png" style="border-style: none;" alt="CC0" />
  </a>
  <br />
  To the extent possible under law,
  <a rel="dct:publisher"
     href="http://www.germanforblack.com">
    <span property="dct:title">Ben Schwarz</span></a>
  has waived all copyright and related or neighboring rights to
  <span property="dct:title">Design of developer specification</span>.
This work is published from:
<span property="vcard:Country" datatype="dct:ISO3166"
      content="AU" about="http://www.germanforblack.com">
  Australia</span>.
</p>
