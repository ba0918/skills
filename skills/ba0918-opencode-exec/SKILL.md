---
name: ba0918-opencode-exec
description: "Run one task through opencode v2 (opencode run) with a prompt file, model, and environment the caller prepared, then return the exit code, the paths of the stdout and stderr files, and the list of files that changed in the repository. It does not write the prompt, judge the result, or set up read-only mode, worktrees, or permissions. Runs only when the user names this executor, or when an instruction the user prepared (an assignment table, a local skill, an instruction file) names it; being loaded, or opencode merely coming up in conversation, is not a request. The working directory contents and the prompt are sent to the provider of the chosen model, without asking again before the run. Use when the user says run this with opencode, have another provider's model do this task, hand this to opencode, or execute this prompt through opencode. 日本語キーワード: opencode で実行 opencode に任せて 別の提供元のモデルで 実行役 プロンプトを実行"
---

# opencode Executor

## Scope

This skill is an executor: it runs `opencode run` (opencode v2) exactly once with a prompt file,
a model, and an environment that the caller prepared, and returns what happened — the exit code,
the paths of the stdout and stderr files, and the list of files that changed.

It does not cover:

- Writing or improving the prompt. The prompt file arrives complete; its content is the caller's.
- Judging the result. The skill neither summarizes the output nor says whether the task
  succeeded; the caller reads the files and decides.
- Preparing the environment: making the run read-only, choosing or creating a worktree, or
  setting permissions. The caller does that, through the working directory, the opencode agent
  it names, or the pre-command it passes. The skill does not control or enforce any of it.
- opencode v1. Its flags differ and it has no `--standalone`, so the skill refuses to run it.
- Undoing changes. The skill reports changes and never reverts them.

## When this runs

Run only when one of these names this executor:

- the user, directly ("run this with opencode", "have opencode's model investigate this");
- an instruction the user prepared, in whatever form — an assignment table, a local skill that
  combines this one with a task, an instruction file.

Nothing else is a request. This skill being loaded, a task skill being loaded, or opencode
coming up in conversation ("how do I use opencode?") does not start a run.

A run sends the contents of the working directory and the prompt to the provider of the chosen
model. Being named counts as the decision to send them: do not ask for confirmation again before
running.

## Inputs

| Input | Required | Default when not given |
|---|---|---|
| Prompt file — a self-contained task instruction | yes | — |
| Model — `provider/model` or `provider/model#variant` | yes | — |
| Working directory — where opencode runs, such as a prepared worktree | no | the current working directory |
| Agent name — an agent defined in the opencode configuration, used to apply its permission settings | no | none; `--agent` is omitted |
| Pre-command — a command placed in front of opencode, such as one that starts a sandbox; received as a list of words (an argument list) | no | none |
| Command name — the name opencode v2 is installed under | no | `opencode` |
| No-change — this run must not change the working directory | no | not set |
| Time limit | no | none; wait however long the run takes |
| Output location — where the stdout, stderr, and pre-run record files go | no | a new temporary directory, outside any repository |

Do not choose a model, a pre-command, or anything else the caller did not pass. The only values
the skill supplies are the defaults in this table.

## Before running

Stop without running, and tell the caller what is missing or wrong, when any of these holds:

- The prompt file or the model was not passed.
- The prompt file does not exist, is empty, or cannot be read.
- The working directory does not exist.
- The output location is inside the repository that contains the working directory — or, when
  the working directory is not under git, inside the working directory itself. Compare resolved
  absolute paths. Never move the output somewhere else silently: the caller would then look for
  the files in the wrong place. When the output location is outside and does not exist yet,
  create it.
- The prompt file's contents begin with `-`. opencode could read the prompt as a flag.
- The version check below finds no command, or a major version other than 2.

Do not check how the model is written. If it is wrong, opencode reports an error, and that
error is the result.

Then, in this order:

1. **Check the version inside the pre-command.** Run the pre-command followed by
   `<command name> --version`, in the working directory. If the command is not found, stop and
   say so. If the major version is not 2, stop and report that opencode v2 is required and which
   version was found. The check runs inside the pre-command because a sandbox may resolve the
   command name to a different installation than the one outside it. v1 is refused rather than
   tried, because its flags mean different things and it has no `--standalone`.
2. **Record the repository's state**, when the working directory is under git. Find the root of
   the repository that contains it (`git rev-parse --show-toplevel`, run in the working
   directory). Run every other git command in this skill at that root, because the paths git
   reports are relative to it. Record, for the whole repository:
   - the current commit (`git rev-parse HEAD`; record "none" before the first commit);
   - every file with changes and every untracked file git does not ignore
     (`git status --porcelain --untracked-files=all --no-renames`, which lists untracked files
     one by one instead of collapsing a directory into one line, and a rename as its two paths);
   - the content hash of each of those files (`git hash-object <path>`), or "absent" for a file
     that was deleted.

   Write this record to a file in the output location, named per run like the output files
   below, with `.before` as the ending. Keep its contents out of the conversation. When the
   working directory is not under git, or git cannot be found, record nothing; the change list
   will then be reported as not detectable.

## Command

Run this, in the working directory:

```
[pre-command] <command name> run --standalone --auto --model <model> [--agent <agent name>] <prompt file contents>
```

- **Pre-command.** Place the words the caller passed in front, in the same order, each one
  unchanged. Do not interpret them. When the caller passed the pre-command as one string, place
  that string as one single word: do not split it on spaces and do not let a shell interpret it.
- **`--standalone`, always.** Without it opencode hands the work to its background service,
  which runs outside any sandbox the pre-command set up.
