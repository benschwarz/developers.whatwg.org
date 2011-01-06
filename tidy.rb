require "rubygems"
require "bundler/setup"

require "nokogiri"
require "sass"
require "yui/compressor"

doc = Nokogiri::HTML(File.open(ARGV[0], "r"))
js_compressor = YUI::JavaScriptCompressor.new

# Remove all scripts and styles included
doc.css("link[rel='stylesheet'], style, link[href^='data:text/css']").remove
doc.css("script").remove

# Compile master.scss
# Write output to public/css
Dir.chdir("sass") do
  css = Sass.compile_file("master.scss", :style => :compressed)
  File.open("../public/css/master.css", "w+"){|buffer| buffer << css }
end

# Include my scripts and styles
Dir.chdir("public") do
  Dir["**/*.css"].each do |stylesheet_filepath|
    doc.css("head")[0].add_child('<link rel="stylesheet" href="/' + stylesheet_filepath + '">')
    puts "Included stylesheet #{stylesheet_filepath}"
  end
end

# Write everything back into the file it came from
File.open(ARGV[0], "w") do |file|
  file << doc.to_html
end