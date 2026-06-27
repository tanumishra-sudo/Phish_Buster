const express = require('express');
const router = express.Router();
const predictionController = require('../controllers/predictionController');
const { validateURL } = require('../middleware/validation');

// Single URL prediction
router.post('/predict', validateURL, predictionController.predictPhishing);

// Batch URL prediction
router.post('/predict-batch', predictionController.predictBatch);   

// Get prediction history (optional)
router.get('/history', predictionController.getHistory);

module.exports = router;