# encoding: UTF-8
require "rubygems"
require "bundler"

Bundler.require

doc = Nokogiri::HTML(File.open(ARGV[0], "r"))

# Remove all scripts and styles included
doc.css("link[rel='stylesheet'], style, link[href^='data:text/css']").remove
doc.css("script").remove

# Wrap the header group in an a referencing "/"
doc.at("header.head hgroup h1").replace("<h1><a href='/' rel='home'>HTML5</a></h1>")

# Write everything back into the file it came from
File.open(ARGV[0], "w") do |file|
  file << doc.to_html
end
