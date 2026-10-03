---
name: ba0918-activity-report
description: "Collect the user's git commits for a period they name, across every repository they worked in (local clones on all branches plus GitHub), classify them, and write one self-contained HTML page that shows what they did with charts and plain-language summaries. Writes that one file only when the user asks for such a report. Use when the user asks what they did recently, wants a look back over their recent activity, a summary of their git log over a period, or a visual activity report across repositories. 日本語キーワード: 活動レポート 振り返り 最近何してた git log まとめ 期間 リポジトリ横断 作業記録 可視化 HTML"
---

# Activity Report

## Scope

Turns the user's commits over a period into one HTML page they can open and enjoy. It reads
repositories and writes that single file, only when the user asked for the report. It does not
commit, push, publish, or upload the page; the page can carry subjects of unpushed commits, so
sharing it is the user's call.

## Procedure

1. **Settle the inputs.** The period is required; ask if it is missing. Take the reader from the
   user, defaulting to the user themselves, and write in the user's language. When the reader is
   not an engineer, add a short explanation of what a commit is near the top; the example omits
   it because its reader is the developer. The author is the
   local git user name and email plus the GitHub login if `gh` is signed in. Ask where the
   repositories live if no directory is evident.
2. **Collect from both sources.** Locally, for every git repository under that directory, run
   `git log --all --since <start> --until <end> --author <name-or-email>`. On GitHub, run
   `gh search commits --author <login> --committer-date <start>..<end> --limit 1000`; a search
   returns at most 1000 results, so when one comes back full, split its range (one day per search,
   for example) and search again. Merge the
   two, deduplicate by commit SHA, name each repository from its `origin` URL so worktrees and
   extra clones fold together, and convert all times to the user's time zone. Local is the main
   source: GitHub search sees only default branches of indexed repositories and misses much.
3. **Classify.** Use the Conventional Commits type (`ci` and `build` join `chore`; merges are their
   own group). Give an untyped commit a type by reading its subject, so no "other" bucket remains.
4. **Write the page.** Follow `assets/example.html` for its sections, layout, styling, charts and
   tone, replacing every piece of its data with the collected data. For each repository, read its
   subjects and write a short plain metaphor, a one-line description, and one to three
   summary bullets; keep the raw commit list in a collapsed block. Count releases only from
   release commits and say they were not checked against tags. The example is in English and
   covers two days: write every label and sentence in the reader's language, and for a period
   longer than a few days chart commits per day instead of per hour. Keep it a single file with
   no external requests.
5. **Save it** where the user says, or outside every repository otherwise.

## Evidence of completion

- The path of the written file.
- The per-repository counts and the total, matching the number of deduplicated commits.
- The period, the sources used, and any source that failed (for example `gh` not signed in).
- A rendered view of the page where a browser or screenshot tool is available.
