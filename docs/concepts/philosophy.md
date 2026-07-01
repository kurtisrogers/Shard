# Philosophy

Shard occupies a specific niche: **making it easy to build components in Django**, not shipping a catalog of ready-made widgets.

## Framework, not library

A library gives you pre-built pieces to import. A framework gives you patterns to build your own pieces.

Shard provides:

- A `Component` base class
- A props system
- State persistence and action dispatch
- Slot composition
- Scoped CSS
- HTMX and Alpine.js integration

You provide:

- Component classes
- Templates
- Styles
- Business logic

## Lighter than React/Vue

Shard deliberately avoids:

- Virtual DOM
- Client-side routing
- Build tooling
- npm dependencies in your app
- A separate API layer for UI state

Server state lives on the server. Client interactivity is opt-in via Alpine.js. Most updates flow through HTMX partial renders.

## Less opinionated than full SPA frameworks

Shard does not dictate:

- CSS methodology (BEM, utility classes, plain CSS — your choice)
- Page layout structure
- Form handling strategy (use Django forms if you want)
- Authentication patterns

The only conventions are where files go and how components connect.

## Django ecosystem only

Shard uses:

- Django templates
- Django cache
- Django static files
- Django URL routing
- Django management commands

HTMX and Alpine.js are bundled as static assets — no CDN dependency, no package.json in your project.

## When to use Shard

**Good fit:**

- Server-rendered Django apps that need reusable UI pieces
- Teams who want component composition without a SPA
- Projects that value simplicity over client-side richness
- Gradual enhancement of existing Django templates

**Less ideal:**

- Highly interactive dashboards with complex client state graphs
- Real-time collaborative editing
- Offline-first applications

For those cases, a dedicated frontend framework may serve you better. Shard is for teams who want to stay in Django.
