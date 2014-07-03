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

import time

class jinja_extension:

    """ Jinja extension, provides blog functionality. """

    def __init__(self, generator):

        # get site generate object
        self.generator = generator

        # vars
        self.blog_conf = {
            "blog_page_path" : "blog",
            "tag_page_path" : "blog/tag",
            "tag_template" : "blog/tag.html.jinja",
            "archive_page_path" : "blog/archive",
            "archive_template" : "blog/archive.html.jinja",
            "posts_per_page" : 10
        }

        # attempt to override vars with site_conf
        if "blog" in self.generator.site_conf:
            self.blog_conf = dict(self.blog_conf.items() + self.generator.site_conf['blog'].items())

        # get all blog posts
        self.posts = self.generator.get_site_pages("blog")

        self.get_blog_posts()

    def get_jinja_filters(self):
        return {}

    def get_jinja_functions(self):
        return {
            'tags' : self.get_tags,
            'archive_dates' : self.get_archive_dates,
            "blog_conf" : self.get_blog_conf,
            "posts" : self.get_blog_posts,
            "get_posts" : self.get_blog_posts
        }

    def get_dynamic_pages(self):

        """ Returns list of tag and archive pages for blog. """

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

    def get_tags(self):

        """  Get list of tags used in blog posts """

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

    def get_archive_dates(self):

        """ Get list of dates that reference months with archieved posts """

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

    def get_blog_conf(self):

        """ Get current blog config, exposes it to jinja template. """

        return self.blog_conf

    def get_blog_posts(self, limit = None, offset = 0, month_timestamp=None, tagged=""):

        """ Get all blog posts sorted by date """

        # get limit if not set
        if not limit: limit = self.blog_conf['posts_per_page']

        # need dateutil
        import dateutil.parser

        def blog_post_sort(page):
            page_info = self.generator.load_page(page)
            if "post_date" in page_info:
                return int( time.mktime( time.strptime( str(dateutil.parser.parse(page_info['post_date'])), "%Y-%m-%d %H:%M:%S") ) )
            return 0
   
        # if month given remove all posts that don't fall into date range
        if month_timestamp:
            sorted_posts = []
            for post in self.posts:
                page_info = self.generator.load_page(post)
                if not "post_date" in page_info: 
                    continue

                # get start of month
                year = time.strftime("%Y", time.gmtime(month_timestamp))
                month = time.strftime("%m", time.gmtime(month_timestamp))
                month_start = time.mktime( time.strptime("%s/%s" % (month, year), "%m/%Y") )

                # get end of month
                month = int(month) + 1
                if month > 12: 
                    month = 1
                    year = int(year) + 1
                month_end = time.mktime( time.strptime("%s/%s" % (month, year), "%m/%Y") )
                

                # get unix timestamp
                unix_time = int( time.mktime( time.strptime( str(dateutil.parser.parse(page_info['post_date'])), "%Y-%m-%d %H:%M:%S") ) )

                # if it falls between month_start and month_end append to posts
                if unix_time > month_start and unix_time < month_end:
                    sorted_posts.append(post)
        else:
            sorted_posts = self.posts

        # if tag given remove all posts that don't have that tag
        if tagged:
            posts = sorted_posts
            sorted_posts = []
            for post in posts:
                page_info = self.generator.load_page(post)
                if not "tag" in page_info or not tagged in page_info["tag"]: continue
                sorted_posts.append(post)


        # sort post by date
        sorted_posts = sorted(
            sorted_posts,
            key=blog_post_sort
        )

        # reverse sort
        sorted_posts.reverse()

        # no limit set
        if limit <= 0:
            return sorted_posts

        # limit and offset set
        elif limit > 0 and offset > 0:
            return sorted_posts[offset:(offset + limit)]

        # just limit set
        elif limit > 0:
            return sorted_posts[0:limit]
