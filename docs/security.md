# Security

This page documents Shrd's security posture, how to audit dependencies, and the status of bundled assets as of **July 2026**.

## Summary

| Area                        | Status              | Notes                                        |
| --------------------------- | ------------------- | -------------------------------------------- |
| Python runtime dependencies | **No known CVEs**   | `Django>=4.2` only; audited with `pip-audit` |
| Dev / docs dependencies     | **No known CVEs**   | pytest, ruff, mkdocs-material, pre-commit    |
| Bundled HTMX                | **Current**         | Shipped `2.0.9` (latest stable 2.x)          |
| Bundled Alpine.js           | **Current**         | Shipped `3.15.12` (latest stable 3.x)        |
| Application surface         | **Standard Django** | No extra DB tables; state in Django cache    |

Shrd adds no middleware and no background workers. Security boundaries are the same as a typical Django app: escape untrusted content, validate action payloads, and restrict view-data component whitelists.

## Auditing Python dependencies

Install dev dependencies and run [pip-audit](https://pypi.org/project/pip-audit/):

```bash
pip install -e ".[dev,docs]"
pip install pip-audit
pip-audit
```

As of the last audit (July 2026), the project reported **no known vulnerabilities** in:

- `Django` (runtime)
- `pytest`, `pytest-django`, `pytest-cov` (dev)
- `ruff`, `pre-commit` (dev)
- `mkdocs-material` (docs)

### Runtime dependency policy

Shrd intentionally keeps a **single runtime dependency** on Django. This limits supply-chain exposure and makes security review straightforward.

When upgrading Django in your project, follow [Django's security release notes](https://docs.djangoproject.com/en/stable/releases/security/). Shrd supports Django 4.2 through 6.x (see `pyproject.toml` classifiers).

## Bundled JavaScript assets

Shrd ships HTMX and Alpine.js as static files under `shard/static/shard/js/`. No CDN is required at runtime.

| Asset           | Bundled version | Latest stable (Jul 2026) | Gzip size |
| --------------- | --------------- | ------------------------ | --------- |
| `htmx.min.js`   | 2.0.9           | 2.0.9                    | ~16 KB    |
| `alpine.min.js` | 3.15.12         | 3.15.12                  | ~16 KB    |
| `shard.js`      | —               | —                        | <1 KB     |

Check bundled versions locally:

```bash
# HTMX exposes version in the minified bundle
rg -o 'version:"[0-9.]+"' shard/static/shard/js/htmx.min.js

# Alpine version (requires Node or a browser)
node -e "const fs=require('fs'); global.window={}; eval(fs.readFileSync('shard/static/shard/js/alpine.min.js','utf8')); console.log(window.Alpine.version)"
```

### HTMX security notes

- HTMX increases HTML expressiveness. **Always escape user-supplied content** in templates. Django's default auto-escaping is your first line of defense.
- Shrd actions are **POST-only**; there are no GET endpoints for state mutation.
- For untrusted HTML fragments, use HTMX's [`hx-disable`](https://htmx.org/attributes/hx-disable/) attribute to prevent attribute processing inside that subtree.
- HTMX 2.x is the supported major version. Version 4.x is in beta; Shrd will evaluate it after a stable release.

No library-level CVEs affect the bundled HTMX 2.0.4 runtime as of July 2026.

### Alpine.js security notes

- Alpine evaluates expressions from HTML attributes. Keep `get_client_state()` values server-controlled; do not pass raw user input into Alpine seed data.
- For strict Content Security Policy (CSP) without `unsafe-eval`, consider Alpine's [CSP build](https://alpinejs.dev/advanced/csp). Shrd does not yet ship this variant; see the [roadmap](roadmap.md).
- Alpine 3.15.x includes CSP evaluator hardening (short-circuit fixes, assignment guards). Updating from 3.14.8 is recommended when asset budgets allow.

## View data security

View data can instantiate components by name from structured data. **Always use a whitelist:**

```python
# Per-call whitelist (preferred for dynamic data)
render_view_data(tree, allowed_components=frozenset({"Card", "Counter"}))

# Or global setting
SHARD_VIEW_DATA_ALLOWED_COMPONENTS = ["Layout", "Card", "Counter"]
```

Never pass user-controlled component names without validation. `ViewDataError` is raised when no whitelist is configured.

## Cache and state

Component state (props, server state, slots) is stored in Django's cache backend. In production:

- Use a shared cache (Redis, Memcached) if you run multiple app servers.
- Set `SHARD_STATE_TIMEOUT` appropriately for your session model.
- Treat cache entries as sensitive if component state contains PII.

## CI and release tooling

GitHub Actions workflows use pinned major versions (`actions/checkout@v4`, `actions/setup-python@v5`). Pre-commit hooks pin tool versions in `.pre-commit-config.yaml`.

Recommended additions (tracked on the [roadmap](roadmap.md)):

- `pip-audit` in CI on every PR
- Dependabot for GitHub Actions and pre-commit hook revisions
- Automated checks that bundled JS versions match documented versions

## Reporting vulnerabilities

If you discover a security issue in Shrd:

1. **Do not** open a public GitHub issue for exploitable vulnerabilities.
2. Email the maintainers or use GitHub's private security advisory flow on [kurtisrogers/Shard](https://github.com/kurtisrogers/Shard/security/advisories).
3. Include reproduction steps, affected versions, and impact assessment.

We aim to acknowledge reports within 72 hours and publish fixes or mitigations as soon as practical.

## Security checklist for Shrd apps

- [ ] `CACHES['default']` configured for your deployment topology
- [ ] `shard_doctor` passes in each environment
- [ ] View data uses an explicit component whitelist
- [ ] User input is escaped in templates (default Django behavior)
- [ ] Action handlers validate and authorize payloads in `before_action`
- [ ] Production uses HTTPS and standard Django security settings (`SECURE_*`, CSRF)
- [ ] `SHARD_STATE_TIMEOUT` matches your data retention policy
