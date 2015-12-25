HG=hg
SVN=svn
CURL=curl
PYTHON=python
RUBY=ruby
PATCH=patch

postprocess: clean-output process_assets tidy
	bundle exec rake postprocess:execute

multipage-dev.zip:
	$(CURL) --compressed https://html5.org/temp/multipage-dev.zip > $@

multipage-dev: multipage-dev.zip
	unzip -o multipage-dev.zip

tidy: multipage-dev
	$(RUBY) tidy.rb multipage-dev/index.html
	cp -r multipage-dev/*.html public

process_assets:
	$(RUBY) assets.rb

clean: clean-output
	$(RM) -r multipage-dev
	$(RM) multipage-dev.zip

clean-output:
	$(RM) -r public/**/*.html
	$(RM) -r public/css/*.css
	$(RM) -r public/javascript/*.js
	$(RM) -r public/*.manifest
