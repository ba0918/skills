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
   the repository that contains it (`git rev-parse --show-toplevel`) and record, for that whole
   repository:
   - the current commit (`git rev-parse HEAD`; record "none" before the first commit);
   - every file with changes and every untracked file git does not ignore
     (`git status --porcelain --untracked-files=all --no-renames`, which lists untracked files
     one by one instead of collapsing a directory into one line, and a rename as its two paths);
   - the content hash of each of those files (`git hash-object <path>`), or "absent" for a file
     that was deleted.

   Write this record to a file in the output location, named per run like the output files
   below. Keep it out of the conversation: the caller only needs its path. When the working
   directory is not under git, or git cannot be found, record nothing; the change list will
   then be reported as not detectable.

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
