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

    """ Jinja extension, provides useful time related functions and filters. """

    def __init__(self, generator):
        self.generator = generator

    def get_jinja_filters(self):
        return {
            'strtotime' : self.string_to_time,
            'timetostr' : self.time_to_string
        }

    def get_jinja_functions(self):
        return {
            'get_time' : time.time
        }

    def string_to_time(self, string):

        """ convert time/date in string to unix timestamp """

        import dateutil.parser
        return int( time.mktime( time.strptime( str(dateutil.parser.parse(string)), "%Y-%m-%d %H:%M:%S") ) )

    def time_to_string(self, unix_time, format = "%Y-%m-%d %H:%M:%S", tz_offset = 0):

        """ convert unix timestamp to string """

        return time.strftime(format, time.gmtime(unix_time + tz_offset))