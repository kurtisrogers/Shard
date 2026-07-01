from shard import mount
from tests.support.components import Wrapper


def test_load_scoped_styles_from_colocated_css():
    html = mount(Wrapper, slots={"default": "x"})
    assert "<style data-shard-styles=" in html
    assert "wrapper" in html
    assert '[data-shard-scope="wrapper"]' in html
