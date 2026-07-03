from django.test import override_settings

from shard import mount
from tests.support.components import Wrapper


@override_settings(SHARD_MINIFY_CSS=True)
def test_scoped_styles_minified_when_enabled():
    html = mount(Wrapper, slots={"default": "x"})
    assert '<style data-shard-styles="wrapper">' in html
    assert ".wrapper{padding:1rem;}" in html


def test_scoped_styles_not_minified_in_debug_by_default():
    with override_settings(DEBUG=True):
        html = mount(Wrapper, slots={"default": "x"})
    assert "padding: 1rem" in html
    assert "padding:1rem" not in html


@override_settings(SHARD_MINIFY_CSS=False)
def test_scoped_styles_can_disable_minification():
    html = mount(Wrapper, slots={"default": "x"})
    assert "padding: 1rem" in html
    assert "padding:1rem" not in html
