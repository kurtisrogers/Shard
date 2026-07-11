# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- Bundled HTMX updated from `2.0.4` to `2.0.9`
- Bundled Alpine.js updated from `3.14.8` to `3.15.12`

### Added

- `pip-audit` in dev dependencies and CI security audit job
- Dependabot configuration for pip and GitHub Actions

## [0.3.0] - 2026-07-01

### Added

- View data rendering (`shard.view_data`, `render_view_data()`)
- `ViewTreeComponent` for mutable layouts via HTMX actions
- `SHARD_VIEW_DATA_ALLOWED_COMPONENTS` setting
- `ViewDataError` exception
- Documentation guides for view data and HTMX/Alpine workflows
- Example `/dynamic/` demo page with `ViewPage` component
- Tree helpers: `ensure_node_ids`, `commit_view_tree`, `get_slot_nodes`, `set_slot_nodes`

### Changed

- PyPI package name is `shrd` (import name remains `shard`)

## [0.2.0] - Earlier

- Core component framework: props, state, slots, scoped CSS
- HTMX actions and Alpine.js integration
- Performance/size reporting (`shard_report`)

[0.3.0]: https://github.com/kurtisrogers/Shard/compare/v0.2.0...v0.3.0
