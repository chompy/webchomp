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

import sys, os, yaml, hashlib, fnmatch, logging
from boto.s3.connection import S3Connection

""" S3Push WebChomp Action Class """
class webchomp_action:

    def __init__(self, site, config = {}):
        self.site = site
        self.config = config

    def get_webchomp_actions(self):
        return {
            's3sync' : self.s3sync,
            's3push' : self.s3sync
        }

    def get_webchomp_arguments(self):
        return {
            's3sync' : ['page'],
            's3push' : ['page'],
        }

    def s3sync(self, args):
        s3 = webchomp_s3push(self.site)

        # if page arg provided only sync one page
        if 'page' in args and args['page']:
            return s3.upload_file(args['page'])
        # all pages and assets
        else:
            return s3.sync()

class webchomp_s3push:

    """ Amazon S3 Uploader Class """

    def __init__(self, site, config = {}):

        # webchomp configuration
        self.config = config

        # get logger
        self.logger = logging.getLogger('webchomp')

        # set site
        self.site = site
        self.site_path = "site/%s" % site
        self.site_output_path = "output/%s" % site

        # verify site exists
        if not os.path.exists(self.site_path):
            self.logger.critical("Site '%s' does not exist" % site)
            raise Exception("Site '%s' does not exist" % site)
            return

        # Found, yay!
        self.logger.info("Found site '%s'" % (site))

        # load site conf yml
        self.site_conf = {}
        if os.path.exists("%s/site.yml" % self.site_path):
            f_io = open("%s/site.yml" % self.site_path, "r")
            self.site_conf = yaml.load(f_io.read())
            f_io.close()

        # get s3 key/secret
        if not "amazon_s3" in self.site_conf or not "access_key" in self.site_conf['amazon_s3'] or not 'access_secret' in self.site_conf['amazon_s3']:
            self.logger.critical("Amazon S3 key/secret have not been set in site.yml.")
            raise Exception("Amazon S3 key/secret have not been set in site.yml.")
            return

        self.aws_access_key = self.site_conf['amazon_s3']['access_key']
        self.aws_secret_key = self.site_conf['amazon_s3']['access_secret']

        # get bucket
        if not "bucket" in self.site_conf['amazon_s3']:
            self.logger.critical("Amazon S3 bucket has not been set in site.yml.")
            raise Exception("Amazon S3 bucket has not been set in site.yml.")
            return

        self.s3_bucket_name = self.site_conf['amazon_s3']['bucket']

        # make s3 connection
        self.s3_conn = S3Connection(self.aws_access_key, self.aws_secret_key)

        # get bucket
        if self.s3_conn.lookup(self.s3_bucket_name) is None:
            self.logger.critical("Bucket '%s' does not exist." % self.s3_bucket_name)
            raise Exception("Bucket '%s' does not exist." % self.s3_bucket_name)

        self.s3_bucket = self.s3_conn.get_bucket(self.s3_bucket_name, validate=False)
        self.logger.info("Found bucket '%s'" % self.s3_bucket_name)

        # get list of keys in bucket
        self.s3_bucket_list = {}
        for key in self.s3_bucket.list():
            self.s3_bucket_list[key.name] = key        

    def sync(self, delete_remote = True):

        """ Sync local to remote. """

        # check remote files, see if exist locally, delete otherwise
        if delete_remote:
            for i in self.s3_bucket_list:
                if not os.path.exists("%s/%s" % (self.site_output_path, i)):
                    self.s3_bucket_list[i].delete()

        # get all local files and upload
        for root, dirnames, filenames in os.walk(self.site_output_path):
            for filename in fnmatch.filter(filenames, '*'):
                self.upload_file( ("%s/%s" % (root, filename)).replace(self.site_output_path, "") ) 

    def upload_file(self, file_path):

        """ Upload file to S3 """

        file_path = os.path.normpath(file_path).replace("\\", "/")
        if file_path[0] == "/": file_path = file_path[1:]

        # check if file exists locally
        if not os.path.exists("%s/%s" % (self.site_output_path, file_path)):
            return False

        # open local file, get md5 and file pointer
        local_file = open("%s/%s" % (self.site_output_path, file_path), "rb")
        local_md5 = hashlib.md5(local_file.read()).hexdigest()
        local_file.close()
        
        # search bucket list for file
        if file_path in self.s3_bucket_list:
            key = self.s3_bucket_list[file_path]
        else:
            key = self.s3_bucket.get_key(file_path, validate=False)

        # compare md5
        # TODO find better way
        if key.etag and key.etag.replace('"',"") == local_md5:
            self.logger.info("Upload file: '%s' (Skipped, no change)" % file_path)
            return False

        self.logger.info("Upload file: '%s'" % file_path)

        # sudo upload
        key.set_contents_from_filename("%s/%s" % (self.site_output_path, file_path))

        # make public
        key.make_public()

        return True