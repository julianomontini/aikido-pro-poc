# Requirements — Aikido Pro POC

This is the assignment. Everything below is something *you* implement — the scaffold gives you a place to put it and a stub that fails loudly (`501 not implemented`, or `NotImplementedError`) until you do.

Work one requirement at a time, commit, push, and check what Aikido reports before moving to the next one. That mapping — "this commit, this finding" — is the actual point of the exercise, more than the finished app.

## Prerequisites

| Need | Notes |
|---|---|
| Poetry installed locally | `pipx install poetry` or https://python-poetry.org/docs/#installation |
| `poetry.lock` generated | Run `poetry install` once — it's not shipped with the scaffold (see README.md). Commit it before your first push; Aikido/pip-audit read this file, not `pyproject.toml`, for exact resolved versions. |
| GitHub repo (public) pushed from this scaffold | `git init && git add -A && git commit -m "scaffold" && gh repo create --public --source=. --push` (or do it by hand) |
| Aikido account, free plan | https://app.aikido.dev/login/sign-up — sign up with the GitHub account that owns the repo, it simplifies the connect step |
| Repo connected to Aikido | GitHub App install, not a token in the repo: https://help.aikido.dev/code-scanning/connect-your-source-code/connect-github-account-to-aikido |
| Render account (free) | For §DAST — https://render.com, sign up with GitHub |

---

## §SAST — five scenarios

Static analysis reads code, never runs it. Each of these is a real, well-known vulnerability class — implement the *insecure* version first so Aikido has something to catch, then optionally come back and fix it once you've seen the finding.

### SAST-1 — SQL injection
**Where:** `app/routes/reports.py :: search_reports()`
**Do:** Implement search over the `reports` table by `title`/`body` using the `q` query-string param, returning matches rendered via `app/templates/search_results.html`. Build the SQL by putting `q` directly into the query string rather than using a parameterized query (`?` placeholders).
**Why it's realistic:** this is the single most common SAST finding in real codebases — an f-string or `%`-formatted query built from request input.
**Acceptance:** Aikido (or `semgrep --config p/python`) flags the query construction as SQL injection. A request like `?q=' OR '1'='1` should return every report, not just matches.
**Docs:** https://www.aikido.dev/code/static-code-analysis-sast · https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html

### SAST-2 — OS command injection
**Where:** `app/routes/reports.py :: export_report()`
**Do:** Export a report to the format given by the `fmt` query param by shelling out to a converter (e.g. build a string like `f"pandoc report_{report_id}.txt -o report_{report_id}.{fmt}"` and run it with `shell=True`, or `os.system(...)`). Don't validate/allowlist `fmt` first — that's the bug.
**Acceptance:** a request with `?fmt=txt; touch /tmp/pwned` (or similar) demonstrates command injection locally; Aikido flags `subprocess`/`os.system` usage with unsanitized input.
**Docs:** https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html

### SAST-3 — Path traversal
**Where:** `app/routes/files.py :: get_attachment()`
**Do:** Serve `filename` from `ATTACHMENTS_DIR` by joining the path directly (`ATTACHMENTS_DIR / filename` or `os.path.join`) and reading/returning the file, without checking that the resolved path stays inside `ATTACHMENTS_DIR`.
**Acceptance:** `GET /attachments/..%2f..%2f..%2fetc%2fpasswd` (URL-encoded `../`) escapes the intended directory locally; Aikido/Semgrep flags unsanitized path construction from user input.
**Docs:** https://cheatsheetseries.owasp.org/cheatsheets/Path_Traversal_Cheat_Sheet.html

### SAST-4 — Insecure deserialization
**Where:** `app/routes/files.py :: restore_backup()`
**Do:** Accept an uploaded file (form field `backup`) describing reports to restore, and load it with `pickle.loads(data)` on the raw uploaded bytes — no check on where those bytes came from. `pickle` is stdlib, so this needs no extra dependency and no compiler.
**An alternative, if you have a C compiler available:** `yaml.load(data)` (no `Loader=`, or `Loader=yaml.Loader`, not `yaml.safe_load`) is the classic version of this same bug, and pairs naturally with an old, vulnerable `PyYAML` pin for SCA-1 — a SAST finding (unsafe `yaml.load` call) and an SCA finding (the vulnerable package version) describing the same real risk from two angles. This scaffold defaults to `pickle` instead because PyYAML's pre-5.4 releases need to compile a C extension from source on Windows (`Microsoft Visual C++ 14.0 or greater is required`) unless you install the free Build Tools for Visual Studio first — see the note under SCA-1.
**Acceptance:** Aikido flags `pickle.loads` (or `yaml.load` without a safe loader, if you went that route) on untrusted/request-derived input as arbitrary code execution risk.
**Docs:** https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html

