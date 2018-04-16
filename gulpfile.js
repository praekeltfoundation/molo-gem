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
    sassPaths = [
        'gem/styles/gem/base_style.scss',
        'gem/styles/gem/base_style-rtl.scss',
        'gem/styles/gem-malawi/malawi.scss',
        'gem/styles/maintenance.scss',

        'gem/styles/gem-springster/01_springster.s+(a|c)ss',
        'gem/styles/gem-springster/02_springster-rtl.s+(a|c)ss',
        'gem/styles/gem-springster/03_state.s+(a|c)ss',
        'gem/styles/gem-springster/04_state-320.s+(a|c)ss',
        'gem/styles/gem-springster/05_no-script-state.s+(a|c)ss',
        'gem/styles/gem-springster/@font-face-baton.s+(a|c)ss'
    ],
    sassDest = {
         prd: 'gem/static/css/prd',
         dev: 'gem/static/css/dev'
    };


function styles(env) {
  var s = gulp.src(sassPaths);
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
    .pipe(gulp.dest(sassDest[env]));
}
gulp.task('styles:prd', function() {
  return styles('prd');
});
gulp.task('styles:dev', function() {
  return styles('dev');
});

// Minify JS
gulp.task('compress', function() {
  gulp.src('gem/static/js/springster.js')
    .pipe(minify({
        ext:{
            min:'-min.js'
        },
        noSource:[],
    }))
    .pipe(gulp.dest('gem/static/js/'))
});


gulp.task('watch', function() {
    livereload.listen();
    gulp.watch(['gem/styles/**/*.scss',' gem/static/js/springster.js'], ['styles']);
});

gulp.task('styles', ['styles:dev', 'styles:prd']);
gulp.task('default', ['styles', 'compress']);
