"""
    WebChomp -- A tool for generating static websites.
    Copyright (C) 2014 Nathan Ogden

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys, os, fnmatch, yaml, shutil, time
from scss import Scss
from jinja2 import Environment, FileSystemLoader
import dateutil.parser

""" Site Generator Class """
class webchomp_generator:

	""" Load specified site, exit out if site isn't found. """
	def __init__(self, site):

		# set site
		self.site = site

		# Store site path
		self.site_path = "site/%s" % site
		# Store other useful pathes
		self.site_page_path = "%s/page" % self.site_path
		self.site_template_path = "%s/template" % self.site_path
		self.site_asset_path = "%s/asset" % self.site_path

		# page info cache
		self.page_info = {}

		# list of already compiled scss, to prevert recompiling
		self.compiled_scss = []

		# verify site exists
		if not os.path.exists(self.site_path):
			print "ERROR: Specified site does not exist."
			return sys.exit()

		# Found, yay!
		print "Found site '%s'..." % (site)

		# create site output if not exist
		if not os.path.exists("output"):
			os.mkdir("output")
		if not os.path.exists("output/%s" % self.site):
			os.mkdir("output/%s" % self.site)
			os.mkdir("output/%s/asset" % self.site)
			os.mkdir("output/%s/asset/css" % self.site)

		# load site conf yml
		self.site_conf = {}
		if os.path.exists("%s/site.yml" % self.site_path):
			f_io = open("%s/site.yml" % self.site_path, "r")
			self.site_conf = yaml.load(f_io.read())
			f_io.close()

	""" Generate the loaded site. """
	def generate(self, page = None):

		# Copy assets directory
		print "Copying site assets...",
		if os.path.exists("output/%s/asset" % self.site):
			shutil.rmtree("output/%s/asset" % self.site)
		shutil.copytree(self.site_asset_path, "output/%s/asset" % self.site)
		
		# Recreate asset/css
		os.mkdir("output/%s/asset/css" % self.site)		

		print "Done"

		# Get pages in site
		print "Generating pages..."
		pages = self._get_site_pages()
		for page in pages:
			self.generate_page(page)

	""" *private* Get an array of all pages in the site. """
	def _get_site_pages(self, sub_path = ""):

		# find all page definition (yml) files
		matches = []

		for root, dirnames, filenames in os.walk("%s%s" % (self.site_page_path, sub_path)):
			for filename in fnmatch.filter(filenames, '*.yml'):
				matches.append( os.path.join(root, filename).replace(self.site_page_path, "").replace("\\", "/")[1:] )
		return matches

	""" *private* Load page components, store in page_info array """
	def _load_page(self, page_path):

		# make sure page_path exists
		if not os.path.exists("%s/%s" % (self.site_page_path, page_path)):
			return False

		# check if page was already loaded
		if page_path in self.page_info:
			return self.page_info[page_path]

		# open page, parse yaml
		page_file = open("%s/%s" % (self.site_page_path, page_path), "r")
		page_info = yaml.load(page_file.read())
		page_file.close()

		# store page info
		self.page_info[page_path] = page_info

		return page_info

	"""  Generate specified page. """
	def generate_page(self, page_path):

		print "Processing '%s'..." % page_path.replace(self.site_page_path, ""),

		# get page info
		page_info = self._load_page(page_path)
		if not page_info: 
			print "Failed (Page not found)."
			return False

		# find page template
		page_template = page_info['_template'] if '_template' in page_info else "default.html.jinja"

		# make sure page_template exists
		if not os.path.exists("%s/jinja/%s" % (self.site_template_path, page_template)):
			print "Failed (Page template does not exist)."
			return False

		# get page relative asset dir
		asset_relative_output_dir = "asset"
		for subpath in os.path.split(os.path.dirname(page_path)):
			if subpath: asset_relative_output_dir = "../%s" % asset_relative_output_dir

 		# load component :: Jinja function
		def load_component(component_name, page_path = "", type="text"):

			# load page from page_path
			if page_path:
				sub_page_info = self._load_page(page_path)
				if sub_page_info and component_name in sub_page_info: return sub_page_info[component_name]

			# no page_path use current page component
			elif component_name in page_info:
				return page_info[component_name]
			return "[component not found]"

		# check if component exists :: Jinja function
		def has_component(component_name, page_path = ""):

			# load page from page_path
			if page_path:
				sub_page_info = self._load_page(page_path)
				if component_name in sub_page_info: return True

			# no page_path use current page component
			elif component_name in page_info:
				return True

			return False

		# load scss :: Jinja function
		def load_scss(filename):

			# make sure we haven't already compiled
			if not filename in self.compiled_scss:

				# make sure scss file exists
				if not os.path.exists("%s/scss/%s" % (self.site_template_path, filename)): return ""

				# open file
				scss_fo = open("%s/scss/%s" % (self.site_template_path, filename), "r")
				scss = scss_fo.read()
				scss_fo.close()

				# load compiler
				scss_compiler = Scss(search_paths = [ os.path.dirname("%s/%s" % (self.site_template_path, filename)) ])

				# compile and output
				output_fo = open("output/%s/asset/css/%s" % (self.site, os.path.basename(filename).replace(".scss", ".css")) , "w")
				output_fo.write(    
					scss_compiler.compile(scss)
				)
				output_fo.close()

				# note that this scss has been compiled
				self.compiled_scss.append(filename)

			# output HTML LINK tag for stylesheet
			return "<link rel='stylesheet' type='text/css' href='%s/css/%s' />" % (asset_relative_output_dir, os.path.basename(filename).replace(".scss", ".css"))

		# check if asset exists
		def asset_exists(filename):
			return os.path.exists("%s/%s" % (self.site_asset_path, filename))

		# get list of sub pages :: Jinja function
		def get_sub_pages(subpage):
			if not subpage and not '_subpage' in page_info: return []
			if not subpage: subpage = page_info['_subpage']
			return self._get_site_pages(subpage)

		# get given page full url
		def get_page_url(page):
			relative_path = ""
			for path in os.path.split(os.path.dirname(page_path)):
				if path:
					relative_path += "../"
			return "%s%s" % (relative_path, page.replace(".yml", ".html"))

		# convert time/date in string to unix timestamp
		def string_to_time(string):
			return int( time.mktime( time.strptime( str(dateutil.parser.parse(string)), "%Y-%m-%d %H:%M:%S") ) )

		# convert unix timestamp to string
		def time_to_string(unix_time, format = "%Y-%m-%d %H:%M:%S", tz_offset = 0):
			return time.strftime(format, time.gmtime(unix_time + tz_offset))

		# load template environment
		jinja2 = Environment(loader=FileSystemLoader( "%s/jinja" % self.site_template_path ), extensions=['jinja2.ext.do'])

		# load custom filters
		try:
			import markdown
			jinja2.filters['markdown'] = markdown.markdown
			jinja2.filters['strtotime'] = string_to_time
			jinja2.filters['timetostr'] = time_to_string

		except ImportError:
			pass		

		# load template
		tmpl = jinja2.get_template(page_template)
		template = tmpl.render(
			load_scss = load_scss, 
			load_component = load_component, 
			has_component = has_component, 
			get_sub_pages = get_sub_pages, 
			get_page_url = get_page_url, 
			site = self.site_conf, 
			asset_path = asset_relative_output_dir,
			asset_exists = asset_exists,
			get_time = time.time
		)

		# output page
		# create subdirs
		if not os.path.exists("output/%s/%s" % (self.site, os.path.dirname(page_path))):
			os.makedirs( "output/%s/%s" % (self.site, os.path.dirname(page_path)) )
		
		# get page extension
		ext = os.path.basename(page_template).split(".")
		if len(ext) > 2:
			ext = ext[len(ext) - 2]
		else:
			ext = "txt"

		# output page
		page_fo = open("%s.%s" % (os.path.splitext( "output/%s/%s" % (self.site, page_path) )[0], ext), "w"  )
		page_fo.write(template)
		page_fo.close()

		print "Done."
		return True