# WebChomp v0.01

** About WebChomp **

WebChomp is a tool to that generates a complete static website from YAML, Jinja, and SCSS files. The goal of WebChomp is to build a system that would allow one to make a site that contains regularly updated content without the need for a dynamic server side solution.

Planned features include...

- Automatic push to Amazon S3.
- Cronjob support, self updating content.
- GUI for creating and editing pages.

** Dependencies **

- Python 2.7.x (http://www.python.org/)
- PyScss (https://github.com/Kronuz/pyScss/)
- PyYaml (http://pyyaml.org/)
- Jinja2 (http://jinja.pocoo.org/)
- Python-Markdown (http://packages.python.org/Markdown/)

** Running WebChomp **

WebChomp currently runs from the command line. The syntax is as follows...

    python webchomp.py [-h] <site_name> <action_to_perform>
    
The only action that can be performed in the current version is 'generate' which will build out the entire site and place the static files in the 'output' directory.

** Building A Site **

TODO: Info on creating site directory, creating yaml pages files, etc etc