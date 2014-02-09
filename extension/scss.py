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

"""
    Handles compiling and embedding of SCSS files.
"""

import os, logging

class jinja_extension:

    def __init__(self, page_obj):
        self.page = page_obj

        # list containing already compiled SCSS to prevert recompiling
        self.compiled_scss = []

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            'load' : self.load_scss
        }

    # load scss :: Jinja function
    def load_scss(self, filename):

        # load PyScss         
        from scss import Scss

        # make sure we haven't already compiled
        if not filename in self.compiled_scss:

            # make sure scss file exists
            if not os.path.exists("%s/scss/%s" % (self.page.site_template_path, filename)): return ""

            # open file
            scss_fo = open("%s/scss/%s" % (self.page.site_template_path, filename), "r")
            scss = scss_fo.read()
            scss_fo.close()

            # scss logging
            logging.getLogger("scss").addHandler(logging.StreamHandler())

            # load compiler
            scss_compiler = Scss(search_paths = [ os.path.dirname("%s/scss/%s" % (self.page.site_template_path, filename)) ])

            # compile
            compiled_css = scss_compiler.compile(scss)

            # use cssutils to parse urls and add as assets
            try:
                import cssutils
                cssutils.log.setLevel(logging.ERROR)
                sheet = cssutils.parseString(compiled_css)
                for image_path in cssutils.getUrls(sheet):
                    image_path = image_path.replace("../", "")
                    if not os.path.exists("%s/%s" % (self.page.site_asset_path, image_path)): continue

                    # make sure asset function is available
                    if "asset" in self.page.jinja_functions and "add" in self.page.jinja_functions['asset']:
                        self.page.jinja_functions['asset']['add'](image_path)
            except ImportError:
                pass

            # create css dir if not exist
            if not os.path.exists("%s/asset/css" % self.page.site_output_path):
                os.mkdir("%s/asset/css" % self.page.site_output_path)

            # output to css
            output_fo = open("%s/asset/css/%s" % (self.page.site_output_path, os.path.basename(filename).replace(".scss", ".css")) , "w")
            output_fo.write(    
                scss_compiler.compile(scss)
            )
            output_fo.close()

            # note that this scss has been compiled
            self.compiled_scss.append(filename)

        # output HTML LINK tag for stylesheet
        return "<link rel='stylesheet' type='text/css' href='%s/css/%s' />" % (self.page.asset_relative_output_dir, os.path.basename(filename).replace(".scss", ".css"))
