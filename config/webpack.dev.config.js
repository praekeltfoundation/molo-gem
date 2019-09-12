const path = require("path"),
      webpack = require("webpack"),
      BundleTracker = require("webpack-bundle-tracker"),
      config = require("./webpack.base.config.js");

  config.plugins = config.plugins.concat([new BundleTracker({filename: './webpack-stats.json'})])
module.exports = config
