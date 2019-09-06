var path = require("path"),
    webpack = require("webpack"),
    BundleTracker = require("webpack-bundle-tracker");


  module.exports = {
    mode: 'development',
    context: __dirname,
    entry: "./gem/static/js/index",
    output: {
      path: path.resolve('./gem/static/js/bundles'),
      filename: "[name]-[hash].js"
    },
    plugins: [
      new BundleTracker({filename: "webpack-stats.json"})
    ],
    module: {
      rules: [
        {
          test: /\.js$/,
          exclude: /node_modules/,
          use: ['babel-loader']
        }
      ]
    },
    resolve: {
      extensions: ['*', '.js', '.jsx']
    }
  };
