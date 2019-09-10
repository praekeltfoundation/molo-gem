FED Workflow
------------------

## HTML Template Approach
  We use BEM methodologies / naming convention
  [introduction to BEM](http://getbem.com/introduction/)
  [Methodology Quick Start](https://en.bem.info/methodology/quick-start/)


### Example: Languages block
  ```
    <div class="languages">
      <h2 class="language__title">Language block</h2>
      <ul class="language-list">
        <li class="language-list__item"></li>
        <li class="language-list__item"></li>
      </ul>
    </div>
  ```

## CSS Styles Approach
  We write CSS styles using SCSS extension for rich CSS features.
  SCSS is compiled using [gulp.js](https://gulpjs.com/) tast runner workflow and or [Webpack](webpack.js) bundler workflow

  We use SMACSS methodologies / CSS structure and naming convention
  [SMACCS Cookbook](  https://smacss.com/book/)

  Application CSS Folder: `/styles/app-name/`
    -/layout/
      _l-header.scss
      _l-footer.scss
    - /modules
      _m-article-list.scss
      _m-article.scss
    - /state
      _s-article-list.scss
      _s-article.scss
    - /utils
      variables.scss
      color.scss
    _base.scss
    _versions.scss
    styles-rtl.scss


  Output CSS Folder: `/static/css/dev/filename.css`
                                  /maps/filename.css
                    /static/css/prd/filename.css
                              /maps/filename.css



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
