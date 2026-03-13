import { spawn } from 'child_process';

console.log('Parent ELECTRON_RUN_AS_NODE:', process.env.ELECTRON_RUN_AS_NODE);

const child = spawn('node', ['-e', 'console.log("Child ELECTRON_RUN_AS_NODE:", process.env.ELECTRON_RUN_AS_NODE)'], {
  env: { ...process.env, ELECTRON_RUN_AS_NODE: '0' }
});

child.stdout.on('data', (data) => console.log(data.toString()));
child.stderr.on('data', (data) => console.error(data.toString()));
