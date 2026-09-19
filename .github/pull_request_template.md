## Summary

<!-- Brief description of what this PR does and why -->

## Changes

-

## Checklist

### General
- [ ] PR title is concise and descriptive
- [ ] No secrets, credentials, or API keys are committed

### Python
- [ ] `ruff check` passes with no warnings
- [ ] New/changed endpoints have tests and all pass with `pytest`
- [ ] Pydantic models are used for request/response validation

### Terraform (infrastructure)
- [ ] `terraform fmt -check` passes
- [ ] `terraform validate` passes
- [ ] Plan output reviewed — no unintended resource destroys or replacements
