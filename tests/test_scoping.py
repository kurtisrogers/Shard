from shard.scoping import scope_attribute, scope_css


def test_scope_css_prefixes_class_selector():
    scoped = scope_css(".title { color: red; }", "card")
    assert '[data-shard-scope="card"] .title' in scoped
    assert "color: red" in scoped


def test_scope_css_prefixes_multiple_selectors():
    scoped = scope_css(".a, .b { margin: 0; }", "box")
    assert '[data-shard-scope="box"] .a' in scoped
    assert '[data-shard-scope="box"] .b' in scoped


def test_scope_css_preserves_root_selector_when_unmapped():
    scoped = scope_css(":root { --x: 1; }", "theme")
    assert ":root" in scoped
    assert "--x: 1" in scoped


def test_scope_css_handles_media_queries():
    css = "@media (max-width: 600px) { .box { padding: 1rem; } }"
    scoped = scope_css(css, "card")
    assert "@media" in scoped
    assert '[data-shard-scope="card"] .box' in scoped


def test_scope_css_handles_multiple_rules_in_sequence():
    css = ".outer { color: blue; }"
    scoped = scope_css(css, "nest")
    assert '[data-shard-scope="nest"] .outer' in scoped
    assert "color: blue" in scoped


def test_scope_attribute_helper():
    assert scope_attribute("card") == 'data-shard-scope="card"'
