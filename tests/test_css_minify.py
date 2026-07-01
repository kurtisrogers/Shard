from shard.css_minify import minify_css


def test_minify_css_removes_comments_and_whitespace():
    css = """
    /* card styles */
    .card {
      padding: 1rem;
      margin: 0;
    }
    """
    assert minify_css(css) == ".card{padding:1rem;margin:0;}"


def test_minify_css_preserves_quoted_strings():
    css = '.icon::before { content: "/* not a comment */"; }'
    assert minify_css(css) == '.icon::before{content:"/* not a comment */";}'


def test_minify_css_preserves_media_queries():
    css = """
    @media (max-width: 768px) {
      .card { padding: 0.5rem; }
    }
    """
    assert minify_css(css) == "@media (max-width:768px){.card{padding:0.5rem;}}"
