---
name: ba0918-rework
description: "Diagnose a scope of code the person names — a file, a directory, a symbol, or the last N commits — for bugs, design problems, performance problems, memory leaks, security problems, and mismatches with the written specification, then fix what it finds one item at a time, verifying each fix with tests and committing each as its own commit on a dedicated branch in a separate worktree. Unlike ba0918-refactor, it allows fixes that change behavior: it declares what changes and tests both what changes and what must not. Edits run only when the person names a scope and asks for it to be fixed; a request only to find or list problems is review or investigation, and problem code noticed during other work is pointed out, not fixed. Use when the user says rework this, find and fix the problems in this, diagnose and fix this directory, fix everything wrong with this module, or clean up the bugs in the last N commits. 日本語キーワード: 手直し 問題を見つけて直して 診断して直して まとめて直して 直近Nコミットを直して rework"
---

# Rework

## Scope

Applies when the person names a scope and asks for its problems to be fixed. The skill
diagnoses the scope, fixes each problem it finds — including fixes that change behavior — one
at a time, verifies each fix with tests, and commits each fix as its own commit on a dedicated
branch.

It does not cover:

- Diagnosis only. A request to find or list problems without fixing them is a review or an
  investigation, not this skill.
- Improving how code reads while keeping its behavior identical. That is the skill
  `ba0918-refactor`. Design problems fixed here are structural changes made to remove a
  problem, not small readability transformations.
- Merging, pushing, filing issues, or deleting the worktree. The person decides these after
  reading the report.
- Fixing anything outside the named scope, or running a flow to get agreement for doing so.

**The top priority is not to add questions to the person.** When people are asked too often,
they approve without reading, and asking stops meaning anything. What can be decided from
measurement or from evidence inside the repository is decided here and acted on. In place of
up-front confirmation, two safety nets remain:

- Every fix is its own commit on a dedicated branch. A fix the person dislikes is undone by
  reverting that commit.
- The report carries the evidence behind each decision and the measured results.

### Inputs

| Input | Required | Meaning |
|---|---|---|
| Scope | yes | A file, a directory, a symbol, or "the last N commits" (expanded to the files those commits changed) |
| Perspectives | no | Which of the six perspectives to look at (for example, security only). Default: all six |
| Advance permission | no | Permission to proceed on ask items without asking (see Rules) |

If the scope cannot be resolved — a path does not exist, a symbol cannot be found — change
nothing and return the reason.

If the scope is too large to hold in mind at once, propose a split and stop. Stopping partway
through a scope leaves it unclear what was fixed and what was not. Draw no fixed line such as a
line count: while diagnosing, if you judge before finishing the files in scope that you can no
longer retain what you have read, stop and write that reason into the split proposal. There is
no upper limit on the number of items fixed.

When the scope is large, the read-only diagnosis may be handed to an agent running in a
separate context. Editing files always stays with the session that was invoked.

## When edits may run

Edit files only when the person has named a scope and asked for it to be fixed. Do not edit in
these cases:

- The person asked only to find or list problems ("find the problems in this", "list what is
  wrong"). That is the job of a review or an investigation; answer without changing files or
  creating a branch.
- You noticed problematic code while doing other work. Point it out and stop.
