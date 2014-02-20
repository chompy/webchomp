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

import re, os, fnmatch, shutil, imp, itertools

class jinja_extension:

    """ Jinja extension, provides process of custom tags. """

    def __init__(self, generator):
        self.generator = generator

        # load all tags
        self.extensions = {}
        for root, dirnames, filenames in itertools.chain( os.walk("extension/"), os.walk(self.generator.site_extension_path) ):
            for filename in fnmatch.filter(filenames, '*.py'):
                extension = imp.load_source(
                    "tag_%s" % os.path.splitext(filename)[0],
                    os.path.join(root, filename)
                )
                if hasattr(extension, 'tag_extension'):
                    self.extensions["tag_%s" % os.path.splitext(filename)[0]] = extension.tag_extension(self.generator)

        # load jinja functions
        self.tags = {}
        for extension in self.extensions:
            # append functions
            if hasattr(self.extensions[extension], "get_tags"):
                self.tags = dict( self.tags.items() + self.extensions[extension].get_tags().items() )

    def get_jinja_filters(self):
        return {
            'tags' : self.parse_tags
        }

    def get_tags(self):
        return {
            ''
        }

    def parse_tags(self, string):

        """ 
        Parses custom tags from given string. Runs it through matching
        custom tag extension.
        """

        # regex to match
        regex = re.compile("\[(.*?) (.*?)\]")

        # match
        for match in regex.findall(string):

            # loop through all tags
            for tag in self.tags:
                if match[0].lower() == tag.lower():
                    string = string.replace("[%s %s]" % (match[0], match[1]), self.tags[tag](match[1]))

        return string
