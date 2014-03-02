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

import re, os, fnmatch, shutil, imp, itertools, urlparse

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
        self.tags = self.get_tags()
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
            'imgleft' : self.image,
            'imgright' : self.image_right,
            'imgcenter' : self.image_center,
            'iframe' : self.iframe,
            'youtube' : self.youtube
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
                if re.sub('<[^<]+?>', '', match[0].lower()) == tag.lower():
                    string = string.replace("[%s %s]" % (match[0], match[1]), self.tags[tag]( re.sub('<[^<]+?>', '', match[1]) ))

        return string


    def image(self, filename, align="left"):

        """
        Allows the addition of an image asset from a tag.
        """

        # make sure asset extension exists
        if not "asset" in self.generator.jinja_functions or not "add" in self.generator.jinja_functions['asset'] or not "exists" in self.generator.jinja_functions['asset']:
            return ""

        img_tag = "<img src='"
        img_tag_close = "' class='align-%s' />" % align

        # parse image url
        image_url = urlparse.urlparse(filename)

        # get url vars
        url_vars = {}
        for key in urlparse.parse_qs(image_url.query):
            url_vars[key] = urlparse.parse_qs(image_url.query)[key][0]

        # if image is in assets process and update node with new url
        if self.generator.jinja_functions['asset']['exists'](image_url.path):
            return img_tag + self.generator.jinja_functions['asset']['image'](image_url.path, url_vars) + img_tag_close

        # in image/filename
        elif self.generator.jinja_functions['asset']['exists']( "image/%s" % os.path.basename(image_url.path) ):
            return img_tag + self.generator.jinja_functions['asset']['image']( "image/%s" % os.path.basename(image_url.path), url_vars) + img_tag_close

        # in images/filename
        elif self.generator.jinja_functions['asset']['exists']( "images/%s" % os.path.basename(image_url.path) ):
            return img_tag + self.generator.jinja_functions['asset']['image']( "images/%s" % os.path.basename(image_url.path), url_vars) + img_tag_close

        return ""

    def image_right(self, filename):
        return self.image(filename, "right")

    def image_center(self, filename):
        return self.image(filename, "center")

    def iframe(self, url, classname = ""):
        return "<div class='iframe-container'><iframe src='%s' class='%s' seamless='seamless'></iframe></div>" % (url, classname)

    def youtube(self, url):

        # get youtube id
        query = urlparse.urlparse(url)
        if query.hostname == 'youtu.be':
            return self.iframe("https://www.youtube.com/embed/%s" % query.path[1:], 'youtube')
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = urlparse.parse_qs(query.query)
                return self.iframe("https://www.youtube.com/embed/%s" % p['v'][0], 'youtube')
            if query.path[:7] == '/embed/':
                return self.iframe("https://www.youtube.com/embed/%s" % query.path.split('/')[2], 'youtube')
            if query.path[:3] == '/v/':
                return self.iframe("https://www.youtube.com/embed/%s" % query.path.split('/')[2], 'youtube')
        
        return ""