# Upstream patch provenance

This directory holds the reviewable, repository-owned representation of the
small patches applied to **external** pinned SGLang and Mooncake checkouts. It
does not vendor either upstream repository and is not a third implementation
of their code.

`manifest.json` is the index. Every series has one upstream checkout, one full
base commit, one execution order, a directory for its mail patches, and the
commands that later prove it can be applied. The current three entries are
`PLANNED`: their fixed source seams are known, but no upstream code, focused
test, or runtime artifact exists yet. An empty planned directory is therefore
an honest reservation, **not** a patch artifact and not an
`IMPLEMENTED_UNVALIDATED` claim.

## Materialization rule

The author of a later Mooncake observation, SGLang trace-only, or SGLang
behavior change must do all of the following in the same task that introduces
the actual upstream change:

1. Start from the manifest's exact `upstream.commit` in a clean external
   checkout. Do not rebase the change onto an unrecorded source revision.
2. Keep instrumentation and behavior changes in separate upstream commits and
   run their focused upstream tests before exporting anything.
3. Export the ordered commit range with `git format-patch` into the declared
   `patch_directory`. Add each relative `.patch` path and its SHA-256 digest to
   `patches`, then change only that series from `PLANNED` to `MATERIALIZED`.
4. In a fresh disposable worktree at the same base commit, apply the listed
   files in order with the manifest's `apply_command`, run the declared focused
   tests, and retain the command output in the relevant G0 run bundle. If
   `git am` fails, run the listed `abort_command`; do not hand-edit the patch
   result until the cause is understood.
5. Record the resulting upstream HEAD and test command/output in the run
   `manifest.json`. A patch file alone is not runtime validation.

The intended export shape is:

```bash
git -C "$CHECKOUT" format-patch --no-stat \
  --output-directory "$REPO_ROOT/<patch_directory>" \
  "$BASE_SHA"..HEAD
```

The follow-up manifest entry must list the generated files in the order passed
to `git am`; shell glob order is not a provenance contract.

## What this proves—and what it does not

The repository test only proves that the declared planned series are tied to
the correct full source commits, isolated by upstream, and cannot be mistaken
for existing patches. It does not clone an upstream checkout, apply a patch,
or prove a runtime behavior. Those become required evidence only after a
series is materialized under T6 or T7; stock T5 remains unpatched.
