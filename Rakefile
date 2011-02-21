# encoding: UTF-8
require "rubygems"
require "bundler"

Bundler.require

ROOT=File.expand_path(File.dirname(__FILE__))
@@docs = Hash.new {|h,k| h[k] = Nokogiri::HTML(File.open(k), "r")}

namespace :postprocess do
  task :execute => [:add_main_section, :add_wrapper, :insert_head, :references, :footer, :analytics, :search_index, :insert_search, :insert_javascripts, :insert_syncing, :insert_manifest, :add_next_up_links, :insert_whatwg_logo, :remove_comments, :remove_dom_interface, :toc, :transform_index, :write_docs]

  task :write_docs do
    @@docs.each do |path, doc|
      File.open(path, "w") {|file| file << doc.to_html }
    end
  end

  def each_page(&block)
    Dir[File.join(ROOT, 'public', "*.html")].each do |path|
      yield @@docs[path], path
    end
  end

	def insert(markup_path, selector, method = :add_child)
		markup = File.open(markup_path, "r").read

		each_page do |doc, filename|
		  doc.at(selector).send(method, Nokogiri::HTML::fragment(markup))
	  end
	end

	task :add_wrapper do
	  each_page do |doc, filename|
      doc.at("body").children = Nokogiri::HTML::fragment("<div class='wrapper'>#{doc.at("body").to_html}</div>")
	  end
  end

	# This will seem strange, we'll get the header, keep its contents, remove it from the DOM
  # Then, we'll get everything within the body, wrap it within a <section role="main">
  # Finally, we'll add back the header above the newly created <section>
	task :add_main_section do
	  each_page do |doc, filename|
	    header = doc.at("header")
      header.remove

      doc.at("body").children = Nokogiri::HTML::fragment("<section role='main'>#{doc.at("body").to_html}</section>")
      doc.at("section[role='main']").before(Nokogiri::HTML::fragment(header.to_html))
	  end
  end

  desc "Does some special transformations on the index.html file"
  task :transform_index do
      doc = @@docs[File.join(ROOT, 'public', 'index.html')]
      doc.at("section[role='main']").children.first.before(File.open("html/credits.html", "r").read)

      # Remove hashes from links
      doc.css("ol.toc a").each do |link|
        link.attributes["href"].value = link.attributes["href"].to_s.gsub(/#(.*)+$/, "")
      end
  end

  desc "Add document footer"
  task :footer do
		insert("html/footer.html", "body .wrapper")
  end

  desc "Add analytics"
  task :analytics do
		insert("html/analytics.html", "body")
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
					wrapper = reference_link.parent.replace(Nokogiri::HTML::fragment("<div class='reference-wrapper'>#{reference_link.parent.to_s}</div>"))[0]
					wrapper.add_child('<aside id="'+ reference_string +'" class="reference">'+ aside_content +'</aside>')
        end
      end
    end
  end

  desc "Add a search index json file"
  task :search_index do
    fork do
      toc = Nokogiri::HTML(File.open("public/index.html", "r"))
      index = toc.css("ol.toc li a").inject([]) do |index, link|
        section = link.css("span")
        section_text = section.text.strip
        section.remove

        parent_section = link.parent.parent.parent

        if parent_section.node_name == "li"
          section_text = "#{section_text} — #{parent_section.at("a").text}"
        end

        index << {
          :uri => link.attributes["href"],
          :text => link.text.strip,
          :section => section_text
        }
      end

      File.open("public/search_index.json", "w") {|buffer| buffer << JSON.generate(index)}
    end
  end

  desc "Add search to each html file"
  task :insert_search do
    insert("html/search.html", "header.head")
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

  desc "Add manifest reference"
  task :insert_manifest => "generate:manifest" do
    each_page {|doc, filename| doc.at("html")['manifest'] = "/offline.manifest"}
  end

  desc "Insert syncing notification"
  task :insert_syncing do
    insert("html/syncing.html", "body")
  end

	task :insert_head do
	  head = File.open("html/head.html", "r").read
	  each_page {|doc, filename| doc.css("head").children.first.before(head) }
	end

  desc "Add 'next up' page links"
  task :add_next_up_links do
    each_page do |doc, filename|
			next_page = doc.at("link[rel='next']") || doc.at("nav a:nth-child(3)")

			unless next_page
				puts "No 'next' link found for #{filename}"
				next
			end

			title = next_page.attributes["title"].to_s.gsub("→", "")
			href = next_page.attributes["href"]
			doc.at("footer").before('<div id="up-next"><a href="'+href+'"><p>Up next</p><h1>'+title+'</h1></a></div>')
		end
  end

  desc "Insert WHATWG logo"
  task :insert_whatwg_logo do
    each_page do |doc, filename|
      doc.at("header.head hgroup").before('<div class="logo">WHATWG</div>')
    end
  end

  task :remove_comments do
    Dir.chdir("public") do
      Dir["*.html"].each do |page|
        without_comments = File.open(page, "r").read.gsub(/<!--(.*)-->/, "")
        File.open(page, "w") {|buffer| buffer << without_comments }
      end
    end
  end

  task :remove_dom_interface do
    each_page do |doc, filename|
      dt = doc.xpath('//dt[text()="DOM interface:"]')
      dt.xpath('following-sibling::dd[1]').remove
      dt.remove
    end
  end

  task :toc do
    each_page do |doc, filename|
      if nav = doc.at("section[role='main'] nav")
        nav.children.first.before("<button id='toc-toggle'>In this section</button>")
        doc.css("section[role='main'] nav > a").remove
        nav.replace(Nokogiri::HTML::fragment(nav.to_s.gsub("&ndash;", "")))
      end
    end
  end
end

namespace :generate do

  desc "Generate a HTML5 manifest for offline specifications"
  task :manifest do
    files = Dir["public/**/*.*"].map{|fp| fp.gsub("public/", "") }.join("\n")

    MANIFEST = %Q{CACHE MANIFEST
# #{Time.now.to_s}
#{ files }

NETWORK:
http://www.google-analytics.com/ga.js
http://images.whatwg.org

    }

    File.open("public/offline.manifest", "w") { |buffer| buffer << MANIFEST }
  end
end
