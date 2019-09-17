'use strict';
const path = require("path"),
      webpack = require("webpack"),
      merge = require("webpack-merge"),
      glob = require("glob"),
      BundleTracker = require("webpack-bundle-tracker"),
      MiniCSSExtractPlugin = require("mini-css-extract-plugin");

  const baseConfig = merge([
    {
      context: __dirname,
      entry: {
        main: "./gem/static/js/entries/index.js",
        style: glob.sync('./gem/static/js/entries/styles/**/*.scss')
      },
      module: {
        rules: [
          {
            test: /\.(js|jsx)$/,
            exclude: /node_modules/,
            use: ["babel-loader"]
          },
          {
            test: /\.css$/,
            use: [
              MiniCSSExtractPlugin.loader,
              {
                loader: 'css-loader',
                options: {
                  sourceMap: true
                }
              }
            ]
          },
          {
            test: /\.scss$/,
            use: [
              MiniCSSExtractPlugin.loader,
              {
                loader: 'css-loader',
                options: {
                  sourceMap: true
                }
              },
              {
                loader: 'sass-loader',
                options: {
                  sourceMap: true
                }
              }
            ]
          }
        ]
      },
      plugins: [
        new MiniCSSExtractPlugin({filename: "./css/[name].css"})
      ],
      resolve: {
        extensions: ["*",".js", ".jsx","scss"]
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
