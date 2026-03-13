import { app } from 'electron';
console.log('app:', typeof app);
console.log('versions:', process.versions.electron);
app.quit();
