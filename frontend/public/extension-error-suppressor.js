// Suppress browser extension errors that pollute the console
// These errors come from extensions like ad blockers, password managers, etc.
// and are not part of our application

(function() {
  const originalError = console.error;
  console.error = function(...args) {
    // Filter out common extension errors
    const errorString = args.join(' ');
    
    // Skip errors from browser extensions
    if (errorString.includes('contentScript.js') || 
        errorString.includes('chrome-extension://') ||
        errorString.includes('moz-extension://') ||
        errorString.includes('safari-extension://')) {
      return; // Suppress the error
    }
    
    // Log all other errors normally
    originalError.apply(console, args);
  };
})();