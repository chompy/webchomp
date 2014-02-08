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

import os, hashlib, shutil

"""
    Main asset processor class.
"""

class asset:

    def __init__(self, page):

        # get page obj
        self.page = page

        # get a list of used assets so that they don't get reprocessed
        self.processed_assets = []        

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
        
"""
    Asset Jinja Extension.
"""

class jinja_extension:

    def __init__(self, page_obj):
        self.asset_processor = asset(page_obj)

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            "exists" : self.asset_processor.asset_exists,
            "add" : self.asset_processor.asset_add
        }

import markdown, re
from markdown.inlinepatterns import ImagePattern, IMAGE_LINK_RE
from markdown.inlinepatterns import LinkPattern, LINK_RE

"""
    Asset Markdown Extension.
"""

class markdown_extension(markdown.extensions.Extension):

    def __init__(self, page_obj):
        self.asset_processor = asset(page_obj)

    def extendMarkdown(self, md, md_globals):

        # get all IMG tags, process asset
        md.inlinePatterns['image_link'] = markdown_asset_image_pattern(self.asset_processor, IMAGE_LINK_RE, md)

        # get all A tags, process asset
        md.inlinePatterns['link'] = markdown_asset_link_pattern(self.asset_processor, LINK_RE, md)


"""
    Parses image tags in markdown, adds to asset process.
"""

class markdown_asset_image_pattern(ImagePattern):

    def __init__(self, asset_processor, pattern, markdown_instance=None):
        ImagePattern.__init__(self, pattern, markdown_instance)
        self.asset_processor = asset_processor

    def handleMatch(self, m):
        # get node
        node = ImagePattern.handleMatch(self, m)
        # get image src
        src = node.attrib.get('src')
        # if image is in assets process and update node with new url
        if os.path.exists("%s/%s" % (self.asset_processor.page.site_asset_path, src)):
            node.attrib['src'] = self.asset_processor.asset_add(src)
        return node

"""
    Parses A tags in markdown, adds to asset process.
"""

class markdown_asset_link_pattern(LinkPattern):

    def __init__(self, asset_processor, pattern, markdown_instance=None):
        LinkPattern.__init__(self, pattern, markdown_instance)
        self.asset_processor = asset_processor

    def handleMatch(self, m):
        # get node
        node = LinkPattern.handleMatch(self, m)
        # get link href
        src = node.attrib.get('href')
        # if link is in assets process and update node with new url
        if os.path.exists("%s/%s" % (self.asset_processor.page.site_asset_path, src)):
            node.attrib['href'] = self.asset_processor.asset_add(src)
        return node        