'use strict';

var gulp              =   require('gulp'),
  glob              =   require('glob'),
  sass              =   require('gulp-sass'),
  sassLint          =   require('gulp-sass-lint'),
  sassGlob          =   require('gulp-sass-glob'),
  cleanCSSMinify    =   require('gulp-clean-css'),
  autoprefixer      =   require('gulp-autoprefixer'),
  bless             =   require('gulp-bless'),
  watch             =   require('gulp-watch'),
  rename            =   require('gulp-rename'),
  gzip              =   require('gulp-gzip'),
  notify            =   require('gulp-notify'),
  sourcemaps        =   require('gulp-sourcemaps'),
  livereload        =   require('gulp-livereload'),
  minify            =   require('gulp-minify'),
  pixrem            =   require('gulp-pixrem'),
  svgmin            =   require('gulp-svgmin'),
  del               =   require('del'),
  gutil             =   require('gulp-util'),
  uglify            =   require('gulp-uglify');


  var stylesDir       =  "gem/static/css/sass/";
  var sassPaths =  [
    'gem/base_style.scss',
    'gem/base_style-rtl.scss',
    'gem-malawi/malawi.scss',
    'gem-ninyampinga/nn.scss',
    'gem-ninyampinga/enhanced-nn.scss',
    'gem-ninyampinga/browsers/nn-safari.scss',
    'gem-yegna/yegna.scss',
    'gem-chhaajaa/chhaajaa.scss',
    'gem-tanzania/tanzania.scss',
    'maintenance.scss',
    'gem-springster/01_springster.s+(a|c)ss',
    'gem-springster/02_springster-rtl.s+(a|c)ss',
    'gem-springster/03_state.s+(a|c)ss',
    'gem-springster/04_state-320.s+(a|c)ss',
    'gem-springster/05_no-script-state.s+(a|c)ss',
    'gem-springster/@font-face-baton.s+(a|c)ss',
  ];
  var authSassPaths = [
    'auth-service/style.feature.scss',
    'auth-service/style.enhanced.scss',
    'gem-springster/auth/springster.feature.scss',
    'gem-springster/auth/springster.enhanced.scss',
    'gem-malawi/auth/zathu.feature.scss',
    'gem-malawi/auth/zathu.enhanced.scss',
    'gem-ninyampinga/auth/ninyampinga.feature.scss',
    'gem-ninyampinga/auth/ninyampinga.enhanced.scss',
    'gem-yegna/auth/yegna.feature.scss',
    'gem-yegna/auth/yegna.enhanced.scss',
    'gem-chhaajaa/auth/chhaajaa.enhanced.scss',
    'gem-chhaajaa/auth/chhaajaa.feature.scss',
    'gem-tanzania/auth/tanzania.feature.scss',
    'gem-tanzania/auth/tanzania.enhanced.scss'
  ];

  var sassDest = {
    prd: 'gem/static/css/dest/prd',
    dev: 'gem/static/css/dest/dev',
  },
  authSassDest = {
    auth: stylesDir + '/dest/auth-compiled'
  };


  for(var i = 0; i < sassPaths.length || i < authSassPaths.length; i++){
    if (sassPaths[i]) {
      sassPaths[i] = stylesDir + sassPaths[i];
    }
    if(authSassPaths[i]) {
      authSassPaths[i] = stylesDir + authSassPaths[i];
    }
  }

  function styles(env) {
    var s = gulp.src(env === 'auth' ? authSassPaths : sassPaths);
    var isDev = env === 'dev';
    if (isDev)
      s = s
          .pipe(sourcemaps.init());
      s = s
      .pipe(sassGlob())
      .pipe(sass().on('error', sass.logError))
      .pipe(bless())
      .pipe(cleanCSSMinify())
      .pipe(pixrem());
      if (isDev)
      s = s
      .pipe(sourcemaps.write('/maps'));
      return s
      .pipe(gutil.env.type !== 'ci' ? notify({ message: `Styles task complete: ${env}` }) : gutil.noop())
      .pipe(gulp.dest(env === 'auth' ? authSassDest[env] : sassDest[env]));
  }
  gulp.task('styles:prd', function() {
    return styles('prd');
  });
  gulp.task('styles:dev', function() {
    return styles('dev');
  });
  gulp.task('styles:auth', function() {
    return styles('auth');
  });

  // Minify JS
  gulp.task('compress', function() {
    return gulp.src([
        'gem/static/js/gulp-entries/main.js',
        'gem/static/js/gulp-entries/springster.js',
        'gem/static/js/gulp-entries/nn.js',
        'gem/static/js/gulp-entries/yegna.js',
        'gem/static/js/gulp-entries/kaios.js',
        'gem/static/js/modeladmin/index.js'
      ]).pipe(rename({
        suffix: "-min",
        extname: ".js"
      }))
      .pipe(uglify())
      .on('error', function (err) { gutil.log(gutil.colors.red('[Error]'), err.toString()); })
      .pipe(gulp.dest('gem/static/js/dest'))
  });


  gulp.task('styles', gulp.series('styles:dev','styles:prd','styles:auth'));
  gulp.task('default', gulp.series('styles','compress'));
