- [x] Confirm workflow failure mode for run #82
- [x] Patch publish workflow so optional private dispatch cannot invalidate the release run
- [x] Validate workflow syntax and summarize the root cause

Review:
- `python -c 'import yaml, pathlib; yaml.safe_load(...)'` confirms `.github/workflows/publish.yml` remains valid YAML after the fix.
- Run `#82` failed before any job started, which is consistent with GitHub rejecting the workflow definition rather than a runner-side shell error.
- The dispatch step now skips safely inside the shell when `POLLYWEB_AWS_DISPATCH_TOKEN` is absent, so PyPI publish success is no longer coupled to a workflow-time secret check.
