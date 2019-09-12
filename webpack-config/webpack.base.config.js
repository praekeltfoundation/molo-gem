const path = require("path"),
      webpack = require("webpack"),
      BundleTracker = require("webpack-bundle-tracker");

  module.exports = {
    context: __dirname,
    entry: "../gem/static/js/entries/index.js",
    output: {
      path: path.resolve("./gem/static/js/dest/dev"),
      filename: "[name]-[hash].js"
    },
    mode: 'development',
    plugins: [
      new BundleTracker({filename: './gem/webpack-stats.json'})
    ],
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: ["babel-loader"]
        }
      ]
    },
    resolve: {
      extensions: ["*",".js", ".jsx"]
    }
  };
