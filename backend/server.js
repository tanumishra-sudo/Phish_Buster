require('dotenv').config();
const express = require('express');
const cors = require('cors');
const path = require('path');
const helmet = require('helmet');
const rateLimit = require('express-rate-limit');
const bodyParser = require('body-parser');

// Import routes
const predictionRoutes = require('./routes/predictions');
const healthRoutes = require('./routes/health');

// Initialize Express app
const app = express();
const PORT = process.env.PORT || 5000;

// ============ Security Middleware ============
// Helmet helps secure Express apps by setting various HTTP headers
app.use(helmet());

// Body parser middleware
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ limit: '10mb', extended: true }));

// CORS configuration
const corsOptions = {
  origin: [
    'http://localhost:5000',
    'http://localhost:3000',
    'http://127.0.0.1:5000',
    'http://127.0.0.1:3000'
  ],
  credentials: true,
  methods: ['GET', 'POST', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization']
};
app.use(cors(corsOptions));

// Rate limiting middleware
const limiter = rateLimit({
  windowMs: parseInt(process.env.RATE_LIMIT_WINDOW_MS) || 900000, // 15 minutes
  max: parseInt(process.env.RATE_LIMIT_MAX_REQUESTS) || 100, // Limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true, // Return rate limit info in `RateLimit-*` headers
  legacyHeaders: false, // Disable `X-RateLimit-*` headers
});

app.use(limiter);

// ============ Logging Middleware ============
app.use((req, res, next) => {
  const timestamp = new Date().toISOString();
  console.log(`[${timestamp}] ${req.method} ${req.path}`);
  next();
});

// ============ Static Files ============
app.use(express.static(path.join(__dirname, '../frontend')));

// ============ Routes ============

// Health check endpoint
app.use('/health', healthRoutes);

// API endpoints
app.use('/api', predictionRoutes);

// ============ Root Endpoint ============
app.get('/', (req, res) => {
  res.json({
    message: '🛡️ PhishGuard - Phishing Detection API',
    version: '1.0.0',
    endpoints: {
      health: 'GET /health',
      predict: 'POST /api/predict',
      predict_batch: 'POST /api/predict-batch'
    },
    documentation: 'Available at /docs'
  });
});

// ============ 404 Handler ============
app.use((req, res) => {
  res.status(404).json({
    error: 'Not Found',
    message: `Cannot ${req.method} ${req.path}`,
    timestamp: new Date().toISOString()
  });
});

// ============ Error Handler ============
app.use((err, req, res, next) => {
  console.error('Error:', err);
  
  const status = err.status || 500;
  const message = err.message || 'Internal Server Error';
  
  res.status(status).json({
    error: {
      message: message,
      status: status,
      timestamp: new Date().toISOString()
    }
  });
});

// ============ Start Server ============
app.listen(PORT, () => {
  console.log('\n' + '='.repeat(60));
  console.log('🚀 PhishGuard Backend Server Started');
  console.log('='.repeat(60));
  console.log(`📍 Server running on http://localhost:${PORT}`);
  console.log(`🌐 Environment: ${process.env.NODE_ENV}`);
  console.log(`⚙️  Python Path: ${process.env.PYTHON_PATH}`);
  console.log('='.repeat(60) + '\n');
});

// ============ Graceful Shutdown ============
process.on('SIGTERM', () => {
  console.log('SIGTERM signal received: closing HTTP server');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('SIGINT signal received: closing HTTP server');
  process.exit(0);
});

module.exports = app;