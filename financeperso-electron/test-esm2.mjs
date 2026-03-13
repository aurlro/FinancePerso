import pkg from 'electron';
console.log('pkg:', typeof pkg, pkg);
const { app } = pkg;
console.log('app:', typeof app);
