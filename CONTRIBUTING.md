# Contributing Guide

This is a solo learning project, but it follows real team conventions on
purpose — the goal is to practice professional DevSecOps workflows.

## Workflow

1. Every change starts as an issue on the [project board](#), assigned to an
   Epic.
2. Create a branch from `main`: `feat/short-description`, `fix/short-description`,
   or `chore/short-description`.
3. Commit using [Conventional Commits](https://www.conventionalcommits.org/):
   `feat:`, `fix:`, `chore:`, `docs:`, `ci:`, `test:`.
4. Open a Pull Request into `main`. The CI pipeline (lint, test, build, security
   scan) must pass before merging.
5. Squash-merge into `main`. `main` is always deployable — merging triggers an
   automatic deployment to production.

## Code Style

- Python code is formatted and linted with `ruff`.
- All code comments, docstrings, commit messages, and documentation are written
  in English.
- Type hints are required for all new functions.

## Architecture Decisions

Any decision with long-term impact (choice of library, infrastructure pattern,
data model change) should be recorded as an ADR in `docs/adr/`. Copy the
existing format from `docs/adr/0001-tech-stack-selection.md`.

## Security

- Never commit secrets, API keys, or `.env` files.
- Every Docker image is scanned with Trivy before being pushed to the registry.
- Dependency versions are pinned in `requirements.txt`.
