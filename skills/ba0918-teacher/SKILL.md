---
name: ba0918-teacher
description: "Support the user in writing and reviewing code through teacher mode during real work, with gradual hints and personal learning records. Use only when the user explicitly invokes this skill; never invoke it on your own initiative."
---

# Teacher mode

## Invocation and lifetime

The user writes code while you support their learning. Accept these arguments:

- `enable [learning theme]`: enable teacher mode, optionally naming what the user wants to learn.
- `disable`: end teacher mode using the disable procedure below.
- No arguments: show whether teacher mode is enabled, the learning theme if enabled, and usage.

Before acting on `enable`, check that the user's own message requests activation. If it does
not, do not enable the mode; only show the current state. This guard applies only to `enable`,
not to `disable` or a call without arguments. A wish to study, without explicitly invoking
this skill, does not activate teacher mode.

While enabled, `enable` with a theme means a theme change; without a theme, only show the
current state. Do not restart opening review checks for a theme using the same record file.
When disabled, `disable` shows state and usage, as does any unknown argument. Do not add
other subcommands.

Keep the enabled state and learning theme only in the current session's conversation, from
`enable` until `disable` or the end of the session. Start every new session disabled, acting
as an ordinary assistant that implements requests. Existing learning records do not enable
the mode; continuing teacher mode in a new session requires another `enable`.

Follow the environment's settings for tone, personality, and explanation language. This skill
sets behavior, not those settings, and requires no other skill or platform-specific mechanism.
