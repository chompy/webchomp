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

import os, sys, shutil, subprocess, itertools

class jinja_extension:

    """ Jinja extension, uses AbiWord to convert DOC to HTML. """

    def __init__(self, generator):
        self.generator = generator

        # get path to doc2page DOC files
        self.doc_path = os.path.normpath("%s/doc2page" % self.generator.site_path)
        if "doc2page" in self.generator.site_conf and "path" in self.generator.site_conf['doc2page']:
            self.doc_path = os.path.normpath("%s/%s" % (self.generator.site_path, self.generator.site_conf['doc2page']['path']))

        # path to abiword
        self.abiword = "abiword"
        if "doc2page" in self.generator.site_conf and "abiword" in self.generator.site_conf['doc2page']:
            self.abiword = os.path.normpath(self.generator.site_conf['doc2page']['abiword'])
            if not os.path.exists(self.abiword):
                self.abiword = os.path.normpath("%s/%s" % (self.generator.site_path, self.generator.site_conf['doc2page']['abiword']))

        # asset path, for assets found inside DOC files
        self.asset_relative_path = "doc2page"
        self.asset_path = os.path.normpath("%s/%s/doc2page" % (self.generator.site_output_path, "asset"))
        if "doc2page" in self.generator.site_conf and "asset_path" in self.generator.site_conf['doc2page']:
            self.asset_relative_path = self.generator.site_conf['doc2page']['asset_path']
            self.asset_path = os.path.normpath("%s/%s/%s" % (self.generator.site_output_path, "asset",  self.generator.site_conf['doc2page']['asset_path']))

        # create asset path if not exists
        if not os.path.exists(self.asset_path):
            os.makedirs(self.asset_path)


    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            'convert' : self.convert,
            'exists' : self.exists
        }

    def exists(self, doc):

        """ Returns if given DOC file exists. """

        return os.path.exists(os.path.normpath("%s/%s" % (self.doc_path, doc)))


    def convert(self, doc):

        """ Convert given DOC file to HTML, return HTML. """

        current_doc_path = os.path.normpath("%s/%s" % (self.doc_path, doc))
        
        # use abiword to do the conversion
        if subprocess.call([self.abiword, '--to=html', current_doc_path]):
            return "[Unable to convert '%s' to page content.]" % os.path.basename(current_doc_path)

        # get path to outputed HTML file
        html_output_path = "%s.html" % os.path.splitext(current_doc_path)[0]

        # get outputted HTML
        html_io = open(html_output_path, "r")
        html = html_io.read()
        html_io.close()
        
        # get only what's inside BODY tag
        html_body = html[html.find("<body>")+6:html.find("</body>")]

        # get assets
        asset_path = "%s_files" % html_output_path
        if os.path.exists(asset_path):
            for filename in os.listdir(asset_path):

                new_file_path = os.path.normpath("%s/%s/%s" % (self.asset_path, os.path.splitext(os.path.basename(current_doc_path))[0], filename))

                print os.path.dirname(new_file_path)
                # create asset path if not exists
                if not os.path.exists(os.path.dirname(new_file_path)):
                    os.makedirs(os.path.dirname(new_file_path))

                # move asset
                os.rename(
                    "%s/%s" % (asset_path, filename),
                    os.path.normpath(new_file_path)
                )

                # set filepath in html doc
                html_body = html_body.replace(
                    os.path.basename("%s_files" % html_output_path), 
                    "%s/%s/%s" % (self.generator.asset_relative_output_dir, self.asset_relative_path, os.path.splitext(os.path.basename(current_doc_path))[0] )
                )

            # delete asset dir
            os.rmdir(asset_path)

        # delete generated html file
        os.remove(html_output_path)

        # output html body
        return html_body
        