const path = require("path"),
      webpack = require("webpack"),
      BundleTracker = require("webpack-bundle-tracker"),
      UglifyJsPlugin = require('uglifyjs-webpack-plugin');

  module.exports = {
    mode: 'development',
    context: __dirname,
    entry: "./gem/static/js/reactComponents/index",
    output: {
      path: path.resolve('./gem/static/js/bundles'),
      filename: "[name]-[hash].js"
    },
    plugins: [],
    module: {
      rules: [
        {
          test: /\.(js|jsx)$/,
          exclude: /node_modules/,
          use: ["babel-loader"]
        }
      ]
    },
    optimization: {
      minimizer: [
        new UglifyJsPlugin({
          sourceMap: true,
          uglifyOptions: {
            compress: false,
            ecma: 6,
            mangle: true
          }
        })
      ]
    },
    resolve: {
      modules: ['node_modules'],
      extensions: ['.js', '.jsx']
    }
  };
