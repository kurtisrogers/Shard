# Shard

A Django-native component framework for building UI with **props**, **server state**, **slots**, and **scoped styles** — using only the Django ecosystem plus bundled HTMX and Alpine.js.

📖 **[Full documentation](https://kurtisrogers.github.io/Shard/)**

Shard is a framework, not a drop-in library. Your Django project adopts its conventions: components live in your apps, templates sit beside scoped CSS, and HTMX carries server actions.

## Philosophy

Shard does not ship a widget catalog. It gives you a small, familiar model — closer to React/Vue than to Django templates alone — without a build step or SPA complexity:

- **Props** — typed inputs declared on a Python class
- **State** — server-owned data updated via `@action` methods
- **Slots** — wrap and compose markup like `children` / default slots
- **Scoped styles** — co-located `.css` files, automatically prefixed to the component
- **Computed** — derived values via `@computed` methods
- **Events** — HTMX custom events via `@emits` and `ActionResult`
- **HTMX** — partial re-renders after actions
- **Alpine.js** — optional client-side behavior inside templates

## Quick start

```python
# myapp/components.py
from shard import Component, Prop, action

class Card(Component):
    title = Prop(str, default="")
    template_name = "components/card.html"
```

```django
{% load shard %}
{% shard_scripts %}

{% component Card title="Profile" %}
  <p>Anything here is passed through the default slot.</p>
{% endcomponent %}
```

See the [quickstart guide](https://kurtisrogers.github.io/Shard/getting-started/quickstart/) for a full walkthrough.

## Documentation

| Topic          | Link                                                                                               |
| -------------- | -------------------------------------------------------------------------------------------------- |
| Installation   | [getting-started/installation](https://kurtisrogers.github.io/Shard/getting-started/installation/) |
| Components     | [concepts/components](https://kurtisrogers.github.io/Shard/concepts/components/)                   |
| Slots          | [concepts/slots](https://kurtisrogers.github.io/Shard/concepts/slots/)                             |
| Scoped styles  | [concepts/styles](https://kurtisrogers.github.io/Shard/concepts/styles/)                           |
| Actions & HTMX | [interactivity/actions](https://kurtisrogers.github.io/Shard/interactivity/actions/)               |
| API reference  | [reference/api](https://kurtisrogers.github.io/Shard/reference/api/)                               |
| Examples       | [examples](https://kurtisrogers.github.io/Shard/examples/)                                         |

## Example app

```bash
pip install -e ".[dev]"
cd example
python manage.py migrate
python manage.py runserver
```

## Development

```bash
pip install -e ".[dev]"
pre-commit install          # optional: run checks before each commit
python -m pytest tests/ -q
```

**60 tests** with **≥90% coverage**. CI runs pre-commit, Ruff, tests (Python 3.10–3.12), and docs build on every PR.

```bash
pre-commit run --all-files  # lint + format locally
pip install -e ".[docs]"
python -m mkdocs serve
```

## License

MIT
