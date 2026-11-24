import { readFile } from 'node:fs/promises';
import { chain, read } from '../scripts/runtime.mjs';
import { getter } from '../scripts/scenario.mjs';
await chain();
const deployment = JSON.parse(await readFile(new URL('../deployment.json', import.meta.url)));
const id = BigInt(process.argv[2] ?? '0');
console.log(JSON.stringify(await read(deployment.address, getter, [id]), null, 2));
