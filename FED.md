FED Workflow
------------------

### HTML Template Approach
  We use BEM methodologies / naming convention

  [Introduction to BEM](http://getbem.com/introduction/)

  [Methodology Quick Start](https://en.bem.info/methodology/quick-start/)


### e.g. Languages block
  ```
    <div class="languages">
      <h2 class="language__title">Language block</h2>
      <ul class="language-list">
        <li class="language-list__item">
          <a href="#" class="language-list__anchor">English</a>
        </li>
        <li class="language-list__item">
          <a href="#" class="language-list__anchor">Xhosa</a>
        </li>
      </ul>
    </div>
  ```

### CSS Styles Approach
  We write CSS styles using SCSS extension for rich CSS features.

  SCSS is compiled using [gulp.js](https://gulpjs.com/) tast runner workflow and or [Webpack](webpack.js) bundler workflow.

  We use SMACSS methodologies / CSS structure and naming convention.
  [SMACCS Cookbook](  https://smacss.com/book/)

  Application CSS Folder:
  ```
    /static/css/sass/app-name/
      /layout/
        _l-header.scss
        _l-footer.scss
      /modules
        _m-article-list.scss
        _m-article.scss
      /state
        _s-article-list.scss
        _s-article.scss
      /utils
        variables.scss
        color.scss
      _base.scss
      _versions.scss
      styles-rtl.scss
  ```


#### Gulp.js CSS Output:

  /static/css/dest/dev/filename.css
    /maps/filename.css
  /static/css/dest/prd/filename.css



Gulp.js / Webpack.js: AUTOMATION & LINTING
----------------------------------------
  Requirements:
  * Must have [Node.js](https://nodejs.org/en/), npm installed globally
  * Must have gulp.js installed globally ie. `npm install gulp-cli -g`

  * Make sure the following files are available:
    * NPM file = package.json
    * Entry file = gulpfile.js

  On your CLI, cd to the project.
  run the following commands:
  * npm install
  * npm shrinkwrap
  * gulp --type=ci


  * Make sure the following files are available:
    * Webpack.js Config file = webpack.config.js
    * Babel config = .babelrc

#### Gulp.js JS Output:
  /static/js/dest/filename.js

#### Webpack.js JS Output:
  /static/js/dest/dev/filename.js
  /static/js/dest/prd/filename.js
