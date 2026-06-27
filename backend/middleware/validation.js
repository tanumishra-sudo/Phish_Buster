/**
 * URL Validation Middleware
 */
const validateURL = (req, res, next) => {
  try {
    const { url } = req.body;   

    // Check if URL is provided
    if (!url) {
      return res.status(400).json({
        error: 'Invalid input',
        message: 'URL is required'
      });
    }

    // Check if URL is string
    if (typeof url !== 'string') {
      return res.status(400).json({
        error: 'Invalid input',
        message: 'URL must be a string'
      });
    }

    // Trim whitespace
    req.body.url = url.trim();

    // Check if URL is not empty
    if (req.body.url.length === 0) {
      return res.status(400).json({
        error: 'Invalid input',
        message: 'URL cannot be empty'
      });
    }

    // Add protocol if missing
    if (!req.body.url.startsWith('http://') && !req.body.url.startsWith('https://')) {
      req.body.url = 'https://' + req.body.url;
    }

    // Validate URL format
    try {
      new URL(req.body.url);
    } catch (error) {
      return res.status(400).json({
        error: 'Invalid URL',
        message: 'Please provide a valid URL format'
      });
    }

    // Check URL length (prevent DoS)
    if (req.body.url.length > 2048) {
      return res.status(400).json({
        error: 'Invalid input',
        message: 'URL is too long (max 2048 characters)'
      });
    }

    next();
  } catch (error) {
    return res.status(500).json({
      error: 'Validation error',
      message: error.message
    });
  }
};

module.exports = { validateURL };