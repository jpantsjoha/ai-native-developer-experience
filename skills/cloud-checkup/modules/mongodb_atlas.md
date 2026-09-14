# Data-store module: MongoDB Atlas

Two jobs, kept separate. **Assess** is what the weekly checkup runs: read-only, fills rows
10 to 14 of the report. **Maintain** is the retention and index routine that the assessment
justifies, run deliberately and never from the checkup.

Connect through the driver or the MongoDB MCP server. The connection string is read from
the env var named in the manifest (`connection_env`); its value never enters the probes
file, the report, or a log line.

## Assess (read-only, every checkup)

### 1. Database census

`dbStats` for the whole database: collections, objects, data size, storage size, index
count, total index size. Record all six; the growth between two checkups is the signal, not
the absolute number. A database that is 90% one collection tells you where every later
question belongs.

Then `collStats` per collection: document count, data MB, storage MB, index MB, index
count. Sort by data size and report the top few plus anything that moved.

### 2. Freshness

For each entry in the store's `freshness[]`, take `$max` of the named field and compare
against `max_age_hours`. Report the age in hours, not a verdict word.

Three traps, all of which have produced a green row over a dead pipeline:

- **The writer runs and writes nothing.** Process liveness is not evidence of writes. A
  scheduled job can hold its pid for weeks while its work silently fails. Freshness of the
  data is the only proof, and it belongs in the same row as the job's pid.
- **A TTL index plus a dead writer empties the collection on a known date.** When a
  collection is both stale and TTL-covered, compute the date the last document expires and
  put that date in the finding. That converts "stale" into a deadline.
- **Null sorts before dates and strings in BSON.** A single null-timestamped document
  reports as the collection's oldest and hides where the corpus really starts. Exclude
  explicitly: `{field: {$exists: true, $ne: null}}`.

### 3. Timestamp types

Count documents by BSON type on the date field the retention policy would use:

```
{field: {$type: "string"}} · {field: {$type: "date"}} · {field: {$exists: false}}
```

A collection with both string and date timestamps cannot be range-queried correctly, and a
retention routine that stamps `now + retention` onto the undated ones restarts the clock on
documents of unknown age. Report the split. Unparseable is a count, never a guess.

### 4. Indexes

Per collection: the index list, which index leads with the tenant key, and which carries
`expireAfterSeconds`. Two findings this reliably produces:

- **A tenant-filtered collection with no index leading on the tenant key.** Every read is a
  collection scan, masked entirely while there is one tenant. It stops being invisible at
  the second one. The fix is a compound index leading on the tenant key with the common
  sort field second, so "this tenant, most recent first" is index-covered.
- **A large collection with no TTL index at all**, accumulating with no retention.

`$indexStats` gives ops per index and, in `accesses.since`, the counter's start.
**Always report the window length alongside the ops count.** The counters reset on every
step-down and restart, so the window is usually days. A zero-ops index in a four-day window
is not an unused index: a monthly or quarterly job would not appear in it. **Nothing is
ever dropped on that evidence.**

### 5. Tenant stamping

For each tenant-scoped collection, count `{tenant_key: {$exists: false}}`. Report the
count, the date range of the unstamped documents, and whether the gap is historical (a
migration cutover) or ongoing (a write path that does not stamp).

The asymmetry that makes a green isolation suite meaningless: a suite typically tests that
**reads filter**, and nothing tests that **writes stamp**. A write path that omits the key
and a read path that requires it both pass their own tests, and between them the collection
returns nothing for anybody. Check both directions.

### 6. Backup

Backup policy and last snapshot are not visible over the driver. Say so and mark the row
INCONCLUSIVE with the specific remedy (the provider console, or an Admin API key), rather
than scoring it green. Add the question that matters more than the policy: has a restore
ever been demonstrated?

## Maintain (mutating, deliberate, never from the checkup)

Four subcommands, one routine, in this order. `assess` and `plan` are strictly read-only;
`apply` refuses without an explicit confirmation flag; `rollback` undoes exactly one
generation of stamps.

```
assess    read-only census (the section above, as a written artefact)
plan      read-only: exactly what apply would do, with per-rule matched counts
apply     backup, then create indexes, then stamp expiry. Requires --yes.
rollback  unset the stamps this tool wrote, by policy version
```

