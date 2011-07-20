# encoding: UTF-8
require "rubygems"
require "bundler"

Bundler.require

require "yui/compressor"

js_compressor = YUI::JavaScriptCompressor.new

# Compile master.scss
# Write output to public/css
Dir.chdir("sass") do
  %w(all desktop handheld oldie).peach do |device|
    css = Sass.compile_file("#{device}.scss", :style => :compressed)
    File.open("../public/css/#{device}.css", "w"){|buffer| buffer << css }
  end
end

# Combine javascripts to application.js
Dir.chdir("javascript") do
  application = "../public/javascript/application.js"

  Dir["**/*.js"].each do |javascript_filepath|
    uncompressed = File.open(javascript_filepath, "r").read + "\n"
    File.open(application, "a"){|buffer| buffer << uncompressed }
  end
end
