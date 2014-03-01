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
import os, logging, re

class jinja_extension:

    """ Handles compiling and embedding of SCSS files. """

    def __init__(self, generator):
        self.generator = generator

        # list containing already compiled SCSS to prevert recompiling
        self.compiled_scss = []

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            'load' : self.load_scss
        }

    def load_scss(self, filename):

        """ 
        Loads and compiles SCSS file and adds as asset. Returns
        HTML LINK tag containing file path to outputted CSS file.
        """

        # load PyScss         
        from scss import Scss

        # make sure we haven't already compiled
        if not filename in self.compiled_scss:

            # make sure scss file exists
            if not os.path.exists("%s/scss/%s" % (self.generator.site_template_path, filename)): return ""

            # open file
            scss_fo = open("%s/scss/%s" % (self.generator.site_template_path, filename), "r")
            scss = scss_fo.read()
            scss_fo.close()

            # load compiler
            scss_compiler = Scss(search_paths = [ os.path.dirname("%s/scss/%s" % (self.generator.site_template_path, filename)) ])

            # compile
            compiled_css = scss_compiler.compile(scss)

            # get all urls in CSS
            if "asset" in self.generator.jinja_functions and "add" in self.generator.jinja_functions['asset'] and "exists" in self.generator.jinja_functions['asset']:
                regex = re.compile("url\((.*)\)")
                for image_path in regex.findall(compiled_css):
                    image_path = image_path.replace("../", "")
                    # add asset
                    self.generator.jinja_functions['asset']['add'](image_path)


            # create css dir if not exist
            if not os.path.exists("%s/asset/css" % self.generator.site_output_path):
                os.mkdir("%s/asset/css" % self.generator.site_output_path)

            # output to css
            output_fo = open("%s/asset/css/%s" % (self.generator.site_output_path, os.path.basename(filename).replace(".scss", ".css")) , "w")
            output_fo.write(    
                scss_compiler.compile(scss)
            )
            output_fo.close()

            # note that this scss has been compiled
            self.compiled_scss.append(filename)

        # output HTML LINK tag for stylesheet
        return "<link rel='stylesheet' type='text/css' href='%s/css/%s' />" % (self.generator.asset_relative_output_dir, os.path.basename(filename).replace(".scss", ".css"))
