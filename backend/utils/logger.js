const fs = require('fs');
const path = require('path');

const logDir = path.join(__dirname, '../logs');

// Create logs directory if it doesn't exist
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir);
}

class Logger {   
  constructor() {
    this.logFile = path.join(logDir, `phishguard-${new Date().toISOString().split('T')[0]}.log`);
  }

  log(level, message, data = {}) {
    const timestamp = new Date().toISOString();
    const logMessage = `[${timestamp}] [${level}] ${message}`;
    const fullLog = data && Object.keys(data).length > 0 
      ? `${logMessage} ${JSON.stringify(data)}` 
      : logMessage;

    console.log(fullLog);

    // Write to file
    fs.appendFileSync(this.logFile, fullLog + '\n', 'utf8');
  }

  info(message, data) {
    this.log('INFO', message, data);
  }

  error(message, data) {
    this.log('ERROR', message, data);
  }

  warn(message, data) {
    this.log('WARN', message, data);
  }

  debug(message, data) {
    if (process.env.NODE_ENV === 'development') {
      this.log('DEBUG', message, data);
    }
  }
}

module.exports = new Logger();