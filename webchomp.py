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

import sys, os, fnmatch, yaml, shutil, time, imp, itertools, argparse

# process command line args
arguments = {}
key = ""
count = 0
for arg in sys.argv[1:]:
    # count +1
    count += 1

    # if we have a key then this arg is a value for the key
    if key:
        arguments[key] = arg
        key = ""
        continue
    # if '--' is first characters then it has a value for next arg
    elif arg[0:2] == "--":
        key = arg[2:]
        continue
    # '-' as first character overides action
    elif arg[0] == "-":
        arguments['action'] = arg[1:]
    # first iteration is SITE
    elif count == 1:
        arguments["site"] = arg
    # second iteration is PAGE
    elif count == 2:
        arguments['action'] = arg

# try to get current site
site = arguments['site'] if 'site' in arguments else ""

# get available actions and arugments
action_list = {}
argument_list = {}
for root, dirnames, filenames in itertools.chain( os.walk("app/") ):
    for filename in fnmatch.filter(filenames, '*.py'):
        action_class = imp.load_source(
            "action_%s" % os.path.splitext(filename)[0],
            os.path.join(root, filename)
        )
        if hasattr(action_class, 'webchomp_action'):
            action_object = action_class.webchomp_action(site)
            for action in action_object.get_webchomp_actions():
                action_list[action] = action_object.get_webchomp_actions()[action]
            for argument in action_object.get_webchomp_arguments():
                argument_list[argument] = action_object.get_webchomp_arguments()[argument]

# print help
if not 'action' in arguments or not arguments['action'] in action_list:

    # get version number
    version_io = open("VERSION", "r")
    version = version_io.read()
    version_io.close()

    # print help output
    print "WebChomp v%s -- Static Website generator." % version
    print "usage: python %s [-h] SITE ACTION" % sys.argv[0],

    arguments = []
    for action in argument_list:
        for arg in argument_list[action]:
            if not arg in arguments: arguments.append(arg)
    for argument in arguments:
        print "[--%s] " % argument,

# process action
else:
    action_list[arguments['action']](arguments)