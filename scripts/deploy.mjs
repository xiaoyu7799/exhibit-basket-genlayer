import { startRun, ensureDeployment } from './runtime.mjs';
const run = await startRun(3);
console.log(await ensureDeployment(run));
