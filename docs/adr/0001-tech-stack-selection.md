# ADR 0001: Tech Stack Selection

## Status
Accepted

## Context
This is a from-scratch rebuild of an earlier prototype ("idioms-quiz"). The
previous project surfaced several operational lessons (dependency scanning
false positives, AI model deprecation, unstable third-party data sources,
Docker build caching pitfalls) that should inform decisions this time, rather
than being solved reactively again.

Requirements: fully free hosting (GCP Always Free tier), fully automated
deployment on push to `main`, choice between two AI providers per request,
monitoring dashboards, and Infrastructure as Code via Terraform.

## Decision
- **Backend**: Python 3.12 + FastAPI (consistent with the developer's existing
  skill set and target job market — SRE/DevOps roles that use Python tooling).
- **Frontend**: Server-rendered Jinja2 templates + vanilla JavaScript, no
  frontend build step. Keeps the Docker image small and avoids adding Node.js
  to the runtime environment, which matters on a 1GB RAM instance.
- **Database**: SQLite. No second database process competing for RAM on the
  e2-micro instance.
- **AI providers**: Google Gemini API and Groq API, both offering a genuinely
  permanent free tier (unlike DeepSeek, which only offers a 30-day free token
  grant). Accessed through a shared abstraction layer so a new provider can be
  added without touching exercise-generation logic.
- **Infrastructure**: Terraform provisioning a GCP Compute Engine `e2-micro`
  instance (Always Free tier), with **remote state in a GCS bucket from the
  first commit** — a previous project accumulated a manually-created VM
  alongside a Terraform-managed one due to skipping this early.
- **CI/CD**: GitHub Actions, authenticating to GCP via Workload Identity
  Federation instead of a long-lived service account key.
- **Monitoring**: Prometheus for metrics collection, shipped to **Grafana
  Cloud's free tier** rather than a self-hosted Grafana instance — running
  Prometheus, Grafana, and the application together on a single 1GB VM caused
  resource contention in the previous project.

## Consequences
- No horizontal scaling story — acceptable for a personal study project on a
  single free-tier VM.
- Two AI providers must be kept behind a common interface from day one, which
  adds a small amount of upfront design work but avoids a rewrite later.
- Remote Terraform state requires creating a GCS bucket manually once, before
  the first `terraform init` — documented as a manual bootstrap step.
