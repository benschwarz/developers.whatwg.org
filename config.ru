#\ -p 8095
require "rubygems"
require "bundler"

Bundler.require

# Route directory URI's to index file.
class DirectoryIndex
  def initialize(app, index='index.html')
    @app   = app
    @index = [index].flatten
  end
  def call(env)
    if env['PATH_INFO'] =~ /\/$/
      if index = find_index(env)
        env['PATH_INFO'] += index
      end
    end
    @app.call(env)
  end
  def find_index(env)
    @index.find do |i|
      ::File.exist?(::File.join(Dir.pwd, env['PATH_INFO'], i))
    end
  end
end

use DirectoryIndex
run Rack::Directory.new('public')
