// frontend/webpack.config.js
const path = require("path");
const MiniCssExtractPlugin = require("mini-css-extract-plugin");
const CssMinimizerPlugin = require("css-minimizer-webpack-plugin");
const { CleanWebpackPlugin } = require("clean-webpack-plugin");

const OUTPUT_DIR = path.resolve(__dirname, "../backend/static-frontend/client");

module.exports = {
  mode: "production",            // "development" for local testing
  entry: "./src/index.tsx",
  output: {
    filename: "js/arro.js",      // predictable name (no hashes)
    path: OUTPUT_DIR,
    publicPath: "/static/client/", // MUST match Django’s static URL + subdir
  },
  resolve: {
    extensions: [".ts", ".tsx", ".js", ".jsx"],
  },
  module: {
    rules: [
      { test: /\.[jt]sx?$/, exclude: /node_modules/, use: "babel-loader" },
      {
        test: /\.css$/i,
        use: [MiniCssExtractPlugin.loader, "css-loader"],
      },
      // images/fonts/etc. → predictable output under client/assets
      {
        test: /\.(png|jpe?g|gif|svg|woff2?|ttf|eot)$/i,
        type: "asset/resource",
        generator: {
          filename: "assets/[name][ext]", // no hash; Django will hash on collect
        },
      },
    ],
  },
  plugins: [
    new CleanWebpackPlugin(), // cleans OUTPUT_DIR on each build
    new MiniCssExtractPlugin({
      filename: "css/arro.css",    // predictable CSS name
      chunkFilename: "css/[name].css",
    }),
  ],
  optimization: {
    splitChunks: false,            // single JS file (optional, keeps it simple)
    runtimeChunk: false,
    minimizer: [
      `...`,                       // keep Terser
      new CssMinimizerPlugin(),
    ],
  },
  devtool: false,
};