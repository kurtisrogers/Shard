# Roadmap

This roadmap describes planned and proposed work for Shrd. It is updated periodically and reflects maintainer priorities as of **July 2026**.

**Current release:** `0.3.0` — view data, `ViewTreeComponent`, HTMX/Alpine guides.

!!! note "How to influence the roadmap"
Open a [GitHub discussion](https://github.com/kurtisrogers/Shard/discussions) or issue with your use case. Features that solve real project needs are prioritized over speculative additions.

## Recently shipped

### v0.3.0 (July 2026)

- Structured view data rendering (`render_view_data`, `ViewNode`)
- `ViewTreeComponent` for mutable layouts via HTMX actions
- `SHARD_VIEW_DATA_ALLOWED_COMPONENTS` whitelist setting
- Tree helpers: `ensure_node_ids`, `commit_view_tree`, `get_slot_nodes`, `set_slot_nodes`
- Documentation for view data and HTMX/Alpine workflows
- Example `/dynamic/` demo page

### v0.2.0

- Core component model: props, state, slots, scoped CSS
- HTMX actions, Alpine.js integration, custom events
- `shard_report` size budgets and `shard_doctor` health checks
- Testing helpers (`mount`, `post_action`, `extract_instance_id`)

---

## Near term — v0.4.x

Maintenance and developer-experience improvements with no breaking API changes.

### Security and dependencies

| Item                      | Priority | Description                                                                     |
| ------------------------- | -------- | ------------------------------------------------------------------------------- |
| Bundled asset updates     | High     | Upgrade HTMX `2.0.4` → `2.0.9`, Alpine `3.14.8` → `3.15.12` within size budgets |
| `pip-audit` in CI         | High     | Fail PRs on known Python CVEs in runtime and dev dependencies                   |
| Dependabot config         | Medium   | Automated PRs for GitHub Actions and pre-commit hook revisions                  |
| Documented asset versions | Medium   | Expose HTMX/Alpine versions via `shard_report` and `SHARD` context processor    |

### Framework polish

| Item                    | Priority | Description                                                                                |
| ----------------------- | -------- | ------------------------------------------------------------------------------------------ |
| Render lifecycle hooks  | Medium   | `before_render` / `after_render` on `Component` (currently requires overriding `render()`) |
| Enhanced `shard_doctor` | Medium   | Report bundled JS versions, cache connectivity test, view-data whitelist warnings          |
| View data validation    | Medium   | Optional JSON-schema or TypedDict validation for view trees before render                  |
| Error messages          | Low      | Clearer `PropValidationError` and `ViewDataError` messages with node path context          |

---

## Medium term — v0.5.x

Features that expand capability while keeping the "Django-native, no build step" philosophy.

### Interactivity

| Item                     | Description                                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------------------ |
| Alpine CSP build option  | `SHARD_ALPINE_CSP` setting to ship the CSP-compliant Alpine build for strict `Content-Security-Policy` |
| Out-of-band swaps        | First-class helpers for HTMX OOB updates alongside component re-renders                                |
| Debounced action helpers | Template-tag or Python helpers for common debounce patterns (beyond manual `hx-trigger`)               |
| Action middleware        | Pluggable hooks for cross-cutting concerns (logging, rate limiting, permissions)                       |

### View data and composition

| Item                    | Description                                                                           |
| ----------------------- | ------------------------------------------------------------------------------------- |
| View data serialization | Helpers to export/import view trees (e.g. CMS storage, API responses)                 |
| Partial tree updates    | Re-render only changed subtrees instead of full layout on `ViewTreeComponent` actions |
| Slot schema validation  | Document and enforce expected slot shapes per component in view data                  |

### Developer experience

| Item                      | Description                                                                            |
| ------------------------- | -------------------------------------------------------------------------------------- |
| Type stubs (`py.typed`)   | PEP 561 package for IDE autocomplete on props, state, and view nodes                   |
| Component scaffolding     | `manage.py` command or cookiecutter to generate component + template + CSS boilerplate |
| Debug toolbar integration | Optional panel showing mounted components, cache keys, and action dispatch             |

---

## Long term — v1.0 and beyond

Larger efforts evaluated against demand and complexity.

### Real-time and async

- **Django Channels bridge** — optional WebSocket transport for live updates without abandoning the component model
- **Async action handlers** — `async def` action methods with ASGI-compatible dispatch (requires careful cache and ORM integration)

### Tooling ecosystem

- **Component playground** — local dev UI to mount components in isolation (storybook-like, server-rendered)
- **Visual layout editor** — optional admin integration for view-data trees (targets CMS/admin use cases)
- **Migration guides** — patterns for adopting Shrd incrementally in existing Django template projects

### Performance

- **Fragment caching** — cache rendered component HTML with invalidation tied to state version
- **Lazy script loading** — defer Alpine until a component on the page requests `get_client_state()`
- **CSS deduplication** — share scoped style blocks when the same component appears multiple times on one page

---

## Non-goals

Shrd will **not** pursue:

- A pre-built widget catalog (buttons, modals, data tables) — use your own design system
- Client-side routing or a virtual DOM
- A required npm/build toolchain in consumer projects
- Replacing Django forms, auth, or ORM patterns

These stay outside scope per the [philosophy](concepts/philosophy.md).

---

## Versioning policy

Shrd follows [Semantic Versioning](https://semver.org/):

- **Patch** — bug fixes, security updates, documentation
- **Minor** — backward-compatible features and deprecations
- **Major** — breaking API or convention changes (targeted for 1.0 after API stabilizes)

See [Releasing](RELEASING.md) for the release process.

## Status legend

| Label         | Meaning                                                  |
| ------------- | -------------------------------------------------------- |
| **Planned**   | Scoped for the listed version range; likely to ship      |
| **Proposed**  | Under consideration; needs design and community feedback |
| **Exploring** | Early investigation; no commitment                       |

Items in the tables above are **Planned** unless noted otherwise in a linked GitHub issue.
