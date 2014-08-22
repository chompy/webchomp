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

import os

class jinja_extension:

    """ Jinja extension, page related functions. """

    def __init__(self, generator):
        self.generator = generator

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            'get_sub_pages' : self.get_sub_pages,
            'get_page_url' : self.get_page_url,
            'generate_pagination' : self.generate_pagination,
            'get_page_path' : self.get_page_path,

            # shortened names
            'subpages' : self.get_sub_pages,
            'pageurl' : self.get_page_url,
            'path' : self.get_page_path,
            'pagination' : self.generate_pagination,
        }

    def get_sub_pages(self, subpage):

        """ Returns list of subpages for given path. """

        if not subpage and not '_subpage' in self.generator.current_page_info: return []
        if not subpage: subpage = self.generator.current.page_info['_subpage']
        return self.generator.get_site_pages(subpage)

    def get_page_url(self, page = "", pagination = 1, ext = None):

        """ Get relative URL for given page. """

        # get current page if page not given
        if not page: page = self.generator.current_page_path

        # get relative path to page
        relative_path = ""
        for path in os.path.split(os.path.dirname(self.generator.current_page_path)):
            if path:
                relative_path += "../"

        # get page info
        page_info = self.generator.load_page(page)
        if page_info and '_template' in page_info and page_info['_template']:
            # get page extension
            if not ext:
                ext = os.path.basename(page_info['_template']).split(".")
            
                if len(ext) > 2:
                    ext = ext[len(ext) - 2]
                else:
                    ext = "html"
            return "%s%s%s.%s" % (relative_path, os.path.splitext(page)[0], ("-page%s" % str(pagination) if pagination > 1 else ""), ext)

        return "%s%s%s.%s" % (relative_path, os.path.splitext(page)[0], ("-page%s" % str(pagination) if pagination > 1 else ""), "html")

    def generate_pagination(self, page_no):

        """ Generates same page with different pagination value. """

        self.generator.generate_page(page_path=self.generator.current_page_path, pagination=page_no)
        return ""

    def get_page_path(self, page = ""):

        """ Returns array of parent pages. """

        # get current page if page not given
        if not page: page = self.generator.current_page_path

        # split page up by directory and generate a list of
        # pathes from it
        path_children = []
        for index, path in enumerate(os.path.normpath(page).split(os.sep)):
            if not path: continue

            # splice together the full path to the current page
            full_path = "%s" % (os.path.splitext( "/".join(os.path.normpath(page).split(os.sep)[0:index + 1] ) )[0].strip())

            # make sure this page exists
            if full_path in self.generator.pages:
                path_children.append(full_path)
            elif "%s.yml" % full_path in self.generator.pages:
                path_children.append("%s.yml" % full_path)

            
        return path_children
