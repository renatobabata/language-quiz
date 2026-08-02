# ADR 0002: Pin third-party GitHub Actions by commit SHA, not by version tag

## Status
Accepted

## Context
While setting up the CI pipeline, the `aquasecurity/trivy-action@0.24.0` step
failed to resolve. Investigation revealed this was not a configuration
mistake: on March 19, 2026, a threat actor with compromised credentials
force-pushed 75 of 76 version tags in the `aquasecurity/trivy-action`
repository (tags `0.0.1` through `0.34.2`) to point at malicious commits,
turning trusted version references into a credential-stealing supply chain
attack (tracked as CVE-2026-33634, GHSA-69fq-xp46-6x23). The compromised
action read GitHub Actions runner memory and exfiltrated secrets — SSH keys,
cloud credentials, Docker/Kubernetes tokens — to an attacker-controlled
domain. The same campaign also compromised `aquasecurity/setup-trivy` and
published a malicious `trivy` binary release (`v0.69.4`).

The exposure window was approximately 12 hours (March 19, ~17:43 UTC to
March 20, ~05:40 UTC). This project's own CI runs happened well outside that
window, so no evidence of impact — but the underlying risk (a Git tag is a
mutable pointer; anyone with push access can force it to point anywhere) is
permanent and applies to any third-party action pinned by tag, not just
Trivy.

## Decision
Pin every third-party GitHub Action used for anything security- or
infrastructure-critical to an immutable **commit SHA**, not a version tag.
The SHA is documented with a trailing comment noting the human-readable
version it corresponds to, e.g.:

```yaml
uses: aquasecurity/trivy-action@57a97c7e7821a5776cebc9bb87c984fa69cba8f1 # v0.35.0
```

For `trivy-action` specifically, the commit `57a97c7e7821a5776cebc9bb87c984fa69cba8f1`
is the verified-safe commit that both the clean `v0.35.0` tag and the GitHub
security advisory point to.

## Consequences
- Dependabot/Renovate-style automatic action updates require slightly more
  care (they need to resolve and verify the new SHA, not just bump a tag
  number), but this is a small cost against the alternative.
- SHA pins need to be manually refreshed when intentionally upgrading an
  action version — this is a deliberate trade-off: an explicit, reviewed
  action is safer than an implicit, automatic one for CI-critical
  dependencies.
- This pattern should be applied going forward to any new third-party action
  added to the pipeline (e.g. future deploy or monitoring integrations), not
  retrofitted only where an incident already happened.
