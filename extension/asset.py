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

import os, shutil, urlparse, imp, itertools, fnmatch

class asset:

    """ Main asset processor class. """

    def __init__(self, generator):

        # get generator object
        self.generator = generator

        # get a list of used assets so that they don't get reprocessed
        self.processed_assets = []

        # load all filters
        self.extensions = {}
        for root, dirnames, filenames in itertools.chain( os.walk("extension/"), os.walk(self.generator.site_extension_path) ):
            for filename in fnmatch.filter(filenames, '*.py'):
                extension = imp.load_source(
                    "asset_filter_%s" % os.path.splitext(filename)[0],
                    os.path.join(root, filename)
                )
                if hasattr(extension, 'asset_filter'):
                    self.extensions[os.path.splitext(filename)[0]] = extension.asset_filter(self)

        # load tag functions
        self.filters = {}
        for extension in self.extensions:
            # append functions
            if hasattr(self.extensions[extension], "get_filters"):
                self.filters = dict( self.filters.items() + self.extensions[extension].get_filters().items() )

    def asset_exists(self, filename):

        """ Returns actual asset path if given file exists. """

        # default path in asset/
        if os.path.exists("%s/%s" % (self.generator.site_asset_path, filename)):
            return "%s/%s" % (self.generator.site_asset_path, filename)

        # template/asset
        if os.path.exists("%s/%s/%s" % (self.generator.site_template_path, "asset", filename)):
            return "%s/%s/%s" % (self.generator.site_template_path, "asset", filename)

        # custom user pathes
        if 'asset' in self.generator.site_conf and 'paths' in self.generator.site_conf['asset']:
            for path in self.generator.site_conf['asset']['paths']:
                if os.path.exists("%s/%s" % (path, filename)):
                    return "%s/%s" % (path, filename)

                if os.path.exists("%s/%s/%s" % (self.generator.site_path, path, filename)):
                    return "%s/%s/%s" % (self.generator.site_path, path, filename)

    def prepare_output(self, filename):

        """
        Prepares for output by making sure
        appropiate output path exists and
        returns path file should be copied
        too.
        """
        # make output dir if not exist
        if not os.path.exists("%s/asset/%s" % (self.generator.site_output_path, os.path.dirname(filename))):
            os.makedirs("%s/asset/%s" % (self.generator.site_output_path, os.path.dirname(filename)) )

        return "%s/asset/%s" % (self.generator.site_output_path, filename)

    def get_output_path(self, filename, relative_path = True):

        """
        Return output path to file for web.
        """

        # return relative path to asset
        if relative_path:
            return "%s/%s" % (self.generator.asset_relative_output_dir, filename)
        # return absolute path to asset
        else:
            return "/asset/%s" % filename

    def asset_add(self, filename, relative_path = True):

        """ 
        Flags that given file should be outputted. Returns path to 
        outputted file. 
        """

        # get a path where asset exists
        path_to = self.asset_exists(filename)
        if not path_to: return ""

        # determine if asset has already been processed
        if not filename in self.processed_assets:

            # copy asset to output dir
            shutil.copy(path_to, self.prepare_output(filename))

            # add to processed list
            self.processed_assets.append(filename)

        # return relative path to asset
        return self.get_output_path(filename)

    def asset_filter(self, asset_filter, filename, arguments={}, relative_path = True):

        """
        Loads an asset filter.
        """

        if not asset_filter in self.filters: return ""
        if filename in self.processed_assets: return self.get_output_path(filename, relative_path)
        return self.filters[asset_filter](filename, arguments, relative_path)

    def asset_image(self, filename, resize={}, relative_path = True):

        """
        Alias for image_resize asset filter.
        """

        return self.asset_filter("image_resize", filename, resize, relative_path)

    def asset_urlparse(self, url, relative_path = True):

        """
        Parse a asset from a url with URL params.
        """
        # parse image url
        image_url = urlparse.urlparse(url)

        # get url vars
        url_vars = {}
        for key in urlparse.parse_qs(image_url.query):
            url_vars[key] = urlparse.parse_qs(image_url.query)[key][0]
       
        # find filter, use image if none given, run filter
        if not "filter" in url_vars:
            url_vars['filter'] = "image_resize"
        return self.asset_filter(url_vars['filter'], image_url.path, url_vars, relative_path)


