# encoding: UTF-8
require "rubygems"
require "bundler"

Bundler.require

require "yui/compressor"

js_compressor = YUI::JavaScriptCompressor.new

# Compile master.scss
# Write output to public/css
Dir.chdir("sass") do
  %w(all desktop handheld).peach do |device|
    css = Sass.compile_file("#{device}.scss", :style => :compressed)
    File.open("../public/css/#{device}.css", "w"){|buffer| buffer << css }
  end
end

# Compress * javascripts to application.js
Dir.chdir("javascript") do
  application = "../public/javascript/application.js"

  Dir["**/*.js"].peach do |javascript_filepath|
    compressed = js_compressor.compress(File.open(javascript_filepath, "r")) + "\n"
    File.open(application, "a"){|buffer| buffer << compressed }
  end
end
