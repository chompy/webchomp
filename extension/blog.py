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
    Jinja extension, provides blog functionality.
"""

import time

class jinja_extension:

    def __init__(self, generator):

        # get site generate object
        self.generator = generator

        # vars
        self.blog_conf = {
            "blog_page_path" : "blog",
            "tag_page_path" : "blog/tag",
            "tag_template" : "blog/tag.html.jinja",
            "archive_page_path" : "blog/archive",
            "archive_template" : "blog/archive.html.jinja"
        }

        # attempt to override vars with site_conf
        if "blog" in self.generator.site_conf:
            self.blog_conf = dict(self.blog_conf.items() + self.generator.site_conf['blog'].items())

        # get all blog posts
        self.posts = self.generator.get_site_pages("/blog")

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            'tags' : self.get_tags,
            'archive_dates' : self.get_archive_dates,
            "blog_conf" : self.get_blog_conf
        }

    def get_dynamic_pages(self):
        return_pages = {}

        # make tag pages
        for tag in self.get_tags():
            return_pages["%s/%s.yml" % (self.blog_conf['tag_page_path'], tag)] = {
                "_title" : "Posts tagged '%s'" % tag,
                "_template" : self.blog_conf['tag_template'],
                "tag" : tag
            }

        # make archive pages
        archive_dates = self.get_archive_dates()
        for date in archive_dates:
            return_pages["%s/%s.yml" % (self.blog_conf['archive_page_path'], time.strftime("%B-%Y", time.gmtime(date)).lower() )] = {
                "_title" : "Post archive for %s" % time.strftime("%B %Y", time.gmtime(date)),
                "_template" : self.blog_conf['archive_template'],
                "date" : date
            }         

        return return_pages

    """ Get list of tags used in blog posts """
    def get_tags(self):

        tags = []

        # iterate all posts and look for 'tag' component
        for post in self.posts:
            page_info = self.generator.load_page(post)
            if "tag" in page_info:

                # tag as comma delimited string
                if type(page_info['tag']) is str:
                    page_info['tag'] = page_info['tag'].split(",")
                
                # iterate through tags add to grand master tag list
                if type(page_info['tag']) is list:
                    for tag in page_info['tag']:
                        if not tag in tags:
                            tags.append(tag.strip().lower())
        return tags

    """ Get list of dates that reference months with archieved posts """
    def get_archive_dates(self):

        dates = []

        # need dateutil
        import dateutil.parser

        # iterate all posts looking for post_date
        for post in self.posts:

            page_info = self.generator.load_page(post)
            if 'post_date' in page_info:
                unix_time = int( time.mktime( time.strptime( str(dateutil.parser.parse(page_info['post_date'])), "%Y-%m-%d %H:%M:%S") ) )
                year = time.strftime("%Y", time.gmtime(unix_time))
                month = time.strftime("%m", time.gmtime(unix_time))
                unix_time = time.mktime( time.strptime("%s/%s" % (month, year), "%m/%Y") )
                if unix_time not in dates:
                    dates.append(unix_time)

        return dates

    """ Get current blog config, exposes it to jinja template. """
    def get_blog_conf(self):
        return self.blog_conf