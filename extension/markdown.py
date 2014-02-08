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
    Jinja extension, provides Markdown filter.
"""

import markdown, imp, itertools, os, fnmatch

class jinja_extension:

    def __init__(self, page_obj):
        self.page = page_obj

        # load markdown extensions in the same way jinja extensions are loaded
        self.extensions = []
        for root, dirnames, filenames in itertools.chain( os.walk("extension/"), os.walk(self.page.site_extension_path) ):
            for filename in fnmatch.filter(filenames, '*.py'):
                extension = imp.load_source(
                    "extension_%s" % os.path.splitext(filename)[0],
                    os.path.join(root, filename)
                )
                if hasattr(extension, 'markdown_extension'):
                    self.extensions.append(extension.markdown_extension(self.page))

    def get_jinja_filters(self):
        return {
            'markdown' : self.markdown
        }

    def get_jinja_functions(self):
        return {}

    def markdown(self, text):
        return markdown.markdown(text, extensions=self.extensions)