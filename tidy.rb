require "rubygems"
require "bundler/setup"

require "nokogiri"
require "sass"
require "yui/compressor"
require "fileutils"

doc = Nokogiri::HTML(File.open(ARGV[0], "r"))
js_compressor = YUI::JavaScriptCompressor.new

# Remove all scripts and styles included
doc.css("link[rel='stylesheet'], style, link[href^='data:text/css']").remove
doc.css("script").remove

# Compile master.scss
# Write output to public/css
Dir.chdir("sass") do
  css = Sass.compile_file("master.scss", :style => :compressed)
  File.open("../public/css/master.css", "w"){|buffer| buffer << css }
end

# Compress * javascripts to application.js
Dir.chdir("javascript") do
  application = "../public/javascript/application.js"
  
  FileUtils.touch(application)
  FileUtils.rm(application) 
  
  Dir["**/*.js"].each do |javascript_filepath|
    compressed = js_compressor.compress(File.open(javascript_filepath, "r")) + "\n"
    File.open(application, "a"){|buffer| buffer << compressed }
  end
end

# Wrap the header group in an a referencing "/"
doc.at("header.head hgroup h1").replace("<h1><a href='/' rel='home'>HTML5</a></h1>")

# Write everything back into the file it came from
File.open(ARGV[0], "w") do |file|
  file << doc.to_html
end
