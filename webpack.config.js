'use strict';
const path = require("path"),
      webpack = require("webpack"),
      merge = require("webpack-merge"),
      BundleTracker = require("webpack-bundle-tracker");

  const baseConfig = merge([
    {
      context: __dirname,
      entry: "./gem/static/js/entries/index.js",
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
    }
  ]);



  const developmentConfig = merge([
    {
      output: {
        path: path.resolve("./gem/static/js/dest/dev"),
        filename: "[name]-[hash].js"
      },
      plugins: [
        new BundleTracker({filename: './gem/webpack-stats.json'})
      ]
    }
  ]);


  const productionConfig = merge([
    {
      output: {
        path: path.resolve("./gem/static/js/dest/prod"),
        filename: "[name]-[hash].js"
      },
      plugins: [
        new BundleTracker({filename: "./gem/webpack-stats-prod.json"}),
        new webpack.DefinePlugin({
          'process.env': {
            'NODE_ENV': JSON.stringify('production')
          }
        }),
        new webpack.optimize.OccurrenceOrderPlugin()
      ]
    }
  ]);


  module.exports = (mode) => {
    if (mode === "development") {
      return merge(baseConfig, developmentConfig, { mode });
    }
    return merge(baseConfig, productionConfig, { mode });
  };
