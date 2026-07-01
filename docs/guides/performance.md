# Performance & weight

Shard is designed to stay light. This page documents what it costs on the wire and on your server.

## Quick report

```bash
python manage.py shard_report
```

JSON output for tooling:

```bash
python manage.py shard_report --json
```

Fail CI when bundled assets exceed budgets:

```bash
python manage.py shard_report --check-budget
python manage.py shard_report --json --check-budget
```

## Client weight (default setup)

Shard ships three JavaScript files. Only two are required for most pages:

| Asset         | Gzip (approx.) | Required | Purpose                |
| ------------- | -------------- | -------- | ---------------------- |
| `htmx.min.js` | ~16 KB         | Yes      | Server-driven updates  |
| `shard.js`    | <1 KB          | Yes      | HTMX request glue      |
| `alpine.min.js` | ~16 KB       | No       | Client-side UI state   |

**HTMX-only page load:** ~17 KB gzip, **2 requests**

**With Alpine.js:** ~33 KB gzip, **3 requests**

No npm install, no build step, no CSS framework bundled.

## Loading scripts

```django
{# Default: HTMX + shard.js only (~17 KB gzip) #}
{% shard_scripts %}

{# Opt in to Alpine when you use get_client_state() or x-data #}
{% shard_scripts alpine=True %}
```

Or set globally:

```python
SHARD_LOAD_ALPINE = True
```

## Server weight

| Area | Cost |
| ---- | ---- |
| Python package | ~150 KB of code/templates (see `shard_report`) |
| Database | None — no migrations, no ORM models |
| Cache | One entry per mounted component instance |
| Per request | Template render + optional cache read/write |

Shard adds no middleware and no per-request overhead beyond what your components do.

## Optimizations built in

### Scoped CSS omitted from HTMX responses

Component styles are injected on **first render only**. HTMX action responses return HTML fragments without `<style>` tags, avoiding duplicate CSS on every interaction.

### Alpine is optional

Alpine.js is only loaded when you request it. Components that use only server state and HTMX do not pay the ~16 KB gzip cost.

### Minimal glue script

`shard.js` is under 1 KB. It only tags HTMX requests so the server can identify Shard actions.

### Scoped CSS minification

Component styles are minified by default before injection (`SHARD_MINIFY_CSS`). This reduces transfer size on first mount without a build step.

### Script preload hints

`{% shard_scripts %}` emits `<link rel="preload" as="script">` for HTMX and `shard.js` by default so browsers can fetch them earlier during HTML parse (`SHARD_PRELOAD_SCRIPTS`).

### Co-located CSS, not a global bundle

Styles are scoped per component and only included when that component mounts. There is no site-wide CSS payload from Shard.

## Tuning tips

1. **Skip Alpine** on pages that only use HTMX actions
2. **Keep component CSS small** — scoped styles still transfer on first mount
3. **Use Django's cache** with a production backend (Redis) if you mount many components
4. **Enable gzip/brotli** on your reverse proxy for static files (standard Django deployment)
5. **Set `SHARD_STATE_TIMEOUT`** to expire unused component state
6. **Run `shard_report --check-budget` in CI** to catch asset regressions

## Size budgets

Shard ships conservative gzip budgets for bundled JavaScript. CI runs:

```bash
python manage.py shard_report --check-budget
```

Current limits (see `shard/weight.py`):

| Check | Budget |
| ----- | ------ |
| `htmx.min.js` gzip | 17.5 KB |
| `shard.js` gzip | 500 B |
| `alpine.min.js` gzip | 17.5 KB |
| Required JS total | 18 KB |
| All JS (with Alpine) | 35 KB |

Raise budgets intentionally when upgrading vendored libraries.

## Comparison mindset

Shard is not competing with React/Vue bundle sizes — it deliberately avoids a client framework. The tradeoff:

| | Shard | Typical SPA |
|---|-------|-------------|
| JS transfer | ~17–33 KB gzip | 100–300+ KB gzip |
| Build tooling | None | webpack/Vite required |
| Server round-trips | Per action (HTMX) | API calls + hydration |
| SEO / first paint | Server-rendered HTML | Depends on SSR setup |

For Django teams who want components without a SPA, Shard keeps the client payload small by keeping logic on the server.
