require "rubygems"
require "bundler/setup"

require "nokogiri"
require "peach"
require "json"

namespace :postprocess do
  task :execute => [:credits, :references, :footer, :analytics, :search_index, :insert_search, :insert_stylesheets, :insert_javascripts, :insert_manifest, :insert_syncing, :insert_charset]

  def each_page(&block)
    Dir.chdir("public") do
      Dir["*.html"].peach do |html|
        doc = Nokogiri::HTML(File.open(html, "r"))
        yield doc, html
        File.open(html, "w") {|file| file << doc.to_html }
      end
    end
  end

  desc "Add credits information"
  task :credits do
    Dir.chdir("public") do
      doc = Nokogiri::HTML(File.open("index.html", "r"))
      doc.at("header.head").after(File.open("../html/credits.html", "r").read)
      
      File.open("index.html", "w") {|file| file << doc.to_html }
    end
  end

  desc "Add document footer"
  task :footer do
    footer = File.open("html/footer.html", "r").read
    
    each_page do |doc, filename|
      doc.css("body")[0].add_child(footer)
    end
  end
  
  desc "Add analytics"
  task :analytics do
    analytics = File.open("html/analytics.html", "r").read
    
    each_page do |doc, filename|
      doc.css("body")[0].add_child(analytics)
    end
  end
  
  desc "Pull references inline"
  task :references do
    reference_doc = Nokogiri::HTML(File.open("public/references.html", "r"))
    
    each_page do |doc, filename|
      doc.css("a[href*='#refs']").each do |reference_link|
        reference_string = reference_link.attributes["href"].value.gsub(/^(.*)\#/, "")
        aside_content = reference_doc.css("dt#" + reference_string + " + dd").inner_html

        # Create aside element above the parent of the link
        unless doc.css("aside#" + reference_string).any?
          reference_link.parent.add_child('<aside id="'+ reference_string +'" class="reference">'+ aside_content +'</aside>')
        end
      end
    end
  end

  desc "Add a search index json file"
  task :search_index do
    toc = Nokogiri::HTML(File.open("public/index.html", "r"))
    index = toc.css("ol.toc li a").inject([]) do |index, link| 
      section = link.css("span")
      section_text = section.text.strip
      section.remove
      index << {
        :uri => link.attributes["href"],
        :text => link.text.strip,
        :section => section_text
      }
    end

    File.open("public/search_index.json", "w") {|buffer| buffer << JSON.generate(index)}
  end

  desc "Add search to each html file"
  task :insert_search do
    search = File.open("html/search.html", "r").read
    each_page do |doc, filename|
			doc.at("header.head").add_child(search)
    end
  end

  desc "Insert javascripts"
  task :insert_javascripts do
    Dir["public/**/*.js"].each do |js_path|
      js_path = js_path.gsub("public/", "")
      each_page do |doc, filename|
        doc.at("body").add_child('<script src="/' + js_path + '" defer>')
      end
    end
  end

  desc "Insert stylesheets"
  task :insert_stylesheets do
    Dir["public/**/*.css"].each do |css_path|
      css_path = css_path.gsub("public/", "")
      each_page do |doc, filename|
        doc.at("head").add_child('<link rel="stylesheet" href="/' + css_path + '">')
      end
    end
  end

  desc "Add manifest reference"
  task :insert_manifest => "generate:manifest" do
    each_page {|doc, filename| doc.at("html")['manifest'] = "/offline.manifest"}
  end
  
  desc "Insert syncing notification"
  task :insert_syncing do
    syncing = File.open("html/syncing.html", "r").read
    
    each_page do |doc, filename|
      doc.at("body").add_child(syncing)
    end
  end

  desc "Set character encoding"
  task :insert_charset do
    each_page {|doc, filename| doc.at("head").children.first.before('<meta charset="utf-8">') }
  end
end

namespace :generate do

  desc "Generate a HTML5 manifest for offline specifications"
  task :manifest do
    files = Dir["public/**/*.*"].map{|fp| fp.gsub("public/", "") }.join("\n")

    MANIFEST = %Q{CACHE MANIFEST
# #{Time.now.to_s}

#{ files }
    }

    File.open("public/offline.manifest", "w") { |buffer| buffer << MANIFEST }
  end
end
