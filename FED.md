FED

  Maintenance, Performance, and Readability.

  MARKUP & CSS
  ---------------
  -  We use SMACSS, BEM methodologies

  BEM
  https://en.bem.info/methodology/quick-start/
  http://getbem.com/introduction/

  BEM Naming Convention
    Languages
    Language__current
    Language__title
    Language__title--icon
    Language__dropdown-button

    Language__list
    Language-list__toggle
    Language-list__item

  SMACSS
  https://smacss.com/book/

  E.G. variables / colors.scss
    $de_york - #2A9B58;
    $robin_egg_blue - #37BFBE;
    $mandy - #EC3B3A;
    $danube - #5F7AC9;
    $roman - #EF9955;
    $saffron - #F2B438;
    $medium_violet - #B62A99;

  FILE PATH: /styles/app-name/
    /layout/
      _l-header.scss
      _l-footer.scss
      _l-layout.scss | @import all layout compoments
    /modules
      _m-article-list.scss
      _m-article.scss
      _m-modules.scss | @import all modules compoments
    /state
      _s-article-list.scss
      _s-article.scss
      _s-state.scss | @import all state compoments
    /variables
      variables.scss
      color.scss
    _base.scss
    _versions.scss
    styles.scss | @import all compoments
    styles-rtl.scss

  OUTPUT FILE PATH: /static/css/dev with sourcemaps /maps
                    /static/css/prd


  CSS / BEM Linting
  https://github.com/postcss/postcss-bem-linter
  - Enforce coding standard rules


  COMPRESSION / AUTOMATION
  -------------------------
  Requirements:
  Must have node.js npm and gulp installed globally

  - npm install gulp-cli -g

  For asset bundling & processing, concatenating and minification file:
  - gulpfile.js
  - package.json

  Commands:
  - npm install
  - gulp

  IMAGES FORMATS:
    SVG, PNG, Sprites icons
    Images must be compressed

  PAGE HEADING IMAGE
  {plugin-name}--call-to-action
    identity-image
    identity-image--{modifier}


BUTTON VARIANTS
  Single link and button text with primary style
  ```{% url "forgot_password" as link %}
    {% trans "Forgot PIN" as buttontext %}
    {% include "patterns/basics/buttons/sp_variations/button.html" with type="secondary" hyperlink=link text=buttontext %}```

  Multiple links, button text and extra string with secondary style
  ```{% trans "Log in to Enter" as buttontext %}
    {% url "molo.profiles:auth_login" as link1 %}
    {% url "molo.yourwords:competition_entry" competition.slug as link2 %}
    {% include "patterns/basics/buttons/sp_variations/button.html" with type="secondary" hyperlink=link1|add:"?next="|add:link2 text=buttontext %}}```

  Input Button and button text with primary style
    ``{% trans "Submit Your Story" as buttontext %}
    {% include "patterns/basics/buttons/sp_variations/button.html" with type="primary" text=buttontext %}``

HEADING TO BE ADDED
