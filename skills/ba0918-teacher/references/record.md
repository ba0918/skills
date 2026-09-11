# Learning record procedures

## Storage and lifetime

Keep personal learning records at `~/.agents/ba0918-teacher/<name>.md`, outside repositories
and under the user's home directory. Knowledge belongs to the user, not a repository.
Use lowercase letters and digits for the language or field name, such as `rust`, `typescript`,
or `sql`. If the theme names no language, use the language of the code being worked on.
Record a concept spanning two fields only in the current theme's file.

Records persist across sessions until the user deletes them. Never delete or merge concept
entries or session summaries; the user organizes them manually. The mode's enabled state and
learning theme live only in the conversation until disable or session end, not in the record.

Write only the contents of the fields in "Record format". Do not write code examples, even
ones you invent. Never include the working repository's code, internal project or host names,
or customer names, including within fields.

## Record format

Write records in this fixed order so the user can read, edit, and prepare them by hand:

1. Level 1 heading: the record name.
2. Experience line: one of new to it, able to read it, or writing it regularly.
3. Level 2 heading for what to do next: a bullet list, replaced with current intentions on
   each disable.
4. Level 2 heading for concepts: one level 3 heading per concept, each with four bullet lines
   in this order:
   - State: understood or stuck.
   - Last checked date: for a stuck concept, the date it was recorded as stuck.
   - Next review date: blank while stuck.
   - Source: a URL or document title and section, with verified or unverified status.
     Its contents may be empty when no source is available yet.
5. Level 2 heading for session summaries: append a dated bullet, one line per session per
   file. When returning to a file in the same session, rewrite that session's line rather
   than adding another.

Write dates as `YYYY-MM-DD`. Use the environment's language for headings, field names, and
the words within the format. For an existing file, match its existing names. The English
labels in this illustration express their meaning; they do not mandate the output language.

```markdown
# rust

Experience: able to read it

## What to do next
- Write lifetime annotations independently

## Concepts
### Borrow checker
- State: understood
- Last checked: 2026-09-11
- Next review: 2026-09-12
- Source: The Rust Programming Language, References and Borrowing (verified)

## Session summaries
- 2026-09-11: Understood how to read borrow checker errors; got stuck on lifetimes
```

## Reading existing records

Treat a file as unreadable if either condition holds:

- Any required level 2 heading for next intentions, concepts, or session summaries is missing.
- For a concept, the state or last checked date is missing, an understood concept lacks a
  next review date, or the meaning of one of those values cannot be interpreted.

Tell the user which part is unreadable and do not overwrite the file. Use "Files that cannot
be saved" for the rest of the session, with the partial-content display rule for unreadable
files at disable.

Allow other differences. Ignore and preserve lines the user added, allow reordered level 2
headings, and accept equivalent wording for states and other values. A blank next review
date for a stuck concept and an empty source are valid.

## Files that cannot be saved

If a file cannot be written, continue teacher mode. Tell the user once, at the first failure,
that its record is not being saved, and make no more attempts to write that file during this
session. Treat even one refusal to create or write a file the same way. This applies only to
that file; continue writing other record files normally. Never save to another location,
including inside the repository, and do not keep asking for permission at later milestones.

At disable, display the entire file you would have written, in the record format, so the
user can replace the file with it. Display each affected file separately if there are several.
For an unreadable file, instead display only entries added or changed during this session
for the user to add manually. Do not reconstruct the whole file: replacing it could lose
existing concepts or notes in the parts you could not read.

## Opening a record

Open the record for the learning theme's language or field. Read an existing file according
to "Reading existing records". If no corresponding file exists, propose its name and create
it only after the user agrees. When creating a new file, ask about experience once and fill
the experience field with their answer. Follow "Files that cannot be saved" for refusal or
failure, and continue teaching.

While a theme is provisional, defer all record reads, writes, and review checks. Once the
theme is confirmed, wait until the current small piece of work is finished, then open its
record and perform opening review checks. If the confirmed theme corresponds to the same
file as the provisional theme, also record together the concepts understood while the theme
was provisional and before this opening. If it corresponds to a different file, do not
record those concepts.

