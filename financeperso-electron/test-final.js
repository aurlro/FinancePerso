const electron = require('electron');
console.log('Type:', typeof electron);
console.log('Is string:', typeof electron === 'string');
console.log('Keys:', Object.keys(electron).slice(0, 5));

// Essaie de trouver les bindings autrement
console.log('process.versions:', Object.keys(process.versions));
