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
parser.add_argument('action', type=str, help='action to perform [generate, component, s3sync]')
parser.add_argument('--page', type=str, help='Perform action on single specified page')
parser.add_argument('--component-name', type=str, help='Set component name for component action.')
parser.add_argument('--component-value', type=str, help='Set component value for component action.')
args = parser.parse_args()

# perform specified action

# GENERATE
if args.action.lower() == "generate":
    import app.generator
    site_generator = app.generator.webchomp_generator(args.site)
    if not args.page:
        site_generator.generate()
    else:
        site_generator.generate_page(args.page)

# COMPONENT
elif args.action.lower() == "component":
    import app.generator, sys
    site_generator = app.generator.webchomp_generator(args.site)
    if not args.page:
        print "ERROR: Page name required to set component."
        sys.exit()
    if not args.component_name:
        print "ERROR: component name required to set component."
        sys.exit()

    site_generator.set_component(args.page, args.component_name, args.component_value)

# S3SYNC
elif args.action.lower() == "s3sync":
    import app.s3push, sys
    s3push = app.s3push.webchomp_s3push(args.site)
    if not args.page:
        s3push.sync()
    else:
        s3push.upload_file(args.page)