### SAST-5 — Weak/broken cryptography
**Where:** `app/auth.py :: hash_password()` / `verify_password()`
**Do:** Hash passwords with `hashlib.md5()` or `hashlib.sha1()`, unsalted, and compare with `==` in `verify_password`. Wire these into a minimal `POST /auth/register` and `POST /auth/login` if you want the full loop — not required for the finding itself, the hash functions alone are enough for SAST to flag.
**Acceptance:** Aikido flags MD5/SHA1 use for password hashing (weak/broken hash algorithm).
**Docs:** https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html

---

## §SCA — three dependency pins

SCA never reads your code — it reads `pyproject.toml`/`poetry.lock`. Perfectly-written code is still vulnerable if it imports a bad version. Your job here is research, not code: find *real* CVEs (don't invent version numbers) and pin to an affected version with `poetry add package==<version>` (this updates both files — commit both).

### SCA-1 — `Jinja2`
Pin `Jinja2==3.1.2` — vulnerable to [CVE-2024-22195 / GHSA-h5c8-rqwp-cp95](https://github.com/advisories/GHSA-h5c8-rqwp-cp95) (HTML attribute injection via the `xmlattr` filter, fixed in 3.1.3). It's already a Flask dependency (Flask 3.0.x requires `Jinja2>=3.1.2`), so pinning the floor version is enough — no new package, no compiler, nothing else to install. It's also the templating engine behind DAST-4's reflected-XSS scenario, worth noticing as you go: an SCA finding (a vulnerable version) and a DAST finding (how the app actually uses the template) pointing at the same general risk area from different angles.

**If you'd rather use PyYAML for this** (the more classic "vulnerable deserialization library" pick, and what SAST-4 originally paired with): any version before 5.4 needs to compile a C extension from source on Windows, which fails with `Microsoft Visual C++ 14.0 or greater is required` unless you install the free [Build Tools for Visual Studio](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (just the "Desktop development with C++" workload) first. If you've done that: `poetry add PyYAML==5.3.1` ([GHSA-8q59-q68h-6hv4](https://github.com/advisories/GHSA-8q59-q68h-6hv4)), and use the `yaml.load()` variant of SAST-4 instead of `pickle.loads()`.
**Look it up (if picking a different package/version entirely):** https://osv.dev/list?ecosystem=PyPI · https://github.com/advisories

### SCA-2 — `requests`
Find a version of `requests` with a known CVE (credential/header leakage on redirect is a well-known one) and `poetry add requests==<that version>`.
**Look it up:** https://osv.dev/list?ecosystem=PyPI&q=requests

### SCA-3 — your choice
Pick one more Python package this app could plausibly use (e.g. `Jinja2`, `Pillow`, `urllib3`) and pin a version with a real, documented CVE the same way.
**Look it up:** https://osv.dev · https://github.com/advisories

**Acceptance for all three:** `poetry run pip-audit --strict` (audits the active Poetry environment directly — no need to export a requirements file) exits non-zero locally, and Aikido's dependency scan lists all three with CVE IDs, not just version warnings.
**Docs:** https://www.aikido.dev/pricing (confirms SCA/dependency scanning + reachability analysis is on the free plan) · https://help.aikido.dev · https://python-poetry.org/docs/cli/#add

---

## §DAST — four scenarios

DAST only sees what's reachable over HTTP on a *running, deployed* app — this is why these live in app behavior/config, not in a code diff a reviewer would catch. You need the Render deploy (see Prerequisites) working before any of these are checkable by Aikido.

### DAST-1 — Broken access control
**Where:** `app/routes/admin.py :: stats()`
**Current state:** already ships with no auth check at all — that's the vulnerability, nothing to add. Confirm a DAST scan (or just `curl` the deployed `/admin/stats` yourself) reaches it unauthenticated.
**Then implement the fix:** write `require_admin()` in `app/auth.py` (a decorator checking a bearer token against an admin user's stored token) and apply it to `stats()`. Re-scan and confirm the finding clears.
**Docs:** https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html

### DAST-2 — Debug mode / verbose errors in a deployed environment
**Where:** `app/config.py`
**Do:** Set `DEBUG = True` for the deployed (Render) environment — e.g. hardcode it, or default an env var to `"true"`. Trigger a 500 (an easy one: hit `/reports/999999/export?fmt=txt` before SAST-2 is implemented, or force one deliberately) and confirm the deployed app leaks a full traceback/file paths, not a clean error page.
**Then implement the fix:** make `DEBUG` false by default in anything that isn't local dev, redeploy, confirm the traceback disappears.
**Docs:** https://help.aikido.dev/dast-surface-monitoring/dast-surface-monitoring-overview

### DAST-3 — Missing security headers
**Where:** `app/main.py`
**Current state:** ships with zero security headers by design — leave it until you've seen a scan (Aikido Quick Scan, or `curl -I` your Render URL) flag the absence of `Content-Security-Policy`, `X-Content-Type-Options`, `Strict-Transport-Security`.
**Then implement the fix:** add an `after_request` hook (or `flask-talisman`) setting at least those three headers, redeploy, confirm they show up in the response and the scan finding clears.
**Docs:** https://cheatsheetseries.owasp.org/cheatsheets/HTTP_Headers_Cheat_Sheet.html

### DAST-4 — Reflected XSS
**Where:** `app/templates/search_results.html`, wired from SAST-1's `search_reports()`
**Do:** Render the search query `q` back onto the results page using `{{ q|safe }}` (or string-concatenate it into raw HTML) instead of plain `{{ q }}` — Jinja2 autoescapes by default, so you have to deliberately opt out, which is exactly how this bug happens in real apps (a developer adds `|safe` to fix a display quirk and reopens XSS).
**Acceptance:** `?q=<script>alert(1)</script>` reflects unescaped into the page; a DAST scan (ZAP or Aikido) flags reflected XSS.
**Docs:** https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html

---

## §Secrets — bonus scenario

### SEC-1 — a hardcoded credential
Add one **obviously fake** credential-shaped string somewhere plausible (e.g. a `THIRD_PARTY_API_KEY = "sk_live_..."`-looking constant in `app/config.py`, or in a throwaway `scripts/notify_slack.py`). It must not be a real key to any real service — the point is to trigger pattern-based secret detection, not to leak anything.
**Acceptance:** Aikido's secrets scan (or `gitleaks detect`) flags it. Then remove it and replace with `os.environ.get(...)`, and confirm the finding is marked resolved on the next scan — practicing what "rotate and remove" actually looks like in the tooling, even though this particular key was never real.
**Docs:** https://help.aikido.dev (secrets detection is listed as included on the free plan across every pricing summary I could find)

---

## §Pipeline — connecting it all to Aikido

`security.yml` in this repo is a skeleton with four `TODO` jobs. This section is what goes in each — plus an honest note on where I couldn't confirm free-plan availability from Aikido's public docs/pricing pages, which were inconsistent with each other.

### PIPE-1 — Confirm connected-repo scanning
No code. In the Aikido dashboard, confirm SAST/SCA/secrets findings are appearing for this repo automatically (this is agentless — Aikido pulls on its own schedule plus on push, no CI step required). This is clearly free-plan (confirmed consistently across Aikido's pricing page and third-party summaries).
**Docs:** https://help.aikido.dev/getting-started/setting-up-your-account/create-account-and-connect-your-repositories

### PIPE-2 — PR Gating
Try enabling PR Gating for this repo (native GitHub integration — Aikido posts a status check on the PR, no runner minutes used). **What I could confirm:** Aikido's own pricing page lists dependency/SAST/secrets scanning as free-plan features but doesn't clearly place PR Gating on the free tier — some third-party pricing summaries put "PR security review" on the paid Basic tier and up. **What to do:** try it, and record in `security.yml`'s `sast`/`sca` job comments what you actually see — either a working status check, or an upgrade prompt. Both are a valid, reportable POC outcome.
**Docs:** https://help.aikido.dev/pr-and-release-gating/aikido-ci-gating-functionality · https://help.aikido.dev/pr-and-release-gating/github-ci-pr-gating-via-aikido-dashboard

### PIPE-3 — Point Surface Monitoring at the Render URL
In the Aikido dashboard, add your Render app's URL as a monitored domain (free plan's fair-usage limit is 1 domain, which is exactly what this POC needs). Start with a **Quick Scan** (passive — headers, cookies, JWT config) since that's the mode explicitly described as free-tier-appropriate in Aikido's docs. Try switching to **Attack Surface Scan** or **Agentic Scan** and note whether your account can access them — third-party pricing summaries suggest deeper "attack surface monitoring" may be Pro-gated, but Aikido's own docs don't say so explicitly.
**Note:** Render's free tier spins the app down after ~15 min idle. If Aikido reports the domain unreachable, `curl` it once to wake it up before rescanning — a known free-tier quirk, not a bug in your app.
**Docs:** https://help.aikido.dev/dast-surface-monitoring/dast-surface-monitoring-overview · https://help.aikido.dev/dast-surface-monitoring/attack-surface-scanning · https://www.aikido.dev/scanners/surface-monitoring-dast

### PIPE-4 — Release Gating (CLI, in `security.yml`)
Implement the `release-gate` job: install `@aikidosec/ci-api-client`, generate an API key (Aikido dashboard → **Settings → Integrations → Continuous Integration**), store it as the `AIKIDO_CLIENT_API_KEY` repo secret, and call `scan-release` against `$GITHUB_SHA`, failing the job above your chosen severity threshold. **What I could confirm:** this is documented with a working GitHub Actions example, but I could not confirm from public docs whether it functions on the free plan or requires Basic/Pro. Wire it up per the docs below and record what actually happens when it runs — that observation is itself part of the deliverable.
**Docs:** https://help.aikido.dev/pr-and-release-gating/cli-for-pr-and-release-gating/github-action-setup-for-aikido-cli-release-gating · https://github.com/AikidoSec/ci-api-client
**Reference shape** (fill in the real flags/threshold once you've read the docs above):
```yaml
- run: npm install --global @aikidosec/ci-api-client
- run: |
    aikido-api-client scan-release ${{ github.event.repository.name }} \
      $GITHUB_SHA \
      --apikey ${{ secrets.AIKIDO_CLIENT_API_KEY }} \
      --fail-on-sast-scan \
      --fail-on-secrets-scan
```

---

## Acceptance checklist

- [ ] SAST-1..5 implemented, each visible as a distinct commit, each flagged by Aikido
- [ ] SCA-1..3 pinned to real CVEs, all three flagged with CVE IDs
- [ ] DAST-1..4 each reproduced against the Render deployment, then remediated, then reconfirmed clear
- [ ] SEC-1 added, flagged, then removed/rotated and reconfirmed clear
- [ ] PIPE-1..4 attempted; `security.yml` TODOs replaced with real steps or an honest note on what's plan-gated
- [ ] `tests/test_scaffold.py`'s stub assertions deleted/updated as each SAST scenario is implemented

## Suggested rollout (once everything above works)

Don't flip every gate to blocking on day one — that's the usual way these programs die. A reasonable order, borrowed from standard DevSecOps rollout advice: report-only for a week → gate secrets and SCA first (lowest false-positive rate) → gate SAST on new/diffed code only, not the whole history → add DAST against staging, baseline/passive first → only then make checks required via branch protection.

## Doc index

- Aikido pricing (free vs. paid, read this yourself — it changes): https://www.aikido.dev/pricing
- Aikido vs. SonarQube (useful since you already run Sonar): https://www.aikido.dev/comparison/aikido-vs-sonarqube
- Aikido help center home: https://help.aikido.dev
- OWASP Cheat Sheet Series (used throughout above): https://cheatsheetseries.owasp.org
- OSV.dev vulnerability database: https://osv.dev
- GitHub Advisory Database: https://github.com/advisories
