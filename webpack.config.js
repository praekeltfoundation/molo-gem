'use strict';

const environment = (process.env.NODE_ENV || 'development').trim();

if (environment === 'development') {
  module.exports = require('./webpack-config/webpack.base.config');
} else {
  module.exports = require('./webpack-config/webpack.prod.config');
}