### Six invariants

1. **Shorten only, never lengthen.** A rule may pull an expiry in; it may never push one
   out. Lengthening resurrects data an earlier and stricter policy had already condemned.
2. **Measure from the document's own timestamp, never from the run clock.** That makes
   re-running idempotent and stops any document having its clock restarted.
3. **No `deleteMany`, ever.** Stamp `ttl_expires_at` and stop; expiry is the TTL monitor's
   job. It spreads the deletes across its sweep instead of one long-running destructive
   command, and it leaves a rollback window while the stamps age in. Assert this in a test
   against the source, not in a comment.
4. **Version every stamp.** Write a `ttl_policy_version` alongside the expiry, so rollback
   removes exactly what this generation wrote and leaves an earlier backfill untouched.
   Bump the version whenever a retention number changes.
5. **Back up before apply.** Run the dump first and record its path in the plan artefact.
   An opt-out flag may exist; the default is that it runs.
6. **Skip what you cannot parse.** A document with a missing or unparseable date field is
   counted and left alone. Stamping it `now + retention` would restart the clock on a
   document of unknown age.

Rules must be **exhaustive and disjoint**: the catch-all rule is an `$nin` over the
enumerated categories, so a category nobody enumerated lands on the longest tier rather
than falling through a gap. A regression test asserts every value present in production
matches exactly one rule.

Indexes are created idempotently, in the background. **Nothing is ever dropped**, for the
`$indexStats` window reason above.

### The reader survey, before shortening anything

**Never set a retention number from the size of the collection. Set it from its readers.**

Before shortening any tier, enumerate every code path that reads the collection. Use a call
graph or an exhaustive grep, then read each query filter by hand, and record for each
reader: what it depends on, and whether its query is time-bounded or unbounded. The output
is a table of reader, dependency, and bound.

The number that governs is the longest **bounded** consumer, with headroom. Every
**unbounded** reader is a separate finding, because no finite retention is strictly
lossless while one exists: the routine cannot prove the shortened window is safe, only that
it clears the bounded ceiling. Say that in the artefact rather than implying proof.

Two things the survey usually surfaces, and both belong to the operator rather than the
routine:

- **The surgical cut is often by a quality field, not by category.** If most of the mass is
  low-value rows distinguishable by a field the readers already ignore, cutting on that
  field reclaims the same space and leaves every judgement-bearing record intact. That is a
  policy change: it needs an operator decision and a policy-version bump.
- **A parallel local record is not a fallback** unless a reader actually reads it. Two
  record sets that are dual-written and compared are parallel, not tiered. Check whether
  anything reads the fallback before calling it one.

Also confirm, once, whether a downstream mirror (a warehouse connector, a change stream)
propagates deletes. Expiry that silently does not reach the mirror is a different data set,
not an archive.

### Where the numbers live

The policy table appears in exactly three places and they change together: the routine's
source, its runbook, and the data-platform design doc. Two of the three agreeing is drift,
not agreement.

---

## Worked example (a live multi-tenant trading platform, 2026-09-04)

*This block is the only project-specific content in this skill. It exists as a reference
implementation. **Do not copy its numbers as defaults**: its retention values were derived
from its own reader survey and mean nothing for another project.*

- Implementation: one maintenance script with `assess / plan / apply / rollback`
  subcommands, tiered retention plus required indexes.
- Runbook, including the full reader-survey table and its verdict, kept beside the script.
- Tests: a unit suite over the script, including the
  source-level assertion that the script contains no delete call, and the assertion that
  every production action value matches exactly one policy rule.
- What the assessment found there: one collection at 96% of the database, of which 97.3%
  were low-value scan records; 10.5% TTL coverage, so retention was indefinite by omission
  rather than by decision; and a fully tenant-filtered collection with six indexes, none of
  them leading on the tenant key.
- What the reader survey changed: the proposed retention for the low-value tier was raised
  substantially before apply, because a regression ground-truth set read the corpus
  unbounded and its calibration depended on corpus depth. The size argument would have cut
  it; the reader argument set it.
