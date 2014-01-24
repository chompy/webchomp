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