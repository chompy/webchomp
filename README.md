WebChomp v0.09
==============
Created By Nathan Ogden

### About WebChomp ###

WebChomp is a tool to that generates a complete static website from YAML, Jinja, and SCSS files. The goal of WebChomp is to build a system that allows one to make a site that contains regularly updated content without the need for a dynamic server side solution.

WebChomp allows one to define pages on their site inside YAML files. A page YAML file contains a list of
key/values, known as a 'component', that can be accessed inside the page's respective Jinja template.

### License ###

WebChomp is released under GPL. See [LICENSE.txt](webchomp/LICENSE.txt) for full license.

### Changelog ###

See [CHANGELOG.md](webchomp/CHANGELOG.md).

### Dependencies ###

** Required **
- [Python 2.7](http://www.python.org/)
- [PyYaml](http://pyyaml.org/)
- [Jinja2](http://jinja.pocoo.org/)

** Optional **
- [Python-Markdown](http://packages.python.org/Markdown/) (For Markdown extension)
- [PyScss](https://github.com/Kronuz/pyScss/) (For SCSS compilation)
- [Cssutils](http://cthedot.de/cssutils/) (For parsing asset urls from SCSS files)
- [Boto](https://github.com/boto/boto) (For Amazon S3 Sync)
- [PIL (Python Imaging Library)](http://www.pythonware.com/products/pil) (For image resizing via Asset extension)
- [python-dateutil](http://labix.org/python-dateutil) (For Time extension)

### Usage ###

WebChomp currently runs from the command line. The syntax is as follows...

    python webchomp.py [-h] SITE ACTION --page PAGE
    
** Available Actions **
- **GENERATE**  : Generates static site, dumps to output/ directory.
- **S3SYNC**    : Uses S3 settings from 'site/[site-name]/site.yml' to upload output/ dir to S3.

The page argument can be passed to run the above commands on a single page in the given site.

### Getting Started ###

There is not currently any documentation. There is however a sample site included which shows 
off how to build a basic site with WebChomp.

** Sample site currently demostrates... **
- Loading components
- Loading SCSS file
- Getting URL of site pages
- Using markdown filter on content

** Things not yet demostrated... **
- Retrieving sub page list
- Loading components from other pages
- Pagination
- Asset loading
- Other stuff? Probably.