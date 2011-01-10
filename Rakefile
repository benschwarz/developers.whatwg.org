require "rubygems"
require "bundler/setup"

require "nokogiri"


namespace :postprocess do
  desc "Add credits information"
  task :credits do
    Dir.chdir("public") do
      doc = Nokogiri::HTML(File.open("index.html", "r"))
      doc.css("body")[0].children[0].before(File.open("../html/credits.html", "r").read)
      
      File.open("index.html", "w") {|file| file << doc.to_html }
      puts "Wrote credits into index.html"
    end
  end
  
  desc "Pull references inline"
  task :references do
    Dir.chdir("public") do
      reference_doc = Nokogiri::HTML(File.open("references.html", "r"))

      Dir["*.html"].each do |html|
        doc = Nokogiri::HTML(File.open(html, "r"))

        # Find reference links
        doc.css("a[href*='#refs']").each do |reference_link|
          reference_string = reference_link.attributes["href"].value.gsub(/^(.*)\#/, "")
          aside_content = reference_doc.css("dt#" + reference_string + " + dd").inner_html

          # Create aside element above the parent of the link
          unless doc.css("aside#" + reference_string).any?
            reference_link.parent.add_child('<aside id="'+ reference_string +'" class="reference">'+ aside_content +'</aside>')
            puts "Added reference for #{reference_string} to #{html}"
          end
        end

        # Write the changes to the document
        File.open(html, "w") {|file| file << doc.to_html }
      end
    end
  end
end