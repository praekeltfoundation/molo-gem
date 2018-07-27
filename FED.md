FED

  Maintenance, Performance, and Readability.
  We use SMACSS and BEM methodologies

  BEM introduction (for HTML MARKUP FILES)
  https://en.bem.info/methodology/quick-start/
  http://getbem.com/introduction/

  BEM Naming Convention Example
    Languages
    Language__current
    Language__title
    Language__title--icon
    Language__dropdown-button

    Language__list
    Language-list__toggle
    Language-list__item

  SMACSS (For SASS / CSS FILES)
  https://smacss.com/book/

  E.G. variables / colors.scss
  $springster-sunny-yellow                :           #FFFC78;
  $mint-green                             :           #a4eed2;
  $sunny-yellow                           :           #fffc80;

  $color-gray             :     color(greyscale, gray-chateau);
  $color-gray-light       :     color(greyscale, gray-light);

FILES DIRECTORY / STRUCTURE
  Folder / files path: /styles/app-name/
    /layout/
      _l-header.scss
      _l-footer.scss
    /modules
      _m-article-list.scss
      _m-article.scss
    /state
      _s-article-list.scss
      _s-article.scss
    /variables
      variables.scss
      color.scss
    _base.scss
    _versions.scss
    styles-rtl.scss
    e.g. ninyampings.scss | @import all compoments folders e.g. @import "util/*";

  Output file path: /static/css/dev
                      with sourcemaps /maps
                    /static/css/prd

CLI: COMPRESSION AUTOMATION + LINTING
  --------------------------------
  - Gulp enforce SASS, JS syntax rules

  Requirements:
  Must have node.js, npm and gulp installed globally
  https://docs.npmjs.com/cli/install
  https://gulpjs.org/getting-started

  Node version: Use Recommended for most users version - https://nodejs.org/en/

  - npm install gulp-cli -g

  Asset bundling & processing, concatenating and minification scripts are:
  - gulpfile.js
  - package.json

  Commands:
  - npm install
  - npm shrinkwrap
  - gulp OR gulp --type=ci

  IMAGES FORMATS:
    SVG, PNG, Sprites icons
    Images must be compressed
