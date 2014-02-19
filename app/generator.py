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

import sys, os, fnmatch, yaml, shutil, time, imp, itertools, logging
from jinja2 import Environment, FileSystemLoader

""" Site Generator WebChomp Action Class """
class webchomp_action:

    def __init__(self, site, config = {}):
        self.site = site
        self.config = config        

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
    	site_generator = webchomp_generator(self.site, self.config)

    	# if page not spcecified generate entire site
    	if not 'page' in args or not args['page']:
        	return site_generator.generate()
        # if page specified only generate page
    	else:
        	return site_generator.generate_page(args['page'])

""" Site Generator Class """
class webchomp_generator:

	""" Load specified site, exit out if site isn't found. """
	def __init__(self, site, config={}):

		# webchomp configuration
		self.config = config

		# set site
		self.site = site

		# get logger
		self.logger = logging.getLogger('webchomp')

		# Store site path
		if "path" in self.config and 'site' in self.config['path']:
			conf_site_path = os.path.normpath(self.config['path']['site'])
			self.site_path = os.path.normpath( "%s/%s" % (conf_site_path, site) )
		else:
			self.site_path = os.path.normpath("site/%s" % site)

		# Store other useful pathes
		self.site_page_path = "%s/page" % self.site_path
		self.site_template_path = "%s/template" % self.site_path
		self.site_asset_path = "%s/asset" % self.site_path

		if "path" in self.config and 'extension' in self.config['path']:
			self.extension_path = os.path.normpath( self.config['path']['extension'] )
		else:
			self.extension_path = os.path.normpath("extension")

		self.site_extension_path = os.path.normpath( "%s/extension" % self.site_path )

		if "path" in self.config and 'output' in self.config['path']:
			conf_output_path = os.path.normpath(self.config['path']['output'])
			self.site_output_path = os.path.normpath( "%s/%s" % (conf_output_path, self.site) )
		else:
			self.site_output_path = os.path.normpath("output/%s" % self.site)		

		# site pages cache
		self.site_pages_cache = {}

		# list of pages for site, includes dynamic ones
		self.pages = self.get_site_pages()

		# page info cache
		self.page_info = {}

		# verify site exists
		if not os.path.exists(self.site_path):
			self.logger.critical("Site '%s' does not exist" % site)
			return sys.exit()

		# Found, yay!
		self.logger.info("Found site '%s'" % (site))

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
		for root, dirnames, filenames in itertools.chain( os.walk(self.extension_path), os.walk(self.site_extension_path) ):
			for filename in fnmatch.filter(filenames, '*.py'):
				extension = imp.load_source(
					"extension_%s" % os.path.splitext(filename)[0],
					os.path.join(root, filename)
				)
				if hasattr(extension, 'jinja_extension'):
					self.extensions["extension_%s" % os.path.splitext(filename)[0]] = extension.jinja_extension(self)

				self.logger.debug("Load extension: %s" %  os.path.splitext(filename)[0])


		# load jinja functions
		self.jinja_functions = {}
		for extension in self.extensions:
			# append functions
			if hasattr(self.extensions[extension], "get_jinja_functions"):
				self.jinja_functions[extension.replace("extension_", "")] = dict( self.extensions[extension].get_jinja_functions().items() )

		# load dynamic pages
		for extension in self.extensions:
			# append pages to page_info
			if hasattr(self.extensions[extension], "get_dynamic_pages"):
				dynamic_pages = self.extensions[extension].get_dynamic_pages()
				for key in dynamic_pages:
					self.page_info[key] = dynamic_pages[key]
					self.pages.append(key)
					self.logger.debug("Generate dynamic page: %s" % key)


	""" Generate the loaded site. """
	def generate(self, page = None):

		# Remove old site directory
		if os.path.exists("output/%s" % self.site):
			shutil.rmtree("output/%s" % self.site)
		
		# Recreate output path
		os.mkdir("output/%s" % self.site)
		os.mkdir("output/%s/asset" % self.site)
		os.mkdir("output/%s/asset/css" % self.site)		

		for page in self.pages:
			self.generate_page(page)

	""" Get an array of all pages in the site. """
	def get_site_pages(self, sub_path = ""):

		# if this request was already processed no need to do another lookup
		if sub_path in self.site_pages_cache:
			return self.site_pages_cache[sub_path]

		# find all page definition (yml) files
		matches = []

		for root, dirnames, filenames in os.walk("%s%s" % (self.site_page_path, sub_path)):
			for filename in fnmatch.filter(filenames, '*.yml'):
				matches.append( os.path.join(root, filename).replace(self.site_page_path, "").replace("\\", "/")[1:] )

		# cache the results
		self.site_pages_cache[sub_path] = matches

		return matches

	""" Load page components, store in page_info array """
	def load_page(self, page_path):

		# check if page was already loaded
		if page_path in self.page_info:
			return self.page_info[page_path]

		# make sure page_path exists
		if not os.path.exists("%s/%s" % (self.site_page_path, page_path)):
			return False

		# open page, parse yaml
		page_file = open("%s/%s" % (self.site_page_path, page_path), "r")
		page_info = yaml.load(page_file.read())
		page_file.close()

		# look for _import key, if present import page settings
		# from provided page path
		if "_import" in page_info:
			import_page = self.load_page(page_info['_import'])
			if import_page:
				page_info = dict(import_page.items() + page_info.items())

		# store page info
		self.page_info[page_path] = page_info

		return page_info

	""" Set page components """
	def set_component(self, page_path, component_name, component_value):

		# get page info
		page_info = self.load_page(page_path)

		# create dict if page_info not loaded
		if not page_info:
			page_info = {}

		# set value
		page_info[component_name] = component_value

		# save page
		page_file = open("%s/%s" % (self.site_page_path, page_path), "w")
		page_file.write( yaml.dump(page_info, default_flow_style=False) )
		page_file.close()

		return True

	"""  Generate specified page. """
	def generate_page(self, page_path, page_info = {}, pagination = 1):

		if pagination == 1:
			self.logger.info("Generate page: '%s'" % page_path)
		else:
			self.logger.info("Generate page: '%s' -- Page %s" % (page_path, pagination))

		# get page info
		if not page_info:
			page_info = self.load_page(page_path)
			if not page_info: 
				self.logger.error("Page '%s' was not found." % page_path)
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
			self.logger.error("Template '%s' for page '%s' does not exist." % (page_template, page_path))

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
			if hasattr(self.extensions[extension], "get_jinja_filters"):
				jinja2.filters = dict( jinja2.filters.items() + self.extensions[extension].get_jinja_filters().items() )

		# load template
		tmpl = jinja2.get_template(page_template)
		template = tmpl.render(
			site = self.site_conf,
			current_page = page_path,
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
		template_notes += "<!-- WebChomp <http://chompy.me/projects/webchomp.html> is released under the GPL software license. -->\n"

		# output page
		page_fo = open("%s%s.%s" % (os.path.splitext( "output/%s/%s" % (self.site, page_path) )[0],  "-page%s" % str(pagination) if pagination > 1 else "", ext), "w"  )
		page_fo.write(template_notes + template)
		page_fo.close()

		return True