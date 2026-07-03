"""Base component for mutable layouts backed by view data."""

from __future__ import annotations

from typing import ClassVar

from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe

from shard.component import Component
from shard.exceptions import ViewDataError
from shard.styles import load_scoped_styles
from shard.view_data import (
    TREE_STATE_KEY,
    ViewNode,
    commit_view_tree,
    ensure_node_ids,
    render_view_data,
    resolve_allowed_components,
)


class ViewTreeComponent(Component):
    """Component that renders a mutable view-data tree stored in server state.

    Subclasses store a view-data descriptor in ``state[view_tree_key]`` and
    override ``get_initial_state()`` to seed it. Use ``commit_view_tree()`` in
    ``@action`` handlers to mutate the layout and prune removed node state.

    The component template should render ``{{ content_html|safe }}`` (or the
    key named by ``content_context_key``).
    """

    view_tree_key: ClassVar[str] = TREE_STATE_KEY
    content_context_key: ClassVar[str] = "content_html"
    allowed_view_components: ClassVar[frozenset[str] | None] = None

    def get_view_tree(self) -> ViewNode:
        tree = self.state.get(self.view_tree_key)
        if not tree:
            raise ViewDataError(
                f"{self.__class__.__name__} state is missing '{self.view_tree_key}'."
            )
        return tree

    def set_view_tree(self, tree: ViewNode) -> None:
        self._state[self.view_tree_key] = tree

    def resolve_view_allowed_components(self) -> frozenset[str]:
        return resolve_allowed_components(allowed_components=self.allowed_view_components)

    def commit_view_tree(self, state: dict, tree: ViewNode) -> ViewNode:
        """Replace the view tree in action state and prune removed node cache."""

        return commit_view_tree(state, self.view_tree_key, tree)

    def render_view_tree(self, tree: ViewNode, *, request=None) -> SafeString:
        return render_view_data(
            tree,
            request=request,
            allowed_components=self.resolve_view_allowed_components(),
            stable=True,
        )

    def render(self, request=None) -> SafeString:
        if not self.template_name:
            raise ValueError(f"{self.__class__.__name__} is missing template_name.")

        tree = ensure_node_ids(self.get_view_tree())
        self.set_view_tree(tree)
        content_html = self.render_view_tree(tree, request=request)

        context = self.get_context_data()
        context[self.content_context_key] = content_html
        if request is not None:
            context["request"] = request

        html = render_to_string(self.template_name, context, request=request)
        styles = ""
        if self._should_include_styles(request):
            styles = load_scoped_styles(
                scope=self.shard_scope,
                template_name=self.template_name,
                stylesheets=self.stylesheets,
                inline_styles=self.styles,
            )

        self.persist()
        return mark_safe(f"{styles}{html}")
