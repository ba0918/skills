---
name: ba0918-handoff
description: "Carry working context from one session to the next through a single file, .agents/HANDOFF.md. Save extracts the goal, history, current state, decisions, open issues, and next actions from the conversation and writes them there, overwriting the previous handoff; restore reads the file and orients the user so the work continues. Use when context is running out, when the user says handoff, hand this over, save before clearing, switch sessions, or pick up where the last session left off. 日本語キーワード: 引き継ぎ ハンドオフ セッション 文脈 保存 復元 コンテキスト 続き"
---

# Session Handoff

## Scope

Applies when work must continue in a different session than the one it started in: context is
running out, the session is about to be cleared, or a new session is picking up prior work.

The argument selects the mode: `save` (default) or `restore`.

There is one handoff file per working tree: `.agents/HANDOFF.md` at the project root. It is
working state, never committed: if it is not ignored by git, warn the user before writing.

The file is written for the next session's agent, so its layout is fixed. What the agent says
to the person in front of it is not: those reports follow ordinary readability — plain sentences
the reader can check against the file, no mandated block.

## Save

1. Record the current branch (`git branch --show-current`); outside a git repository, record
   `(none)` and continue.
2. If `.agents/HANDOFF.md` already exists and its `branch` differs from the current branch, it
   describes other work. Tell the user what it covers and ask before overwriting. On the same
   branch, overwrite without asking.
3. Extract the following from the conversation history. Do not ask the user; transcribe.
   - **Goal** — what the user set out to achieve, and why
   - **History** — decisions made, alternatives rejected and the reason
   - **Current state** — done, in progress (how far), not started
   - **Related files** — absolute paths with each file's role
   - **Decisions and constraints** — user instructions, preferences, adopted policies
   - **Open issues** — unresolved questions, blockers
   - **Next actions** — the concrete first steps for the next session
   - **Cautions** — pitfalls, things not to do
4. Write `.agents/HANDOFF.md` using the template below, creating `.agents/` if needed. `status`
   is exactly one of `in-progress`, `blocked`, `reviewing`; when unsure, `in-progress`.
5. Tell the user, in a few sentences, what state the work was left in and what the next session
   will do first, and that the next session restores it by running this skill in `restore` mode.

Section headings in the file are fixed tokens and stay in English; the content under them
follows the language of the conversation.

```markdown
---
created: {ISO 8601}
branch: {branch}
status: {in-progress | blocked | reviewing}
---

# Handoff: {one-line summary}

## TL;DR
{3–5 lines: the goal and the current position, readable in isolation}

## Goal / Why

## How we got here

## Current state
### Done
### In progress
### Not started

## Related files
- `/absolute/path/to/file` — {role}

## Decisions / constraints

## Open issues

## Next actions
1.

## Cautions
```

## Restore

1. Read `.agents/HANDOFF.md`. If it does not exist, say so and stop.
2. Orient the user: what the work is for, where it stood when the last session ended, and what
   to do first. State the file's `created` time and `branch`; if the branch differs from the
   current one, say so — the file may describe other or finished work. Write it so someone who
   has not read the file can act on it; do not reproduce the file or re-list its cautions.
3. Leave the file in place. The next save overwrites it; deleting it is the user's call.

## Rules

- Save extracts from the conversation autonomously. Never interview the user to fill the file.
- Every file reference in a handoff is an absolute path. The next session's working directory is
  unknown.
- Secrets never enter a handoff file. Name the category ("the API token in `.env`") instead of
  the value.
- Save does not run tests, builds, or any other command beyond reading the branch name.

## Judgment

**Why one file.** Two handoffs never relate to each other except that the newer one supersedes
the older. A fixed path expresses exactly that, with nothing to name, order, or pick from.

**Why restore does not delete.** Deleting on read loses the handoff when the restoring session
dies right afterwards, or when the user only wanted to look. A file that stays costs nothing
until it is stale, and staleness is visible from `created` and `branch` in the report.

**Why the branch check before overwriting.** Two sessions on different work in the same checkout
would otherwise silently destroy each other's handoff. Worktrees do not collide because each has
its own `.agents/`; the check covers the one case that does.

**Why the reports have no fixed block.** A labelled block ("Goal / Where we are / Next move")
can be filled in without telling the reader anything they can act on, and the labels then stand
in for readability. The file has a fixed layout because an agent parses it; the person needs
sentences that connect the state to the next move.

**Why the TL;DR is written for isolation.** The next session reads the TL;DR before anything
else, possibly before it has read any code. A TL;DR that leans on the rest of the file forces a
full read to understand the first line.

## Evidence

- **Save**: `.agents/HANDOFF.md` exists with the template's headings, and a report the user can
  check against it.
- **Restore**: an orientation the user can act on, including the file's `created` and `branch`.
