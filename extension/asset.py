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
    Jinja extension, functions for handling assets.
"""

import os, hashlib, shutil

class jinja_extension:

    def __init__(self, page_obj):
        self.page = page_obj

        # get a list of used assets so that they don't get reprocessed
        self.processed_assets = []

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            "exists" : self.asset_exists,
            "add" : self.asset_add
        }

    # check if asset exists
    def asset_exists(self, filename):
        return os.path.exists("%s/%s" % (self.page.site_asset_path, filename))

    # add asset to output, return relative path to current page
    def asset_add(self, filename, relative_path = True):

        # make sure asset exists
        if not self.asset_exists(filename): return ""

        # determine if asset has almost been processed
        if not filename in self.processed_assets:

            # make output dir if not exist
            if not os.path.exists("%s/asset/%s" % (self.page.site_output_path, os.path.dirname(filename))):
                os.makedirs("%s/asset/%s" % (self.page.site_output_path, os.path.dirname(filename)) )

            # copy asset to output dir
            shutil.copy("%s/%s" % (self.page.site_asset_path, filename), 
                        "%s/asset/%s" % (self.page.site_output_path, filename))

            # add to processed list
            self.processed_assets.append(filename)

        # return relative path to asset
        if relative_path:
            return "%s/%s" % (self.page.asset_relative_output_dir, filename)
        # return absolute path to asset
        else:
            return "/%s" % filename

    def asset_image(self, filename, resize=[]):

        # attempt to find image asset
        if not os.path.exists(filename):
            filename = "%s/%s" % (self.page.site_asset_path, filename)
        if not os.path.exists(filename):
            return ""
        