- **`--auto`, always.** Without it the run may stop at a permission prompt that no one sees.
  `--auto` grants every permission the opencode configuration does not explicitly deny, which is
  why every result says so.
- **The prompt is one argument.** Read the prompt file and pass its whole contents as a single
  message argument, exactly as read. No shell may expand or split it: quotes, `$`, backticks,
  and newlines must reach opencode unchanged. Start the process with an argument list where the
  environment allows it. When the only way to start it is through a shell, put the contents into
  a variable first and pass that variable, double-quoted, as the argument — never paste the
  contents into the command text.
- **Not `--file`.** The prompt is not attached as a file. The prompt file stays where the caller
  put it, as the record of what was asked.
- **Too long to start.** If the process cannot start because the prompt is too long, report
  that. Do not switch to another way of passing it.
- **Output files.** Write stdout and stderr to two files in the output location, named uniquely
  per run with the date and time and a random part — for example
  `opencode-20260924T101500Z-k3f9.stdout` and the same name with `.stderr`. Never overwrite an
  existing file: if the name is taken, pick another random part.
- **Default output format.** Keep opencode's default output in the stdout file. Do not add
  `--format json`.

## Running and waiting

Start the command in a way that lets this session wait for it to finish, and wait until it
exits. A run can take tens of minutes. Do not stop it or start it again to check on its
progress; the stdout and stderr files are there to read after it ends.

Only when a time limit was passed: note the process id of the command at start. Once the limit
passes, stop that process and every process descended from it — first ask them to terminate,
then force any that remain after a short grace period. Stopping only the outermost process is
not enough: when a pre-command wraps opencode, opencode inside it would keep writing. Find the
processes by their descent from the one you started, never by name, and stop no other process:
another opencode run may be working at the same time. After they have stopped, build the change
list as below, and mark the result as timed out.

## Change list

After the run ends — exit code 0, any other exit code, or timed out — build the change list by
comparing the repository with the pre-run record. Skip this when nothing was recorded; the
result then says changes could not be detected.

1. Read the repository's state again, at the repository root and the same way as the pre-run
   record: the current commit, the files with changes and the untracked files git does not
   ignore, and their content hashes.
2. If the current commit differs from the recorded one, note that the commit moved and list
   the files changed between the two commits (`git diff --name-only <before> <after>`; when
   there was no commit before, every file in the new commit, `git ls-tree -r --name-only HEAD`).
3. Compare the union of: files with changes before, files with changes after, untracked files
   before and after, and the files changed between the commits. Collecting this union catches a
   file that had changes before the run and was put back to its committed content during it.
4. For each file in the union, take its content hash before — from the pre-run record, or, for
   a file the record does not list, the hash of that file in the recorded commit
   (`git rev-parse <before>:<path>`), or "absent" when it is not there — and its content hash
   now (`git hash-object <path>`, or "absent" when the file is gone). The file is added,
   modified, or deleted when the two differ.
5. The change list is the files from step 4 whose hashes differ, together with the files
   changed between the commits from step 2. When the commit moved, the change list also states
   that fact, with the commits before and after.

Rules for the change list:

- It covers the whole repository that contains the working directory, not only the working
  directory. Files git ignores are not covered, and the result says so.
- It compares the state before and after only. A file with changes before the run is listed
  when its content changed again. A file that changed during the run and returned to its earlier
  content is not listed.
- It does not tell who made a change: opencode, the caller, or anything else running at the same
  time. A caller that needs to tell them apart gives the run its own directory.
- Nothing in it is reverted. The caller or the person decides what to do with each change.

## Result

Report these five things, without summarizing the output or judging whether the task went well:

1. **Exit code.** On a timeout, say that the run timed out instead of reporting it as a normal
   exit.
2. **The stdout file's path.**
3. **The stderr file's path.**
4. **The change list**, stated as the changes in the repository's git-visible files between the
   start and the end of the run, not attributed to anyone, and excluding files git ignores. When
   the commit moved during the run, say so, with the commits before and after, together with the
   files changed between them. When the working directory is not under git, or git cannot be
   found, say that changes could not be detected instead.
5. **The `--auto` note:** every permission the opencode configuration does not deny was granted
   automatically.

A failure of the pre-command and a failure of opencode are not told apart. Both show up as the
exit code and in the stderr file.

When the run was passed no-change, put one of these before everything else in the result:

- the change list is not empty: say that changes occurred, and list them;
- changes could not be detected: say so, because the run cannot be confirmed to have left the
  directory unchanged.

## Output files

The stdout file, the stderr file, and the pre-run record stay in the output location. The skill
never deletes them, and never deletes the prompt file either. Removing them is up to the caller
or the person, whenever they choose.

## Judgment

**Why the environment is the caller's.** opencode by itself cannot be made read-only from the
command line, so the skill has no way to enforce it. The caller can: with an opencode agent whose
permissions deny writing, or with a pre-command that starts a sandbox where the working directory
is read-only. Keeping that choice with the caller lets the same skill serve investigation,
review, and writing tasks.

**Why the change list is reported, not enforced.** A no-change run that changed files is a fact
the caller must see first, but only the caller knows whether a change was harmless. Reverting it
automatically could destroy work the person wanted, so the skill reports and stops there.

**Why the output lives outside the repository.** Output files inside it would show up in the
change list themselves and leave the repository dirty.

**Why the output format is the default.** The caller reads the output and judges it; opencode's
default output is readable as it is, and a structured format adds nothing the skill uses.
