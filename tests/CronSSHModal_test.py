import pytest
from cronboard_widgets.CronSSHModal import CronSSHModal


def test_parse_host_info_defaults_port():
    hostname, port = CronSSHModal._parse_host_info("node9")
    assert hostname == "node9"
    assert port == 22


def test_parse_host_info_with_port():
    hostname, port = CronSSHModal._parse_host_info("node9:2222")
    assert hostname == "node9"
    assert port == 2222


@pytest.mark.parametrize(
    "value",
    ["", ":", "node9:", ":2222", "node9:abc", "node9:0", "node9:70000"],
)
def test_parse_host_info_invalid(value):
    with pytest.raises(ValueError):
        CronSSHModal._parse_host_info(value)
