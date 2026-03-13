const { app } = require('electron');
console.log('app:', typeof app);
if (app) {
  console.log('SUCCESS!');
  app.quit();
} else {
  console.log('FAILED - app is undefined');
}
