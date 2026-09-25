# Bugs

A bug is code whose behavior differs from what its callers, its tests, its documentation, or
its own name say it should do.

## How to find them

- Edge inputs the code does not handle: an empty collection, zero, a negative number, a missing
  or null value, a very long string, the first and last element of a range.
- Off-by-one errors in loops, slices, pagination, and date ranges; inclusive and exclusive
  bounds mixed up.
- Errors that are caught and dropped, or that turn into a default value the caller cannot tell
  apart from a real result.
- A resource opened on one path and not closed on another, especially an early return or an
  error path.
- Shared mutable state touched from more than one place without a clear owner: concurrent
  updates, a cache that is never invalidated, a default argument that is mutated.
- Comparisons that do not mean what they seem: identity versus equality, floating-point
  equality, string comparison of numbers, time zones and daylight saving time.
- A caller that relies on a return value, an ordering, or an exception the callee no longer
  provides.
- Anything that can lose or corrupt stored data: a partial write without a transaction, an
  overwrite without a check, a migration that drops a column still read elsewhere. Mark such
  an item as data destruction; it comes first in the fix order in `SKILL.md`, after any base
  item it depends on. If it is an ask item, it still waits with the other ask items.

## Pitfalls when fixing

- Fixing the symptom in one caller while the cause stays in the shared function, so other
  callers keep failing. Fix where the wrong behavior originates, and check every caller of the
  changed code.
- Changing an error into a silent default, or a default into an error, beyond what was
  declared. Callers that handled the old behavior now break.
- Tightening a check that some caller depended on being loose. If the looser input was
  accepted by the specification, the fix is a contract change, not a plain bug fix.
- Fixing an ordering or timing problem by adding a delay or a retry. It hides the race rather
  than removing it.
- Writing the test after the fix and to match it. Write the test from the evidence of what the
  behavior should be, and see it fail first.
