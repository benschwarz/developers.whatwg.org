require "rubygems"
require "bundler/setup"

require "nokogiri"

doc = Nokogiri::HTML(File.open(ARGV[0], "r"))

# Remove all scripts and styles included
doc.css("link[rel='stylesheet'], style, link[href^='data:text/css']").remove
doc.css("script").remove

File.open(ARGV[0], "w") do |file|
  file << doc.to_html
end