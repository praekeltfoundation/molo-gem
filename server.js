var webpack = require('webpack'),
    WebpackDevServer = require('webpack-dev-server'),
    config = require('./webpack.base.config.js');

new WebpackDevServer(webpack(config), {
  publicPath: config.output.publicPath,
  hot: true,
  inline: true,
  historyApiFallback: true
}).listen(3000, '127.0.0.1', function(err, result) {
  if(err) {
    consolge.log(err)
  }
  console.log('Listening at 127.0.0.1:3000');
});
