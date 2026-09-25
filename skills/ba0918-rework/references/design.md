# Design problems

A design problem is a structure that keeps producing defects or makes a correct change hard:
responsibilities mixed in one place, dependencies pointing the wrong way, state owned by no one.

Treat a design fix as a structural change made to remove a problem. It is not a small
readability transformation — renaming, extracting a function to shorten it, reordering for
clarity — which is the job of the skill `ba0918-refactor`, not this one. A design fix often
keeps behavior identical; declare that, and prove it with tests as for any other item.

## How to find them

- One unit doing several unrelated jobs: parsing input, applying business rules, and writing
  to storage in the same function, so none of them can be tested alone.
- Dependencies that point the wrong way: core logic importing a web framework, a database
  driver, or a user interface layer; a lower layer calling back into a higher one.
- Business rules duplicated in several places that have already drifted apart, so the same
  input gets different answers depending on the path.
- Hidden global state or singletons that force tests to run in a particular order or share
  setup.
- A type or a flag that carries several meanings, so every caller re-checks which meaning
  applies.
- A bug found under another perspective whose real cause is structural — it will come back in
  a new form unless the structure changes.

## Pitfalls when fixing

- Moving code changes when things happen: initialization order, the moment a side effect runs,
  the point at which an error is raised. Declare any such change or keep the order.
- Splitting a unit changes what is public. A function that was internal may become importable,
  or a public one may disappear; the shape of a public API is a contract change.
- Introducing a new abstraction for one use. Change only as much structure as removes the
  problem you declared.
- Growing the change beyond the scope. Callers outside the scope that would need updating are
  reported, not edited; if the fix cannot be made without them, hold the item.
- A design fix that rewrites code another item was about to fix. Order items so the design fix
  goes first, then re-check whether the other item still applies.
