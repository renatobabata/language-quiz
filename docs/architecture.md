# Architecture Overview

> This document will be expanded as each phase is implemented. It currently
> reflects the Phase 0 planning decisions.

## System Diagram (high level)

```
[Browser: text box + AI provider selector]
              |
              v
        [FastAPI backend] --- SQLite
              |
              v
   [AI Provider Abstraction Layer]
        /              \
  [Gemini API]      [Groq API]
              |
              v
   Exercise generators:
   - Quiz (multiple choice)
   - Cloze (fill in the blank)
   - Flashcards (reading/synonym choice)
   - Crossword (AI extracts words, custom algorithm builds the grid)
              |
              v
        [Results chart]

Infrastructure:
  Terraform -> GCP Compute Engine (e2-micro, Always Free)
  GitHub Actions -> lint/test/build/scan -> push image -> deploy over SSH
  Prometheus (app metrics) -> Grafana Cloud (free tier dashboards)
  Caddy -> HTTPS reverse proxy -> free subdomain (DuckDNS/Cloudflare)
```

## Key Design Decisions

See [docs/adr/](.) for full reasoning. Summary:

- **Single Python/FastAPI service**, no microservices — unnecessary complexity
  for a single e2-micro instance (1GB RAM).
- **AI provider abstraction**: exercise generation logic never calls Gemini or
  Groq SDKs directly; it goes through a common interface so the provider can be
  swapped per-request based on user selection.
- **SQLite over a managed database**: avoids running a second process on a
  memory-constrained VM.
- **Crossword layout is deterministic code, not AI-generated**: the AI only
  extracts vocabulary and clues; a custom algorithm places words on the grid.
- **Grafana Cloud instead of self-hosted Grafana**: avoids resource contention
  on the e2-micro instance (lesson learned from a previous project).

## Data Model (draft, to be refined in Epic 3)

- `Text`: submitted content, detected language, AI provider used
- `Exercise`: type (quiz/cloze/flashcard/crossword), generated data (JSON)
- `ExerciseAttempt`: student answers, score, per-exercise-type breakdown
