from pyjen.jenkins import Jenkins
import pytest
from pyjen.plugins.statusview import StatusView
from ..utils import clean_view


def test_create_status_view(jenkins_env):
    jk = Jenkins(jenkins_env["url"], (jenkins_env["admin_user"], jenkins_env["admin_token"]))
    expected_view_name = "test_create_status_view"
    v = jk.create_view(expected_view_name, StatusView)
    assert v is not None
    with clean_view(v):
        assert isinstance(v, StatusView)
        assert v.name == expected_view_name


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-s"])
