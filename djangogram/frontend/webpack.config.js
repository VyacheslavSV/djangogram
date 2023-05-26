const path = require('path')

module.exports = {
    entry: {
        main: './src/js/main.js',
        ajax: './src/js/ajax.js'
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, '../webapp/static/webapp/js')
    },
    module: {
        rules: [
            {
              test: /\.scss$/,
              use: [
                'style-loader',
                'css-loader',
                'sass-loader',
              ],
            },
            {
                test: /.js$/,
                exclude: /node_modules/,
                use: {
                    loader: "babel-loader"
                }
            }
        ]
    }
    }
