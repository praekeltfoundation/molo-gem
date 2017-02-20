'use strict';

var gulp              =   require('gulp'),
    sass              =   require('gulp-sass'),
    watch             =   require('gulp-watch'),
    cleanCSSMinify    =   require('gulp-clean-css'),
    rename            =   require('gulp-rename'),
    gzip              =   require('gulp-gzip'),
    notify            =   require('gulp-notify'),
    sourcemaps        =   require('gulp-sourcemaps'),
    livereload        =   require('gulp-livereload');

var sassPaths = [
    'gem/client/css/style.scss',
    'gem/client/css/style-rtl.scss',
    'gem/client/css/versions.scss',
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

gulp.task('watch', function() {
    livereload.listen();
    gulp.watch('gem/client/css/*.scss', ['styles']);
});

gulp.task('styles', ['styles:dev', 'styles:prd']);
gulp.task('default', ['styles','watch']);
