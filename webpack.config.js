const path = require('path');
const webpack = require('webpack');

/*
 * Webpack Plugins
 */
const MiniCssExtractPlugin = require('mini-css-extract-plugin');
const HookShellScriptPlugin = require('hook-shell-script-webpack-plugin');

const ProductionPlugins = [
  // production webpack plugins go here
  new webpack.DefinePlugin({
    "process.env": {
      NODE_ENV: JSON.stringify("production")
    }
  })
]

const debug = process.env.NODE_ENV === 'production' ? 'production' : 'development';
const rootAssetPath = path.join(__dirname, 'assets');

module.exports = {
  // configuration
  context: __dirname,
  entry: {
    main_js: './awsmgr/assets/js/main',
    main_css: [
      path.join(__dirname, 'node_modules', '@fortawesome', 'fontawesome-free', 'css', 'all.css'),
      path.join(__dirname, 'node_modules', 'bootstrap', 'dist', 'css', 'bootstrap.css'),
      path.join(__dirname, 'awsmgr', 'assets', 'css', 'style.css'),
    ],
  },
  mode: debug,
  output: {
    chunkFilename: "[id].js",
    filename: "[name].bundle.js",
    path: path.join(__dirname, "awsmgr", "app", "static", "build"),
    publicPath: "/static/build/"
  },
  resolve: {
    extensions: [".js", ".jsx", ".css"]
  },
  devtool: debug ? "eval-source-map" : false,
  plugins: [
    new MiniCssExtractPlugin({ filename: "[name].bundle.css" }),
    new webpack.ProvidePlugin({ $: "jquery", jQuery: "jquery" }),
    new HookShellScriptPlugin({
      // run a single command
      afterEmit: [
          '. $(poetry env info -p)/bin/activate && echo ">>>>RUNNING FLASK DIGEST COMPRESS COMMAND<<<<<"; FLASK_APP="awsmgr.app" flask digest compile; sleep 1; touch awsmgr/__init__.py',
      ],
      // run multiple commands in parallel
      // done: [
      //   // either as a string
      //   'echo "I HAVE NO IDEA WHAT I AM DOING HERE"',
      //   // or as a command with args
      //   // {command: 'echo', args: ['-e', 'HEEEEEEEEEEEEELP']}
      // ],
      // run a command based on the hook arguments
      // assetEmitted: [
      //   // you can return a string
      //   (name, info) => `node ${info.outputPath}`,
      //   // or an object with command and args
      //   (name, info) => ({command: 'node', args: [info.outputPath]})
      // ],
      // return a command and argrs object
    })

  ].concat(debug ? [] : ProductionPlugins),
  module: {
    rules: [
      {
        test: /\.less$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
            options: {
            },
          },
          'css-loader!less-loader',
        ],
      },
      {
        test: /\.css$/,
        use: [
          {
            loader: MiniCssExtractPlugin.loader,
            options: {
            },
          },
          'css-loader',
        ],
      },
      { test: /\.html$/, type: 'asset/source' },
      { test: /\.woff(2)?(\?v=[0-9]\.[0-9]\.[0-9])?$/, type: 'asset/resource', mimetype: 'application/font-woff' },
      {
        test: /\.(ttf|eot|svg|png|jpe?g|gif|ico)(\?.*)?$/i,
        type: 'asset/resource',
        generator: {
          filename: '[name][ext]'
        }
      },
      { test: /\.(js|jsx)$/, exclude: /node_modules/, loader: 'babel-loader', options: { presets: ["@babel/preset-env", "@babel/preset-react"], cacheDirectory: true } },
    ],
  }
};
