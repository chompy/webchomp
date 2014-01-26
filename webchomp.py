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
    
# set up argparser
import argparse
parser = argparse.ArgumentParser(description='Webchomp v0.01 -- Static website generator.', prog="webchomp.py")
parser.add_argument('site', type=str, help='site to perform action on')
parser.add_argument('action', type=str, help='action to perform [generate]')
args = parser.parse_args()

# perform specified action

# GENERATE
if args.action == "generate":
	import app.generator
	site_generator = app.generator.webchomp_generator(args.site)
	site_generator.generate()