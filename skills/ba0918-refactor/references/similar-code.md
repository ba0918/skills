# Similar code

Read in step 6, when an improvement is to be carried to other sites. Finding a site that looks
the same is the easy part; this file is about judging whether the same transformation keeps
behavior there.

## Searching

- Search wide within the scope's language and related directories, and leave the decision to
  the judgment below. Missing a site costs less than wrongly applying to one, but a narrow
  search skips the judgment altogether.
- Prefer a structural search — a clone detector or a syntax-aware search tool, if available —
  over plain text search. Text search matches strings and comments too and returns more false
  matches, so judge its results more conservatively. Note in the report which kind of search
  was used.

## Judging each site

Read the whole file around each site; do not judge from the matching lines alone. Then ask:

1. **Same contract.** After the transformation, are return values, errors, side effects, their
   count and order, and short-circuit or lazy evaluation all unchanged?
2. **Same context.** Is the site used the way the original was? If the value comes from external
   input, or the site is a public API, a serialization boundary, or a reflection target where
   the original was not, the same change means something different. Follow callers back to the
   function's entry, not just the lines around the match.
3. **Deliberate difference.** Does a comment, the history, or a test say this shape is on
   purpose — a compatibility shim, a branch planned to diverge, a pinned behavior?
4. **A check exists.** Does a test, type check, build, lint, or characterization test cover
   this site? The rule from step 3 applies here too.
5. **Performance.** If the change could alter evaluation order, call counts, allocation, or
   complexity, is this site performance-sensitive, or unknown? Then it is uncertain.
6. **Convention.** Does the transformation match the idiom of the code around this site?

## Verdicts

| Verdict | Meaning | Treatment |
|---|---|---|
| safe | every question above lands on the safe side, and the reason fits in a sentence or two | listed for the person's agreement, then applied as in step 5 |
| not applicable | looks the same but a question shows it cannot or should not change | not applied; the reason is recorded |
| uncertain | the context needed to decide is missing | not applied; reported with what the person would need to decide |

Every verdict carries its reason. A "safe" whose reason cannot be written is uncertain. A site
may move from safe to uncertain as you learn more, never the other way without new evidence
such as an added check — a wrong application costs more than a skipped improvement.

## Example

Improvement: split `export(asPdf: bool)` into `exportPdf()` and `exportCsv()`.

| Site | Context | Verdict | Reason |
|---|---|---|---|
| `services/invoice.ts:88` | internal call with a literal `true`; tests cover it | safe | same use as the original, and a test pins the behavior |
| `api/public_export.ts:12` | the flag comes from a query parameter | uncertain | splitting ripples into a public API; needs the person's decision |
| `legacy/report.ts:30` | preceded by a comment marking it for removal after a migration | not applicable | temporary code; not worth changing |
