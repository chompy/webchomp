# WebChomp v0.03

** About WebChomp **

WebChomp is a tool to that generates a complete static website from YAML, Jinja, and SCSS files. The goal of WebChomp is to build a system that would allow one to make a site that contains regularly updated content without the need for a dynamic server side solution.

Planned features include...

- Automatic push to Amazon S3.
- Cronjob support, self updating content.
- GUI for creating and editing pages.

** Dependencies **

- Python 2.7.x (http://www.python.org/)
- PyScss (https://github.com/Kronuz/pyScss/)
- Cssutils (http://cthedot.de/cssutils/)
- PyYaml (http://pyyaml.org/)
- Jinja2 (http://jinja.pocoo.org/)
- Python-Markdown (http://packages.python.org/Markdown/)
- python-dateutil (http://labix.org/python-dateutil)
- Boto (https://github.com/boto/boto)
- PIL (Python Imaging Library) (http://www.pythonware.com/products/pil)

** Running WebChomp **

WebChomp currently runs from the command line. The syntax is as follows...

    python webchomp.py [-h] <site_name> <action_to_perform> --page PAGE
    
TODO: List all available actions

** Building A Site **

TODO: Info on creating site directory, creating yaml pages files, etc etc