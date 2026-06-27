const { PythonShell } = require('python-shell');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
  
// Store prediction history in memory (or use database)
let predictionHistory = [];

/**
 * Single URL Prediction
 */
exports.predictPhishing = async (req, res) => {
  try {
    const { url } = req.body;

    console.log(`[PREDICT] Analyzing URL: ${url}`);

    // Call Python ML script
    const prediction = await runPythonPrediction(url);

    // Store in history
    const historyEntry = {
      id: generateId(),
      url: url,
      prediction: prediction,
      timestamp: new Date().toISOString()
    };
    predictionHistory.push(historyEntry);

    // Keep only last 100 entries
    if (predictionHistory.length > 100) {
      predictionHistory = predictionHistory.slice(-100);
    }

    console.log(`[PREDICT] Result: ${prediction.prediction} (${prediction.confidence}%)`);

    return res.json({
      success: true,
      url: url,
      prediction: prediction.prediction,
      confidence: prediction.confidence,
      features: prediction.features,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('[PREDICT] Error:', error);
    return res.status(500).json({
      error: 'Prediction failed',
      message: error.message || 'Failed to process the URL'
    });
  }
};

/**
 * Batch URL Prediction
 */
exports.predictBatch = async (req, res) => {
  try {
    const { urls } = req.body;

    if (!Array.isArray(urls) || urls.length === 0) {
      return res.status(400).json({
        error: 'Invalid input',
        message: 'Please provide an array of URLs'
      });
    }

    console.log(`[BATCH] Processing ${urls.length} URLs`);

    const results = [];

    for (const url of urls) {
      try {
        const prediction = await runPythonPrediction(url);
        results.push({
          url: url,
          prediction: prediction.prediction,
          confidence: prediction.confidence,
          success: true
        });
      } catch (error) {
        results.push({
          url: url,
          success: false,
          error: error.message
        });
      }
    }

    console.log(`[BATCH] Completed processing ${urls.length} URLs`);

    return res.json({
      success: true,
      total: urls.length,
      results: results,
      timestamp: new Date().toISOString()
    });

  } catch (error) {
    console.error('[BATCH] Error:', error);
    return res.status(500).json({
      error: 'Batch processing failed',
      message: error.message
    });
  }
};

/**
 * Get Prediction History
 */
exports.getHistory = async (req, res) => {
  try {
    const limit = req.query.limit || 50;
    const history = predictionHistory.slice(-limit);

    return res.json({
      success: true,
      count: history.length,
      data: history
    });

  } catch (error) {
    console.error('[HISTORY] Error:', error);
    return res.status(500).json({
      error: 'Failed to retrieve history',
      message: error.message
    });
  }
};

/**
 * Run Python Prediction Script
//  */
// async function runPythonPrediction(url) {
//   return new Promise((resolve, reject) => {
//     const pythonScriptPath = path.join(__dirname, '../../ml_model/predict.py');

//     // Check if script exists
//     if (!fs.existsSync(pythonScriptPath)) {
//       reject(new Error(`Python script not found at ${pythonScriptPath}`));
//       return;
//     }

//     const options = {
//       mode: 'text',
//       pythonPath: process.env.PYTHON_PATH || 'python3',
//       scriptPath: path.dirname(pythonScriptPath),
//       args: [url],
//       timeout: 30000 // 30 second timeout
//     };

//     PythonShell.run('predict.py', options, function (err, results) {
//       if (err) {
//         console.error('[PYTHON] Error:', err);
//         reject(new Error(`Python execution error: ${err.message}`));
//         return;
//       }

//       if (!results || results.length === 0) {
//         reject(new Error('No response from Python script'));
//         return;
//       }

//       try {
//         const prediction = JSON.parse(results[0]);
        
//         // Validate response
//         if (!prediction.prediction || prediction.confidence === undefined) {
//           reject(new Error('Invalid prediction response format'));
//           return;
//         }

//         resolve(prediction);
//       } catch (parseErr) {
//         console.error('[PARSE] Error:', parseErr);
//         reject(new Error(`Failed to parse Python response: ${parseErr.message}`));
//       }
//     });
//   });
// }

// async function runPythonPrediction(url) {
//   return new Promise((resolve, reject) => {
//     const pythonScriptPath = path.join(__dirname, '../../ml_model/predict.py');

//     console.log('[DEBUG] Python script path:', pythonScriptPath);
//     console.log('[DEBUG] Script exists:', fs.existsSync(pythonScriptPath));

//     // Check if script exists
//     if (!fs.existsSync(pythonScriptPath)) {
//       reject(new Error(`Python script not found at ${pythonScriptPath}`));
//       return;
//     }

//     const pythonPath = process.env.PYTHON_PATH || 'python';
    
//     const options = {
//       mode: 'text',
//       pythonPath: pythonPath,
//       scriptPath: path.dirname(pythonScriptPath),
//       args: [url],
//       timeout: 30000 // 30 second timeout
//     };

//     console.log('[DEBUG] Python Path:', pythonPath);
//     console.log('[DEBUG] Script Path:', options.scriptPath);
//     console.log('[DEBUG] Args:', options.args);

//     PythonShell.run('predict.py', options, function (err, results) {
//       console.log('[DEBUG] Python callback fired');
//       console.log('[DEBUG] Error:', err);
//       console.log('[DEBUG] Results:', results);

//       if (err) {
//         console.error('[PYTHON] Error:', err);
//         reject(new Error(`Python execution error: ${err.message}`));
//         return;
//       }

//       if (!results || results.length === 0) {
//         reject(new Error('No response from Python script'));
//         return;
//       }

//       try {
//         console.log('[DEBUG] Parsing result:', results[0]);
//         const prediction = JSON.parse(results[0]);
        
//         // Validate response
//         if (!prediction.prediction || prediction.confidence === undefined) {
//           reject(new Error('Invalid prediction response format'));
//           return;
//         }

//         console.log('[DEBUG] Success:', prediction);
//         resolve(prediction);
//       } catch (parseErr) {
//         console.error('[PARSE] Error:', parseErr);
//         reject(new Error(`Failed to parse Python response: ${parseErr.message}`));
//       }
//     });
//   });
// }

// async function runPythonPrediction(url) {
//   return new Promise((resolve, reject) => {
//     const pythonScriptPath = path.join(__dirname, '../../ml_model/predict.py');

//     console.log('[DEBUG] Python script path:', pythonScriptPath);
//     console.log('[DEBUG] Script exists:', fs.existsSync(pythonScriptPath));

//     if (!fs.existsSync(pythonScriptPath)) {
//       reject(new Error(`Python script not found at ${pythonScriptPath}`));
//       return;
//     }

//     const pythonPath = process.env.PYTHON_PATH || 'python';
    
//     const options = {
//       mode: 'text',
//       pythonPath: pythonPath,
//       scriptPath: path.dirname(pythonScriptPath),
//       args: [url],
//       timeout: 10000, // 10 second timeout
//       env: { PYTHONUNBUFFERED: '1' }
//     };

//     console.log('[DEBUG] Python Path:', pythonPath);
//     console.log('[DEBUG] Script Path:', options.scriptPath);
//     console.log('[DEBUG] Args:', options.args);

//     let callbackFired = false;
//     let timeoutHandle;

//     const safeReject = (error) => {
//       if (!callbackFired) {
//         callbackFired = true;
//         if (timeoutHandle) clearTimeout(timeoutHandle);
//         console.error('[ERROR] Rejecting:', error.message);
//         reject(error);
//       }
//     };

//     const safeResolve = (result) => {
//       if (!callbackFired) {
//         callbackFired = true;
//         if (timeoutHandle) clearTimeout(timeoutHandle);
//         console.log('[SUCCESS] Resolving:', result);
//         resolve(result);
//       }
//     };

//     // Manual timeout
//     timeoutHandle = setTimeout(() => {
//       safeReject(new Error('Python script timeout - no response after 10 seconds'));
//     }, 10000);

//     try {
//       console.log('[DEBUG] About to run Python...');
      
//       PythonShell.run('predict.py', options, function (err, results) {
//         console.log('[DEBUG] Python callback fired');
//         console.log('[DEBUG] Error:', err);
//         console.log('[DEBUG] Results:', results);

//         if (err) {
//           console.error('[PYTHON ERROR]:', err);
//           safeReject(new Error(`Python execution error: ${err.message}`));
//           return;
//         }

//         if (!results || results.length === 0) {
//           console.error('[NO RESULTS] Empty response');
//           safeReject(new Error('No response from Python script'));
//           return;
//         }

//         try {
//           console.log('[DEBUG] Parsing result:', results[0]);
//           const prediction = JSON.parse(results[0]);
          
//           if (!prediction.prediction || prediction.confidence === undefined) {
//             safeReject(new Error('Invalid prediction response format'));
//             return;
//           }

//           console.log('[DEBUG] Parsed successfully:', prediction);
//           safeResolve(prediction);
//         } catch (parseErr) {
//           console.error('[PARSE ERROR]:', parseErr);
//           safeReject(new Error(`Failed to parse Python response: ${parseErr.message}`));
//         }
//       });
//     } catch (execErr) {
//       console.error('[EXEC ERROR]:', execErr);
//       safeReject(new Error(`Failed to execute Python: ${execErr.message}`));
//     }
//   });
// }


async function runPythonPrediction(url) {
  return new Promise((resolve, reject) => {
    const pythonScriptPath = path.join(__dirname, '../../ml_model/predict.py');
    const pythonPath = process.env.PYTHON_PATH || 'python';
    const scriptDir = path.dirname(pythonScriptPath);

    console.log('[DEBUG] Using child_process');
    console.log('[DEBUG] Python:', pythonPath);
    console.log('[DEBUG] Script:', pythonScriptPath);
    console.log('[DEBUG] URL:', url);

    const pythonProcess = spawn(pythonPath, [pythonScriptPath, url], {
      cwd: scriptDir,
      stdio: ['pipe', 'pipe', 'pipe']
    });

    let output = '';
    let errorOutput = '';

    pythonProcess.stdout.on('data', (data) => {
      console.log('[STDOUT]:', data.toString());
      output += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      console.log('[STDERR]:', data.toString());
      errorOutput += data.toString();
    });

    pythonProcess.on('close', (code) => {
      console.log('[DEBUG] Python process closed with code:', code);

      if (code !== 0) {
        console.error('[PYTHON ERROR] Exit code:', code);
        console.error('[STDERR]:', errorOutput);
        reject(new Error(`Python failed with code ${code}: ${errorOutput}`));
        return;
      }

      if (!output) {
        console.error('[ERROR] No output from Python');
        reject(new Error('No output from Python script'));
        return;
      }

      try {
        console.log('[DEBUG] Parsing output:', output.trim());
        const prediction = JSON.parse(output.trim());
        
        if (!prediction.prediction || prediction.confidence === undefined) {
          reject(new Error('Invalid prediction response format'));
          return;
        }

        console.log('[SUCCESS]:', prediction.prediction, prediction.confidence + '%');
        resolve(prediction);
      } catch (err) {
        console.error('[PARSE ERROR]:', err.message);
        console.error('[RAW OUTPUT]:', output);
        reject(new Error(`Failed to parse response: ${err.message}`));
      }
    });

    pythonProcess.on('error', (err) => {
      console.error('[PROCESS ERROR]:', err.message);
      reject(new Error(`Failed to start Python: ${err.message}`));
    });

    // Timeout after 15 seconds
    setTimeout(() => {
      pythonProcess.kill();
      reject(new Error('Python script timeout'));
    }, 15000);
  });
}
/**
 * Generate unique ID
 */
function generateId() {
  return 'pred_' + Date.now() + '_' + Math.random().toString(36).substr(2, 9);
}