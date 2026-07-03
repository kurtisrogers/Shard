import pytest
from django.test import Client

from shard.testing import post_action


def test_post_action_bad_namespace_raises_helpful_error(client: Client):
    with pytest.raises(ValueError, match="Could not reverse action URL"):
        post_action(client, "abc123", "bump", namespace="not-a-real-namespace")
