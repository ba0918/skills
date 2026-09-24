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
