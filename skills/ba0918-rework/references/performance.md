# Performance problems

A performance problem is work that grows faster than it needs to with the size of the input,
or that repeats what could be done once.

Passing tests do not show that a performance fix worked, because the results stay the same.
Measure before and after (see the rules on items that need measurement).

## How to find them

- N+1 queries: a loop over records that triggers a query per record, typically through lazy
  loading of a related object inside the loop, or a call to a data-access function in the loop
  body.
- Nested loops over the same or related collections where a lookup table would do; searching a
  list repeatedly for membership.
- Repeated work inside a loop that does not depend on the loop variable: compiling a pattern,
  opening a connection, reading a configuration file.
- Loading a whole dataset into memory to use a small part of it; fetching every column or field
  when a few are read.
- Serial calls to a remote service that do not depend on each other.
- Missing limits: an endpoint or a job that has no pagination and slows as data accumulates.

## Pitfalls when fixing

- Batch loading changes the order of results. Replacing a per-record query with one query that
  loads everything often returns rows in a different order, or groups them differently. If the
  caller or the output depended on the old order, restore it explicitly or declare the change.
- Batch loading changes what happens for missing or duplicate records: a per-record lookup that
  raised an error for a missing record may now silently skip it.
- Caching changes freshness. A cached value can be stale where the old code always read the
  current value; declare the new staleness or do not cache.
- Running calls in parallel changes the order of side effects and the way errors surface.
- Loading everything at once to avoid many small queries can turn a time problem into a memory
  problem. Measure both when the data can be large.
- "It should be faster now" is not evidence. Report the measured numbers from before and after,
  such as the count of queries issued.
