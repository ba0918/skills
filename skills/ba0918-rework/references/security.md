# Security problems

A security problem is code that lets an input or an actor do more than the specification
allows: read or change data they should not, run code, or exhaust a resource.

## How to find them

- Input from outside — a request, a file, an environment variable, a message — reaching a
  query, a shell command, a file path, a template, or a deserializer without being validated
  or escaped for that destination.
- Queries or commands built by concatenating strings instead of passing parameters.
- Missing or inconsistent authorization: a check on one path to the data but not another; a
  check on the user interface that the server does not repeat.
- Secrets in source, in logs, in error messages, or in responses.
- Weak or hand-written cryptography, predictable random values used for tokens, comparisons of
  secrets that leak timing.
- File paths joined from input without confining them to a directory.
- Unbounded input size, recursion depth, or retry counts that let one request exhaust memory
  or time.
- Handling of stored data that can lose or corrupt it when attacked. Mark such an item as data
  destruction; it is fixed first.

## Pitfalls when fixing

- Rejecting input changes behavior. If the rejected input was never valid under the
  specification — an injection string, a value outside the declared type's range — the fix is
  not a contract change. If the specification accepted that input before, rejecting it is a
  contract change and an ask item.
- Escaping in the wrong place: escaping for one destination and passing the value to another,
  or escaping twice so legitimate data is mangled.
- Fixing one entry point and leaving the others. Search the scope for every path that reaches
  the same sink.
- Error messages that change with the fix and now reveal less (usually intended) or more
  (never intended). Declare the change to what callers see.
- Logging the rejected input verbatim, which can put the attack payload or a secret into logs.
