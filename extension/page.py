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
            'get_page_url' : self.get_page_url
        }

    # get list of sub pages :: Jinja function
    def get_sub_pages(self, subpage):
        if not subpage and not '_subpage' in self.page.current_page_info: return []
        if not subpage: subpage = self.page.current.page_info['_subpage']
        return self.page.get_site_pages(subpage)

    # get given page full url
    def get_page_url(self, page):
        relative_path = ""
        for path in os.path.split(os.path.dirname(self.page.current_page_path)):
            if path:
                relative_path += "../"
        return "%s%s" % (relative_path, page.replace(".yml", ".html"))


