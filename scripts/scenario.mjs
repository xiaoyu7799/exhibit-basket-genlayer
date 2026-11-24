import assert from 'node:assert/strict';
export const getter = 'get_edition';
export function check(normal, exception) {
  assert.equal(normal.state, 'PUBLISHED');
  assert.deepEqual(normal.manifest.map(item => item.id), [436535, 459055]);
  assert.equal(normal.evidence[0][0].reason, 'NOT_FOUND');
  assert.equal(normal.evidence[0][1].reason, 'NO_OFFICIAL_IMAGE');
  assert.equal(exception.state, 'BLOCKED');
  assert.deepEqual(exception.manifest, []);
  assert.equal(exception.evidence[0][0].reason, 'NOT_FOUND');
}
