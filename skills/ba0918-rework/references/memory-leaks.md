# Memory leaks

A memory leak is memory, or another resource, that is kept after it is no longer needed and
accumulates the longer the program runs.

Passing tests do not show that a leak is fixed, because the results stay the same. Compare
memory use, or the count of held resources, over repeated runs before and after the fix (see
the rules on items that need measurement).

## How to find them

- Collections that only grow: a module-level cache, registry, or list with no eviction, size
  limit, or removal on completion.
- Listeners, callbacks, observers, or subscriptions registered and never removed, which keep
  their owners alive.
- Timers, intervals, background tasks, or threads started and never stopped.
- Files, sockets, database connections, or handles opened without a guaranteed close on every
  path, including error paths.
- Closures that capture a large object when only a small part of it is used.
- References between objects that keep each other alive in a runtime that cannot collect such
  cycles, or across a boundary the collector cannot see.

## Pitfalls when fixing

- Evicting from a cache changes behavior for callers that relied on an entry being there, or
  on getting the same instance back.
- Releasing a resource too early: closing a connection or removing a listener that another
  part of the program still uses.
- Moving cleanup to a finalizer or destructor whose timing the runtime does not guarantee.
- Adding a size limit changes which entries survive; declare the eviction policy.
- A single before-and-after snapshot can mislead. Measure a trend over many repetitions of the
  same operation, and compare the growth, not one number.
