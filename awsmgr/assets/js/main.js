/*
 * Main Javascript file for awsmgr.
 *
 * This file bundles all of your javascript together using webpack.
 */

// JavaScript modules
require('@fortawesome/fontawesome-free');
require('jquery');
require('bootstrap');
// require('preact');
require('react');
require('react-dom');
require('htm');

require.context(
  '../img', // context folder
  true, // include subdirectories
  /.*/, // RegExp
);

// Your own code
require('./version');
require('./plugins');
require('./script');