class jinja_extension:

    """ Asset Jinja extension. """

    def __init__(self, generator):
        self.asset_processor = asset(generator)

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            "exists" : self.asset_processor.asset_exists,
            "add" : self.asset_processor.asset_add,
            "image" : self.asset_processor.asset_image,
            "filter" : self.asset_processor.asset_filter,
            "urlparse" : self.asset_processor.asset_urlparse
        }

import markdown, re
from markdown.inlinepatterns import ImagePattern, IMAGE_LINK_RE
from markdown.inlinepatterns import LinkPattern, LINK_RE

class markdown_extension(markdown.extensions.Extension):

    """ Asset Markdown extension. """

    def __init__(self, page_obj):
        self.asset_processor = asset(page_obj)

    def extendMarkdown(self, md, md_globals):

        # get all IMG tags, process asset
        md.inlinePatterns['image_link'] = markdown_asset_image_pattern(self.asset_processor, IMAGE_LINK_RE, md)

        # get all A tags, process asset
        md.inlinePatterns['link'] = markdown_asset_link_pattern(self.asset_processor, LINK_RE, md)

class markdown_asset_image_pattern(ImagePattern):

    """ Parses image tags in markdown, adds to asset process. """

    def __init__(self, asset_processor, pattern, markdown_instance=None):
        ImagePattern.__init__(self, pattern, markdown_instance)
        self.asset_processor = asset_processor

    def handleMatch(self, m):
        # get node
        node = ImagePattern.handleMatch(self, m)
        # get image src
        src = node.attrib.get('src')
        # parse image url
        output_asset = self.asset_processor.asset_urlparse(src)
        if output_asset:
            node.attrib['src'] = output_asset
        return node

class markdown_asset_link_pattern(LinkPattern):

    """ Parses A tags in markdown, adds to asset process. """

    def __init__(self, asset_processor, pattern, markdown_instance=None):
        LinkPattern.__init__(self, pattern, markdown_instance)
        self.asset_processor = asset_processor

    def handleMatch(self, m):
        # get node
        node = LinkPattern.handleMatch(self, m)
        # get link href
        src = node.attrib.get('href')
        # if link is in assets process and update node with new url
        output_asset = self.asset_processor.asset_urlparse(src)
        if output_asset:
            node.attrib['href'] = output_asset
        return node        

class asset_filter:

    """ Default asset filters. """

    def __init__(self, asset_processor):
        self.asset_processor = asset_processor

    def get_filters(self):
        return {
            "image_resize" : self.image_resize
        }

    def image_resize(self, filename, resize={}, relative_path = True):

        """ 
        Flags that image should be outputted, also provides resize 
        options. Returns path to resized image.
        """

        # get a path where asset exists
        path_to = self.asset_processor.asset_exists(filename)
        if not path_to: return ""

        # must be a file
        if not os.path.isfile(path_to): return ""
        
        # import PIL lib
        import PIL
        from PIL import Image, ImageOps

        # import hashlib
        import hashlib

        # process resize args
        resize_args = {}
        for arg in resize:
            # width
            if arg == "w" or arg == "width":
                resize_args['w'] = resize[arg]
            elif arg == "h" or arg == "height":
                resize_args['h'] = resize[arg]
            elif arg == "c" or arg =="crop":
                resize_args['c'] = resize[arg]

        # generate a hash from resize args to name the final out
        arg_hash = hashlib.sha224(str(resize_args)).hexdigest()[0:6]

        # get filename of resized image
        new_filename = "%s_%s%s" % (os.path.splitext(filename)[0], arg_hash, os.path.splitext(filename)[1])

        # determine if asset has almost been processed
        if not new_filename in self.asset_processor.processed_assets:

            # use PIL to reseize
            img = Image.open(path_to)

            # make sure w/h set
            if not "w" in resize_args:
                resize_args['w'] = img.size[0]
            if not "h" in resize_args:
                resize_args['h'] = img.size[1]

            # resize without crop
            if not "c" in resize_args or not resize_args['c']:
                img.thumbnail((int(resize_args["w"]), int(resize_args["h"])), PIL.Image.ANTIALIAS)

            # crop
            else:
               img = ImageOps.fit(img, (int(resize_args["w"]), int(resize_args["h"])), PIL.Image.ANTIALIAS)

            # save image asset to output dir
            img.save(self.asset_processor.prepare_output(new_filename))
            
            # add to processed list
            self.asset_processor.processed_assets.append(new_filename)

        # return relative path to asset
        return self.asset_processor.get_output_path(new_filename)