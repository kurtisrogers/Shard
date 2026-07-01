# Nested components

Render child components from within a parent component's template or Python code.

## Template: shard_child

```html
{# components/dashboard.html #}
<div {% shard_root component %} class="dashboard">
  <section>{% shard_child "Counter" initial=0 %}</section>
  <section>{% shard_child "TodoList" placeholder="Tasks..." %}</section>
</div>
```

Each child gets its own instance ID, state, and scoped styles.

## Python: render_child

```python
class Dashboard(Component):
    show_counter = Prop(bool, default=True)

    def get_extra_widgets(self, request):
        parts = []
        if self.show_counter:
            parts.append(self.render_child("Counter", props={"initial": 0}, request=request))
        return parts
```

## Nesting in page templates

You don't need `shard_child` for page-level composition. Use slots:

```django
{% component Card %}
  {% component Counter %}{% endcomponent %}
{% endcomponent %}
```

Use `shard_child` when the parent component template always includes specific children. Use slots when the parent accepts arbitrary content.

## State isolation

Child components have independent state. A parent's `@action` cannot directly modify a child's state. Options:

1. Lift state to the parent and pass as props (if children are stateless renderers)
2. Use HTMX events to coordinate (`@emits` / listeners)
3. Use Django session or database for shared state

## Performance

Each nested component adds a cache entry. For pages with many components, use a production cache backend (Redis) rather than LocMem.
