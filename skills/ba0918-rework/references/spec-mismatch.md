# Mismatches with the specification

A mismatch is a place where the code and the specification disagree.

What counts as the specification is defined under Terms in `SKILL.md`.

## How to find them

- Documented parameters, return values, defaults, or error conditions that the code does not
  implement, or implements differently.
- Types that promise more than the code delivers: a value declared never missing that can be
  missing, a return type narrower than what is returned.
- A test whose name states a behavior that its assertions do not check, or check the opposite
  of.
- README examples that no longer run as shown.
- Two written sources that describe the same behavior differently.

## Deciding which side is right

When the evidence settles it — the callers' expectations, the tests, and the history of the
change agree on one side — decide without asking. If the code is right, fix the document as
part of the same item and say so in the report; that item is verified by comparing the
document against the code, not by a new test. If the sources contradict each other and nothing
says which takes precedence, the item is an ask item.

## Pitfalls when fixing

- Changing the code to match a document that was never updated after a deliberate change. Read
  the history of both before deciding which one is stale.
- Changing a documented public interface to match the code. That is a contract change.
- Fixing one of several documents that repeat the same claim and leaving the rest
  contradicting it. Find every copy inside the scope; copies outside it are reported.
- Treating a test name as the specification when its assertions and the callers all agree with
  the code. The name may be the stale part.
