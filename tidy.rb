require "rubygems"
require "bundler"
require "nokogiri"

Bundler.require

def process_doc(doc)
  # Remove all scripts and styles included
  doc.css("link[rel='stylesheet'], style, link[href^='data:text/css']").remove
  doc.css("script").remove

  # Wrap the header group in an a referencing "/"
  toc = doc.at("h2#table-of-contents")
  if toc
    toc.add_previous_sibling("<h1><a href='/' rel='home'>HTML: The Living Standard</a></h1>")
  end
end

# Write everything back into the file it came from
Dir.glob("#{ARGV[0]}/*.html").each do |filename|
  file_contents = File.open(filename).read
  doc = Nokogiri::HTML(file_contents)

  if doc
    File.open(filename, "w") do |file|
      puts doc.to_html
      process_doc(doc)
      file << doc.to_html
    end
  end
end
