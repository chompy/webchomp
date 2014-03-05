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

import os, shutil, urlparse, imp, itertools, fnmatch, math
from PIL import Image

class asset_filter:

    """ Asset filter for generating spritesheets. """

    def __init__(self, asset_processor):
        self.asset_processor = asset_processor

    def get_filters(self):
        return {
            "image_spritesheet" : self.spritesheet
        }

    def spritesheet(self, filename, args={}, relative_path = True):

        # arg defaults
        arg_defaults = {
            'cell_width' : 24,
            'cell_height' : 24,
            'max_cols' : 10,
            'padding' : 1,
            'output_format' : 'png'
        }

        # merge arg_defaults with args
        args = dict(arg_defaults.items() + args.items())

        # set constraints
        # max_cols <=0 means unlimited cols
        if int(args['max_cols']) <= 0:
            args['max_cols'] = 99999

        # output already exists
        if os.path.exists( 
            self.asset_processor.prepare_output("%s_sprite_%sx%s.%s" % (
                os.path.splitext(filename)[0], 
                int(args['cell_width']), 
                int(args['cell_height']), 
                args['output_format']
            ))
        ):
            return self.asset_processor.get_output_path("%s_sprite_%sx%s.%s" % (
                os.path.splitext(filename)[0], 
                int(args['cell_width']), 
                int(args['cell_height']), 
                args['output_format']
            ))

        # get path
        path = self.asset_processor.asset_exists(filename)
        if not path: return ""
        
        # path must be directory
        if not os.path.isdir(path): return ""

        # get images for spritesheet
        images = []
        for root, dirnames, filenames in os.walk(path):
            for imgfilename in filenames:
                if not imgfilename.endswith(('.jpg', '.jpeg', '.gif', '.png', '.tif', '.tga')):
                    continue
                image = Image.open("%s/%s" % (path, imgfilename))
                if image: 
                    image.thumbnail((int(args['cell_width']), int(args['cell_height'])), Image.BICUBIC)
                    images.append(image)

        # calculate grid size
        grid = [0,0]
        if (len(images) <= int(args['max_cols'])):
            grid = [len(images), 1]
        else:
            grid = [int(args['max_cols']), len(images) / int(args['max_cols'])]

        # create spritesheet
        spritesheet = Image.new(
            mode='RGBA',
            size=(grid[0] * (int(args['cell_width']) + int(args['padding'])), grid[1] * (int(args['cell_height']) + int(args['padding']))),
            color=(0,0,0,0)
        )

        # iterate images, paste them in
        for count, image in enumerate(images):
            spritesheet.paste(
                image,
                (
                    int((count % grid[0]) * (int(args['cell_width']) + int(args['padding']))),
                    int(math.floor(count / grid[0]) * (int(args['cell_height']) + int(args['padding'])))
                )
            )

        # save output
        spritesheet.save(self.asset_processor.prepare_output("%s_sprite_%sx%s.%s" % (
            os.path.splitext(filename)[0], 
            int(args['cell_width']), 
            int(args['cell_height']), 
            args['output_format']
        )))


        return self.asset_processor.get_output_path("%s_sprite_%sx%s.%s" % (
            os.path.splitext(filename)[0], 
            int(args['cell_width']), 
            int(args['cell_height']), 
            args['output_format']
        ))