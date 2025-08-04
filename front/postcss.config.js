export default {
  plugins: process.env.NODE_ENV === 'development' ? {
    // Skip autoprefixer in development - modern dev browsers don't need prefixes
  } : {
    autoprefixer: {
      overrideBrowserslist: [
        '> 1%',
        'last 2 versions',
        'not dead',
        'not ie 11',
        'not op_mini all',
        'chrome >= 87',
        'firefox >= 78',
        'safari >= 14',
        'edge >= 88',
        'ios >= 14'
      ]
    }
  }
}
