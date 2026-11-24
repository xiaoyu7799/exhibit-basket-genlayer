import assert from 'node:assert/strict';
import { readFile, writeFile } from 'node:fs/promises';
import { encode, read, verifyRun } from './runtime.mjs';
import { check, getter } from './scenario.mjs';
const { log, verified } = await verifyRun();
const states = await Promise.all([0, 1].map(id => read(log.address, getter, [BigInt(id)])));
check(...states);
assert.deepEqual(states, [log.snapshots.normal, log.snapshots.exception]);
const errors = getter === 'get_edition'
  ? {'reject-replay':'EDITION_CLOSED'}
  : {'reject-wrong-delegate':'NOT_DISTRICT_DELEGATE',
     'reject-duplicate-claim':'NOT_CLAIMABLE',
     'reject-invalid-round-claim':'ROUND_NOT_ALLOCATED'};
for (const [tag, expected] of Object.entries(errors)) {
  assert.equal(verified.find(tx => tx.tag === tag)?.contractError, expected, tag);
}
const lint = JSON.parse(await readFile('evidence/lint-deployed.json'));
assert.equal(lint.address,log.address);
assert.equal(lint.deployedSourceSha256,log.sourceSha256);
assert.equal(lint.localSourceSha256,log.sourceSha256);
assert.equal(lint.exitCode,0);
assert(lint.output.lint.ok && lint.output.validate.ok);
await writeFile('evidence/verification.json',encode({
  verifiedAt:new Date().toISOString(),chainId:61999,address:log.address,
  sourceSha256:log.sourceSha256,sourceMatches:true,transactions:verified,
  normal:states[0],exception:states[1],
})+'\n');
console.log('Verified both finalized business outcomes and exact rejection reasons.');
