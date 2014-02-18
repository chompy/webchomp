WebChomp Changelog
===================
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