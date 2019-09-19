const webpack = require('webpack');
const path = require('path');

const {DuplicatesPlugin} = require("inspectpack/plugin");


module.exports = {
    entry: {
        // This allows for multiple React "apps", for different pages
        trend: './src/trend.js'
    },
    module: {
        rules: [
            {
                test: /\.(js|jsx)$/,
                exclude: /node_modules/,
                use: [
                    {
                        options: {
                            presets: ['@babel/preset-env', '@babel/preset-react'],
                            plugins: ['@babel/plugin-proposal-object-rest-spread']
                        },
                        loader: 'babel-loader'
                    }
                ]
            }
        ]
    },
    resolve: {
        alias: {
            react: path.resolve('./node_modules/react'),
        },
        extensions: ['*', '.js', '.jsx']
    },
    output: {
        path: __dirname + '/megaqc/static/js',
        publicPath: '/',
        filename: '[name].js'
    },
    plugins: [
    ],
    devServer: {
        contentBase: './dist',
        hot: true
    },
    devtool: "source-map"
};
