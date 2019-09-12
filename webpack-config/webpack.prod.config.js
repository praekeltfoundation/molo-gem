const path = require("path"),
      webpack = require('webpack'),
      BundleTracker = require('webpack-bundle-tracker'),
      config = require('./webpack.base.config.js');

  config.output.path = require('path').resolve('../gem/static/js/dest/')

  config.plugins = config.plugins.concat([
    new BundleTracker({filename: '../gem/webpack-stats-prod.json'}),
    new webpack.DefinePlugin({
      'process.env': {
        'NODE_ENV': JSON.stringify('production')
      }
    }),
    new webpack.optimize.OccurrenceOrderPlugin()
  ])

module.exports = config
