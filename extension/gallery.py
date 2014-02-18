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

import urlparse

"""
    Tag extension, added a gallery tag that supports images and youtube videos
"""
class tag_extension:

    def __init__(self, generator):
        self.generator = generator

    def get_tags(self):
        return {
            'gallery' : self.gallery_tag
        }

    # get youtube id from url
    def _youtube_id(self, value):
        query = urlparse.urlparse(value)
        if query.hostname == 'youtu.be':
            return query.path[1:]
        if query.hostname in ('www.youtube.com', 'youtube.com'):
            if query.path == '/watch':
                p = urlparse.parse_qs(query.query)
                return p['v'][0]
            if query.path[:7] == '/embed/':
                return query.path.split('/')[2]
            if query.path[:3] == '/v/':
                return query.path.split('/')[2]
        # fail?
        return None

    """ Creates a gallery from definition in current page info. """
    def gallery_tag(self, gallery):

        # get page info
        page_info = self.generator.current_page_info

        # make sure tag properties exist
        if not "_tags" in page_info: return "[TAG: GALLERY (Tag attributes not found.)]"
        if not "gallery" in page_info['_tags']: return "[TAG: GALLERY (Tag attributes not found.)]"
        if not gallery in page_info['_tags']['gallery']: return "[TAG: GALLERY (Tag attributes not found.)]"

        # generate gallery html
        gallery_html = ""
        for item in page_info['_tags']['gallery'][gallery]:
            
            # make sure url provided
            if not 'url' in item: continue

            # get title
            title = item['name'] if 'name' in item else ""

            # get url
            url = item['url']

            # process asset
            image_src = ""

            # youtube link
            if item['type'].lower() == "youtube":
                youtube_id = self._youtube_id(url)
                image_src = "http://img.youtube.com/vi/%s/0.jpg" % youtube_id

            # assume image asset if nothing else specified
            else:
                item['type'] = "image"
                if "asset" in self.generator.jinja_functions and "add" in self.generator.jinja_functions['asset']:
                    url = self.generator.jinja_functions['asset']['add'](url)
                if "asset" in self.generator.jinja_functions and "image" in self.generator.jinja_functions['asset']:                    
                    image_src = self.generator.jinja_functions['asset']['image'](url, {'w' : 256})
                    

            # make html
            gallery_html += "<div class='gallery-item gallery-%s'><a href='%s'><img src='%s' alt='%s' title='%s' /></a></div>" % (item['type'].lower(), url, image_src, title, title)


        return gallery_html + "<div class='clear'></div>"