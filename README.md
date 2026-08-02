# Language Quiz

An AI-powered web application that helps students practice reading comprehension
and vocabulary in any language. Students paste a text and the system generates
four types of study exercises: a multiple-choice quiz, a fill-in-the-blank
(cloze) exercise, vocabulary flashcards, and a crossword puzzle.

## Status

🚧 Project in active development. See the [GitHub Project board](#) for current
progress and [docs/architecture.md](docs/architecture.md) for the system design.

## Features

- Paste any text and get exercises generated on demand
- Choice of AI provider per request: **Gemini** (Google) or **Groq** (Llama)
- **Quiz**: 5 multiple-choice questions, with immediate right/wrong feedback
- **Cloze**: 5 sentences from the text with a key word missing, plus a hint
- **Flashcards**: 5 key vocabulary items
  - For Japanese/Chinese texts: choose the correct hiragana/pinyin reading
    among 4 options
  - For other languages: choose the correct synonym among 4 options
- **Crossword**: puzzle built from key vocabulary in the text (custom layout
  algorithm, not AI-generated)
- Final results chart showing correct vs. incorrect answers across all exercises

## Tech Stack

- **Backend:** Python 3.12, FastAPI
- **Frontend:** Server-rendered templates (Jinja2) + vanilla JavaScript
- **Database:** SQLite
- **AI providers:** Google Gemini API, Groq API
- **Infrastructure:** Terraform, Google Cloud Platform (Compute Engine e2-micro,
  Always Free tier)
- **CI/CD:** GitHub Actions (lint → test → build → security scan → deploy)
- **Monitoring:** Prometheus + Grafana Cloud (free tier)

See [docs/adr/](docs/adr/) for the reasoning behind these choices.

## Local Development

Setup instructions will be added once the application skeleton exists (see
project board, Epic 3).

## Documentation

- [Architecture overview](docs/architecture.md)
- [Architecture Decision Records](docs/adr/)
- [Contributing guide](CONTRIBUTING.md)

## License

MIT — see [LICENSE](LICENSE).
