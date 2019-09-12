const path = require("path"),
      webpack = require("webpack"),
      BundleTracker = require("webpack-bundle-tracker");

  module.exports = {
    context: __dirname,
    entry: "/Users/mitsoqalaba/Sites/WWW/PROJECTS/MOLO/molo-gem/gem/static/js/index.js",
    output: {
      path: path.resolve("../gem/static/js/bundles"),
      filename: "[name]-[hash].js"
    },
    plugins: [
      new BundleTracker({filename: './webpack-stats.json'})
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
      modules: ["./gem/static/js/bundles"],
      extensions: ["*",".js", ".jsx"]
    }
  };
