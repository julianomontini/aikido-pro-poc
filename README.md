# Aikido Pro POC — DevSecOps Pipeline Exercise

A hands-on scaffold for validating **Aikido Pro (free plan)** against a realistic-ish GitHub Actions pipeline: SAST, SCA, and DAST, plus secrets scanning as a bonus.

## What this is

- A small Flask app — "Internal Reports Manager" — that stores reports and lets users search, export, and restore them from backup.
- A GitHub Actions pipeline scaffold: build/test is fully wired up; the **security jobs are stubs** you fill in.
- `REQUIREMENTS.md` — the actual assignment: specific vulnerable scenarios to implement (so Aikido has something real to find) and specific pipeline integration steps to wire up yourself.

## What's done for you (boilerplate)

- Flask app factory, routing skeleton, SQLite schema/seed data (12 sample reports), health check
- `scripts/seed.py` — (re)seed or reset the sample reports on demand
- `pyproject.toml` (Poetry) with the runtime deps pinned; a `poetry.lock` section below explains the one manual step
- `Dockerfile`, `docker-compose.ci.yml` for local runs, `render.yaml` for a free Render deploy — all Poetry-based
- `ci.yml` — install deps via Poetry, run tests (nothing security-related)
- `security.yml` — job skeleton (names, triggers, `permissions:` block, job dependencies) with `TODO` markers where the actual scanning/gating goes
- `.github/dependabot.yml`
- pytest smoke tests, including a scaffold-integrity test that starts **failing** once you've implemented a scenario — that's expected, see below

## What you implement

Everything in `REQUIREMENTS.md`: five SAST-relevant code paths, three SCA dependency pins, four DAST-relevant app behaviors, one secrets-scanning scenario, and four pipeline integration points connecting the repo/app to Aikido. Each requirement has an ID (e.g. `SAST-1`), a file:function pointer, a hint (not a solution), an acceptance check, and doc links.

## Running locally

Needs [Poetry](https://python-poetry.org/docs/#installation) installed once (`pipx install poetry`, or `curl -sSL https://install.python-poetry.org | python3 -`).

```bash
poetry install         # first run also generates poetry.lock -- see note below
poetry run flask --app app.main run --debug
curl localhost:5000/health
```

```bash
poetry run pytest
```

The app seeds itself with 12 sample reports on first run (see `app/db.py`). If you already had the original 3-report DB from before this script existed, or you just want a clean slate, run:

```bash
poetry run python scripts/seed.py            # adds any seed reports not already present
poetry run python scripts/seed.py --reset    # wipes data/reports.db and reseeds from scratch
```

Both are idempotent and safe to rerun.

### About `poetry.lock`

This scaffold ships **without** `poetry.lock` — a hand-written lock file would have fake package hashes, and Aikido/pip-audit need the real ones. Run `poetry install` once locally (or `poetry lock`) and commit the `poetry.lock` it generates as your first commit. From then on, `poetry add <package>==<version>` (used throughout `REQUIREMENTS.md#SCA`) updates it automatically — commit the updated lock file every time.

## Suggested order of work

1. Create your Aikido account (free plan) and connect this repo **before** writing any vulnerable code, so you can watch findings appear as you introduce them: https://help.aikido.dev/getting-started/setting-up-your-account/create-account-and-connect-your-repositories
2. Work through `REQUIREMENTS.md` §SAST, committing one scenario at a time — small diffs make it obvious which commit Aikido flagged.
3. Work through §SCA.
4. Deploy to Render (`render.yaml` is ready — at render.com choose "New +" → "Blueprint" and point it at this repo), then work through §DAST once the app has a public URL.
5. Work through §Pipeline — this is where you decide what actually blocks a merge.
6. Optional but the actual point of the exercise: go back and fix each finding, then re-scan and watch it clear.

## A note on the free plan

Aikido's own marketing/pricing pages weren't fully consistent about which pipeline features (PR gating, release gating, full Surface Monitoring modes) are free vs. paid. See `REQUIREMENTS.md` §Pipeline for what could be confirmed and what you'll need to check live in your own dashboard. Treat "this is gated behind an upgrade" as a valid, useful finding for the POC — not a failure of the exercise.
