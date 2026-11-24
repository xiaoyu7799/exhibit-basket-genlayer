# Exhibit Basket

An exhibition editor locks ranked artwork candidates for each editorial slot.
A consumer needs a complete, machine-readable image package whose selections
follow this order and the museum's published reuse policy. GenLayer checks
each candidate independently and the contract issues a manifest only after
every slot can be filled.

## Contract

Stable Studionet (61999), RPC `https://studio.genlayer.com/api`,
`genlayer-js@2.0.0`, deployment [manifest](deployment.json).

1. An editor calls `propose(label, ranked_slots_json)`. One to three slots
   each contain one to three Met object IDs, in priority order. IDs are unique
   across the edition. The contract fixes the editor and order.
2. Anyone may `resolve(edition)`. The leader and validators retrieve the Met's
   official collection API objects and agree exactly on normalized object ID,
   eligibility reason and eligible image URL. A changed flag or image from
   the leader fails independent equality. An HTTP 404 records `NOT_FOUND`
   and evaluation continues. Rate limits, server outages and network failures
   leave the edition proposed and retryable.
3. The contract selects the first suitable image in each slot. An edition with
   all slots filled becomes `PUBLISHED`; `get_edition(id)` returns the complete
   manifest in slot order. If any slot lacks a suitable image, the edition
   becomes `BLOCKED` with an empty manifest and the candidate reasons. The
   editor can start a new edition. Both outcomes are terminal.

A suitable image requires the museum's `isPublicDomain=true` flag and its
official HTTPS image host. An object with a missing, empty or
unofficial image records `NO_OFFICIAL_IMAGE` and can be replaced. The decision records the museum's metadata at
resolution time. It provides neither a rights opinion in every jurisdiction
nor a guarantee that URLs remain available.

## Reproduce

```sh
npm ci
npm test
python -m pip install genvm-linter==0.11.0
genvm-lint check contracts/exhibit_basket.py --json
node scripts/lint-deployed.mjs
node examples/usage.mjs 0
node examples/usage.mjs 1
npm run verify
```

The isolated unit tests use a controlled SDK stand-in. The live scenario
uses real Studionet wallets: editor proposes two editions, two independent
callers resolve them, and a repeat resolution is rejected. Edition 0 skips missing object 9999999 and object 490002 without an official image,
selects 436535 and fills the second slot with 459055. Edition 1 has only
9999999 and is blocked without a manifest.

For a new deployment, use a separate checkout and remove the generated
`evidence/live.json` in that checkout before running `node scripts/deploy.mjs`
and `npm run live`. Retain the journal while a transaction is pending so the
runner resumes the same hash. The runner uses disposable Studionet signers
and the network's test faucet. Never use a mainnet key.

See [live receipts and readbacks](evidence/live.json) and
[official lint on deployed bytes](evidence/lint-deployed.json).

See [independent receipt and state verification](evidence/verification.json).

[Original deployment and receipts](evidence/archive/4d901fe5/) remain available.
