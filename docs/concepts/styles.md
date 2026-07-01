# Scoped styles

Shard scopes component CSS automatically so class names don't leak globally.

## Convention: co-located CSS

Place a `.css` file beside your component template:

```
templates/components/
├── card.html
├── card.css
├── counter.html
└── counter.css
```

Shard discovers `card.css` when rendering `card.html` and injects scoped styles automatically.

## Writing styles

Write normal CSS with simple class names:

```css
/* card.css */
.card {
  border: 1px solid #ccc;
  border-radius: 0.75rem;
  padding: 1rem;
}

.card__title {
  font-size: 1.125rem;
  font-weight: 600;
}
```

## How scoping works

At render time, Shard prefixes every selector:

```css
/* You write */
.title {
  color: red;
}

/* Browser receives */
[data-shard-scope="card"] .title {
  color: red;
}
```

Your template root element gets the scope attribute via `{% shard_root component %}`:

```html
<article data-shard-scope="card" id="shard-abc123" class="card"></article>
```

## Scope key

The scope key defaults to a slugified component name (`Card` → `card`). Override per class:

```python
class Card(Component):
    scope = "ui-card"  # → data-shard-scope="ui-card"
```

## Disabling scoped styles

```python
class Card(Component):
    scoped_styles = False
```

## Inline styles

```python
class Badge(Component):
    styles = ".badge { padding: 0.25rem 0.5rem; }"
```

## Explicit stylesheets

```python
class Card(Component):
    stylesheets = ["components/card.css", "components/card-theme.css"]
```

## Media queries

`@media` blocks are handled correctly — inner selectors are scoped:

```css
@media (max-width: 600px) {
  .card {
    padding: 0.5rem;
  }
}
```

## What scoping does not do

- Shadow DOM isolation (elements can still inherit global font/color)
- Automatic class name hashing (use BEM or prefixes for clarity)
- CSS Modules-style imports

Scoped styles prevent **selector collisions**, not inheritance. Global page styles still apply.

## Tips

1. Use BEM-style names (`.card__title`) for readability
2. Put `{% shard_root component %}` on the outermost element
3. Avoid styling bare elements (`p`, `a`) without a class — scope helps but class selectors are clearer
4. Page-level layout CSS belongs in your base template, not component CSS
