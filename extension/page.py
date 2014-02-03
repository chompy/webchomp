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
    Jinja extension, page related functions.
"""

import os

class jinja_extension:

    def __init__(self, page_obj):
        self.page = page_obj

        # list containing already compiled SCSS to prevert recompiling
        self.compiled_scss = []

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            'get_sub_pages' : self.get_sub_pages,
            'get_page_url' : self.get_page_url,
            'generate_pagination' : self.generate_pagination
        }

    # get list of sub pages :: Jinja function
    def get_sub_pages(self, subpage):
        if not subpage and not '_subpage' in self.page.current_page_info: return []
        if not subpage: subpage = self.page.current.page_info['_subpage']
        return self.page.get_site_pages(subpage)

    # get given page full url
    def get_page_url(self, page = ""):
        # get current page if page not given
        if not page: page = self.page.current_page_path

        # get relative path to page
        relative_path = ""
        for path in os.path.split(os.path.dirname(self.page.current_page_path)):
            if path:
                relative_path += "../"

        # get page info
        page_info = self.page.load_page(page)
        if page_info and '_template' in page_info and page_info['_template']:
            # get page extension
            ext = os.path.basename(page_info['_template']).split(".")
            if len(ext) > 2:
                ext = ext[len(ext) - 2]
            else:
                ext = "html"
            return "%s%s.%s" % (relative_path, os.path.splitext(page)[0], ext)

        return "%s%s.%s" % (relative_path, os.path.splitext(page)[0], "html")

    # regenerate same page with different pagination
    def generate_pagination(self, page_no):
        self.page.generate_page(self.page.current_page_path, page_no)
        return ""