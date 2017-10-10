'use strict';

var gulp              =   require('gulp'),
    sass              =   require('gulp-sass'),
    watch             =   require('gulp-watch'),
    cleanCSSMinify    =   require('gulp-clean-css'),
    rename            =   require('gulp-rename'),
    gzip              =   require('gulp-gzip'),
    notify            =   require('gulp-notify'),
    sourcemaps        =   require('gulp-sourcemaps'),
    livereload        =   require('gulp-livereload'),
    minify            =   require('gulp-minify');

var sassPaths = [
    'gem/styles/gem/base_style.scss',
    'gem/styles/gem/base_style-rtl.scss',
    'gem/styles/gem-malawi/malawi.scss',

    'gem/styles/versions.scss',

    'gem/styles/gem-springster/springster.scss',
    'gem/styles/gem-springster/springster-rtl.scss',
    'gem/styles/gem-springster/state/state_320.scss',
    'gem/styles/gem-springster/state/state_smart.scss',
    'gem/styles/gem-springster/state/state.scss',
    'gem/styles/gem-springster/state/no-script-state.scss',
];
var sassDest = {
     prd: 'gem/static/css/prd',
     dev: 'gem/static/css/dev'
};
function styles(env) {
  var s = gulp.src(sassPaths);
  var isDev = env === 'dev';
  if (isDev) s = s
    .pipe(sourcemaps.init());
    s = s
    .pipe(sass().on('error', sass.logError))
    .pipe(cleanCSSMinify())
    if (isDev) s = s
        .pipe(sourcemaps.write('/maps'));
        return s
        .pipe(gulp.dest(sassDest[env]))
        .pipe(notify({ message: `Styles task complete: ${env}` }));
}

gulp.task('styles:prd', function() {
  return styles('prd');
});
gulp.task('styles:dev', function() {
  return styles('dev');
});

//Wagtail Admin CSS override - must be on root static
gulp.task('stylesAdmin', function() {
  gulp.src('gem/styles/wagtail-admin.scss')
      .pipe(sass().on('error', sass.logError))
      .pipe(cleanCSSMinify())
      .pipe(gulp.dest('gem/static/css/'))
      .pipe(notify({ message: 'Styles task complete: Wagtail Admin' }));
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
    gulp.watch(['gem/client/css/**/*.scss', 'gem/styles/**/*.scss',' gem/static/js/springster.js'], ['styles']);
});

gulp.task('styles', ['styles:dev', 'styles:prd','stylesAdmin']);
gulp.task('default', ['styles','compress']);
