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

class jinja_extension:

    """ Jinja extension, provides access to page components. """

    def __init__(self, generator):
        self.generator = generator

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            'has' : self.has_component,
            'load' : self.load_component,
        }

    def load_component(self, component_name, page_path = "", type="text"):

        """ Load component and returns its value. """

        # load page from page_path
        if page_path:
            sub_page_info = self.generator.load_page(page_path)
            if sub_page_info and component_name in sub_page_info: return sub_page_info[component_name]

        # no page_path use current page component
        elif component_name in self.generator.current_page_info:
            return self.generator.current_page_info[component_name]
        return "[component not found]"

    def has_component(self, component_name, page_path = ""):

        """ Returns true if given component exists. """

        # load page from page_path
        if page_path:
            sub_page_info = self.generator.load_page(page_path)
            if component_name in sub_page_info: return True

        # no page_path use current page component
        elif component_name in self.generator.current_page_info:
            return True

        return False