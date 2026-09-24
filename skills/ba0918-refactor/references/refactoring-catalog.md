# Refactoring catalog

Read in step 4 before accepting a candidate you found yourself. The patterns are common cases,
not a closed list; the Trap column is the part to check a candidate against, whether or not
it appears here.

The thresholds under "Signs" are prompts to look, not cut-offs. A borderline case becomes a
candidate only if someone new to the code would understand the result faster.

| Pattern | Signs | Behavior-preserving transformation | Trap |
|---|---|---|---|
| Deep nesting | three or more levels of if/for; code drifting right | guard clauses, early returns | an early return must not reorder side effects |
| Long function | several responsibilities; needs scrolling | extract functions at units a name can explain | extraction must not hide shared state |
| Nested conditional expression | `a ? b : c ? d : e` | if/else, early return, or a lookup table | keep short-circuit evaluation order |
| Boolean flag argument | `export(true)` unreadable at the call site | two functions named for their intent, or an enumeration | every caller changes; each must be in scope or go through step 6 |
| Generic name | `data`, `tmp`, `res`, `handle()` | a name that states the role | public APIs and serialized keys cannot be renamed |
| Comment restating code | `// increment i` | delete it; carry intent in names | keep comments that explain why |
| Duplicated logic | the same logic in three or more places | one shared function | do not merge code that is identical by accident or expected to diverge |
| Worthless wrapper | a one-line pass-through with no meaning of its own | inline it | a wrapper that names a concept or forms a test boundary is not worthless |
| Magic number | literals of unclear meaning | a named constant | do not move computation between compile time and run time |
| Stacked negation | `if (!(!a && !b))` | De Morgan's laws | confirm the truth tables match |
| Pointless intermediate variable | used once; its name adds nothing | inline it | do not change evaluation timing or the number of side effects |

Code that looks unused is not in this table. It is reported, never deleted (see the rules in
`SKILL.md`).

## Traps that are not improvements

| Temptation | Why it is a trap |
|---|---|
| inline every abstraction to flatten the code | a named abstraction aids understanding |
| shorten by removing error handling | error behavior is part of the contract; that is a behavior change |
| adopt a style better than the project's convention | inconsistency slows reading of the whole codebase |
| compress into one-liners to cut lines | dense lines are slower to read; line count is not the measure |
| rewrite a hot path for readability | unmeasured slowdown; hold it (step 4) |
