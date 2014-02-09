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

import sys, os, fnmatch, yaml, shutil, time, imp, itertools
from jinja2 import Environment, FileSystemLoader

""" Site Generator WebChomp Action Class """
class webchomp_action:

    def __init__(self, site):
        self.site = site

    def get_webchomp_actions(self):
        return {
            'generate' : self.generate
        }

    def get_webchomp_arguments(self):
        return {
        	'generate' : ['page']
        }

    def generate(self, args):

    	# init generator class
    	site_generator = webchomp_generator(self.site)

    	# if page not spcecified generate entire site
    	if not 'page' in args or not args['page']:
        	return site_generator.generate()
        # if page specified only generate page
    	else:
        	return site_generator.generate_page(args['page'])

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
		self.site_extension_path = "%s/extension" % self.site_path
		self.site_output_path = "output/%s" % self.site

		# page info cache
		self.page_info = {}

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

		# load all jinja extensions
		self.extensions = {}
		for root, dirnames, filenames in itertools.chain( os.walk("extension/"), os.walk(self.site_extension_path) ):
			for filename in fnmatch.filter(filenames, '*.py'):
				extension = imp.load_source(
					"extension_%s" % os.path.splitext(filename)[0],
					os.path.join(root, filename)
				)
				if hasattr(extension, 'jinja_extension'):
					self.extensions["extension_%s" % os.path.splitext(filename)[0]] = extension.jinja_extension(self)

		# load jinja functions
		self.jinja_functions = {}
		for extension in self.extensions:
			# append functions
			self.jinja_functions[extension.replace("extension_", "")] = dict( self.extensions[extension].get_jinja_functions().items() )

	""" Generate the loaded site. """
	def generate(self, page = None):

		# Remove old assets directory
		if os.path.exists("output/%s/asset" % self.site):
			shutil.rmtree("output/%s/asset" % self.site)
		
		# Recreate asset path
		os.mkdir("output/%s/asset" % self.site)

		# Get pages in site
		print "Generating pages..."
		pages = self.get_site_pages()
		for page in pages:
			self.generate_page(page)

	""" Get an array of all pages in the site. """
	def get_site_pages(self, sub_path = ""):

		# find all page definition (yml) files
		matches = []

		for root, dirnames, filenames in os.walk("%s%s" % (self.site_page_path, sub_path)):
			for filename in fnmatch.filter(filenames, '*.yml'):
				matches.append( os.path.join(root, filename).replace(self.site_page_path, "").replace("\\", "/")[1:] )
		return matches

	""" Load page components, store in page_info array """
	def load_page(self, page_path):

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

	""" Set page components, store in page_info array """
	def set_component(self, page_path, component_name, component_value):

		print "Settings component '%s' for '%s'..." % (component_name, page_path),

		# get page info
		page_info = self.load_page(page_path)

		# create dict if page_info not loaded
		if not page_info:
			page_info = {}

		# set value
		page_info[component_name] = component_value

		print yaml.dump(page_info, default_flow_style=False)

		# save page
		page_file = open("%s/%s" % (self.site_page_path, page_path), "w")
		page_file.write( yaml.dump(page_info, default_flow_style=False) )
		page_file.close()
		print "Done"
		return True

	"""  Generate specified page. """
	def generate_page(self, page_path, pagination = 1):

		if pagination == 1: print "Processing '%s'..." % page_path.replace(self.site_page_path, ""),

		# get page info
		page_info = self.load_page(page_path)
		if not page_info: 
			print "Failed (Page not found)."
			return False

		# find page template
		page_template = page_info['_template'] if '_template' in page_info else (self.site_conf['default_template'] if 'default_template' in self.site_conf else "default.html.jinja")

		# get page extension
		ext = os.path.basename(page_template).split(".")
		if len(ext) > 2:
			ext = ext[len(ext) - 2]
		else:
			ext = "html"

		# vars used by extensions
		self.current_page_info = page_info
		self.current_page_path = page_path
		self.current_page_template = page_template
		self.current_page_extension = ext

		# make sure page_template exists
		if not os.path.exists("%s/jinja/%s" % (self.site_template_path, page_template)):
			print "Failed (Page template does not exist)."
			return False

		# get page relative asset dir
		asset_relative_output_dir = "asset"
		for subpath in os.path.split(os.path.dirname(page_path)):
			if subpath: asset_relative_output_dir = "../%s" % asset_relative_output_dir
		self.asset_relative_output_dir = asset_relative_output_dir

		# load template environment
		jinja2 = Environment(loader=FileSystemLoader( "%s/jinja" % self.site_template_path ), extensions=['jinja2.ext.do'])

		# load custom filters
		for extension in self.extensions:
			# append filters
			jinja2.filters = dict( jinja2.filters.items() + self.extensions[extension].get_jinja_filters().items() )

		# load template
		tmpl = jinja2.get_template(page_template)
		template = tmpl.render(
			site = self.site_conf,
			current_page = self.current_page_path,
			asset_path = asset_relative_output_dir,
			f = self.jinja_functions,
			pagination = int(pagination)
		)


		# output page
		# create subdirs
		if not os.path.exists("output/%s/%s" % (self.site, os.path.dirname(page_path))):
			os.makedirs( "output/%s/%s" % (self.site, os.path.dirname(page_path)) )
		
		# append generator notes to page output
		template_notes = "<!-- Generated by WebChomp. -->\n"
		template_notes += "<!-- WebChomp <https://bitbucket.org/chompy/webchomp> is released under the GPL software license. -->\n"

		# output page
		page_fo = open("%s%s.%s" % (os.path.splitext( "output/%s/%s" % (self.site, page_path) )[0], str(pagination) if pagination > 1 else "", ext), "w"  )
		page_fo.write(template_notes + template)
		page_fo.close()

		if pagination == 1: print "Done."
		return True