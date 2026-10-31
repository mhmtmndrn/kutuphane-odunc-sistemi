# AGENTS.md

Web-based book lending system for a small library, used by library staff only: members, books and copies, loans and returns, late fees.

## Conventions

- Development is test-driven: write a failing test before the code that makes it pass.
- Commit messages follow Conventional Commits (`feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`), in English.
- Work on feature branches (`feature/<name>`) and merge them into `main`; do not commit directly to `main`.

## Documents and decisions

- `docs/STATUS.md` is the handoff note: read it first, and update it at milestones.
- Decisions are recorded as ADRs in `docs/decisions/`, from `0000-adr-template.md`. Do not reopen a recorded decision without saying why.
- Research reports go to `docs/research/YYYY-MM-DD-<topic>.md`, task plans to `docs/plans/YYYY-MM-DD-<topic>.md`.

## Language

- Documents are written in Turkish; code, comments, identifiers and commit messages in English.
