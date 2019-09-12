const path = require("path"),
      webpack = require("webpack"),
      UglifyJsPlugin = require('uglifyjs-webpack-plugin');

  module.exports = {
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
    devtool: 'inline-source-map',
    devServer: {
      contentBase: path.join(__dirname, './gem/static/js/bundles'),
      compress: true,
      hot: true,
      port: 9000
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
    },
    mode: 'development'
  };
