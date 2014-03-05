WebChomp Changelog
===================
** 0.11 **
- SCSS extension now pipes found CSS URLs to asset filter system.
- Asset extension now uses filter system on markdown links/images.
- Fixed SCSS compiler extension compiling all SCSS twice.

** 0.10 **
- Added filter system to asset extension. Filters can be added to process assets prior to output.
- Time extension timetostr now uses local time.
- Added 'image' and 'iframe' tags to tag extension.
- Various bug fixes.

** 0.09 **
- Asset extension checks for assets in more places, as well as places defined in site.yml.

** 0.08 **
- Added doc2page extension. Uses Abiword to convert DOCs to HTML and injects it into page.

** 0.07 **
- Added logging through Python's logging module
- Added optional yml file, webchomp.yml, allows configuration of logging and pathes.

** 0.06 **
- Added _import internal component. Allows one to specify a page to import all contents.

** 0.05 **
- Added tag extension whose purpose is the allow the addition of custom tags to page YAML files.
- Added gallery tag extension.

** 0.04 **
- Added new argument processing system, action processing is a bit more robust and works like the extension system.
- Asset management system, assets no longer get outputted by the generator until they are referenced in a template or page.
- Image resize function added: f.asset.image(FILENAME, {'w': WIDTH, 'h': HEIGHT}).

** 0.03 **
- S3SYNC (Amazon S3 Sync) action added.

** 0.02 **
- Jinja functions now load in to arrays related to their function. (i.e. to load a component it's f.component.load)

** 0.01 **
- Initial Version