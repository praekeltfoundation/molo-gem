const path = require("path"),
      webpack = require("webpack"),
      BundleTracker = require("webpack-bundle-tracker"),
      config = require("./webpack.base.config.js");

config.entry = [
  'webpack-dev-server/client?http://localhost:3000',
  'webpack/hot/only-dev-server',
  './gem/static/js/reactComponents/index'
];

// override django's STATIC_URL for webpack bundles
config.output.publicPath = 'http://localhost:3000/assets/js/bundles/'

// Add HotModuleReplacementPlugin and BundleTracker plugins
config.plugins = config.plugins.concat([
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoErrorsPlugin(),
  new BundleTracker({filename: './webpack-stats.json'})
]);

module.exports = config
