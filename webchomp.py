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

import sys, os, fnmatch, yaml, shutil, time, imp, itertools, logging, logging.handlers

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

# config
config = {}

# parse webchomp.yml
if os.path.exists("webchomp.yml"):
    wcyml_io = open("webchomp.yml", "r")
    config = yaml.load(wcyml_io.read())
    wcyml_io.close()

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
            action_object = action_class.webchomp_action(site, config)
            for action in action_object.get_webchomp_actions():
                action_list[action] = action_object.get_webchomp_actions()[action]
            for argument in action_object.get_webchomp_arguments():
                argument_list[argument] = action_object.get_webchomp_arguments()[argument]

# print help
if not 'action' in arguments or not arguments['action'] in action_list:

    # get version number
    version_io = open("%s/VERSION" % os.path.dirname(__file__), "r")
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

    # set logging config
    logging_enabled = True
    log_console_level = "debug"
    log_file_level = "debug"
    if "logging" in config:
        if "enabled" in config['logging']:
            logging_enabled = config['logging']['enabled']
        if "log_level_display" in config['logging']:
            if "console" in config['logging']['log_level_display']:
                log_console_level = config['logging']['log_level_display']['console']
            if "file" in config['logging']['log_level_display']:
                log_file_level = config['logging']['log_level_display']['file']

    # create logging directory if not exist
    if not os.path.exists("log/"):
        os.mkdir("log")

    # configure logging
    if logging_enabled:
        logging.basicConfig(format='[%(asctime)s][%(levelname)s] %(message)s', level=logging.WARN)
        webchomp_logger = logging.getLogger('webchomp')
        webchomp_logger_filehandler = logging.handlers.RotatingFileHandler(
            "log/%s.log" % site,
            maxBytes=65536, # 64KB
            backupCount=5
        )
        webchomp_logger_filehandler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s] %(message)s'))
        webchomp_logger_filehandler.setLevel(getattr(logging, log_file_level.upper()))
        webchomp_logger.addHandler(webchomp_logger_filehandler)
        webchomp_logger.setLevel(getattr(logging, log_console_level.upper()))

        # log the action that is being executed
        webchomp_logger.info("Executing '%s' action on '%s' site" % (arguments['action'].upper(), site))
    else:
        webchomp_logger = logging.getLogger('webchomp')
        webchomp_logger.disabled = True

    # perform action
    action_list[arguments['action']](arguments)