After opening the record, use "Review checks" for due understood concepts. If there are stuck
concepts, mention them once as candidates for today's learning theme, asking whether the user
wants to work on them. Do not make stuck concepts into review questions.

## Learning milestones

Write incrementally when a concept becomes understood, a review check is completed, or the
user gets stuck on an already understood concept. Follow "Dates and concept states" for the
update. Write at these milestones even if every write needs permission; the milestones
already saved survive if the session ends without disable. Do not postpone all writes until
the end. Apply the per-file failure rule after refusal or failure.

Do not read or write records while the theme is provisional. Do not update them during
ordinary work. Disable during ordinary work still summarizes the preceding teaching portion
using "Ending the session".

## Review checks

On enable, offer only one or two understood concepts whose next review date has arrived,
oldest due date first. Do not offer every due concept. Do not repeat opening checks when
returning to the same record file in the same session, including changes between themes.

Ask the user to explain in their own words or write a small code snippet, never choose from
multiple answers. Give a judgment of remembered, partly remembered, or forgotten, together
with your reason. The user can overturn the judgment with a brief correction. Express these
meanings in the environment's language. Update dates using "Dates and concept states".

Let the user skip and move on to work. Leave skipped concepts' dates unchanged and do not ask
about them again during this session, including during work. In-work checks follow the
conditions in "Learning record entry points" in the skill body and use the same question
format, judgments, and date updates. Stuck concepts are never review-check targets.

## Dates and concept states

Obtain today's date from the environment. If unavailable, ask the user once per session;
never guess a date.

Use the understanding criteria in "Learning record entry points" in the skill body. When
first marking a concept understood, or changing it from stuck to understood, set last
checked to today and next review to one day later. Give the user your judgment and its
reason, which they can overturn.

For a completed review check, calculate the planned interval from the stored next review
date minus the stored last checked date, not the actual time elapsed. Set the new interval
from the judgment:

- Remembered: double the planned interval, such as one day to two, then four.
- Partly remembered: keep the planned interval.
- Forgotten: reset to one day; keep the state understood.

Then set last checked to today and next review to today plus the new interval. For example,
last checked on 2026-09-01 and due on 2026-09-03 means a two-day planned interval. If recalled
on 2026-09-11, last checked becomes 2026-09-11 and next review becomes 2026-09-15.

Mark a concept stuck only when writing a session summary on disable or a theme change, and
only if it remains unresolved in this session and is either absent from the record or already
stuck. Set last checked to the date recorded as stuck and leave next review blank. A concept
resolved within the same session goes directly to understood.

If the user gets stuck during work on an understood concept, treat it as forgotten in a
review: keep it understood, set last checked to today, and reset next review to one day
later. Keep that treatment even if it remains unresolved when writing the summary; do not
change an already understood concept to stuck.

## Switching record files

When a theme change corresponds to a different record file:

1. Write a one-line summary of the session so far to the previous file, rewriting this
   session's line if it already exists. Record unresolved concepts for that theme according
   to "Dates and concept states".
2. Read or create the new theme's file using only the first paragraph of "Opening a record";
   perform the review checks in the next step.
3. Offer one or two due review checks for the new file using "Review checks". Skip this step
   if the file had already been opened in this session before the current theme change.

Use the new theme's record for its concepts; do not keep writing them to the previous file.
Honor the deferred theme change during ordinary work described in the skill body.

## Ending the session

On disable, write the session summary and unresolved concepts according to "Record format"
and "Dates and concept states", and replace what to do next with the latest intentions.
Keep one summary line per session per file; rewrite the existing line when returning to the
same file within the session. If disabled during ordinary work, summarize only the teaching
portion before it. Do not write records if the theme is still provisional.

Display unsaved content for every affected file according to "Files that cannot be saved":
the whole intended file for write failures or refusals, only this session's added or changed
entries for unreadable files. Then continue the disable procedure in the skill body.
