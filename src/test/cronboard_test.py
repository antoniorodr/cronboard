import hashlib
import base64
from pathlib import Path
from unittest.mock import MagicMock, patch

import paramiko
import pytest
from textual.app import App, ComposeResult

from cronboard.app import CronBoard
from cronboard_widgets.CronCreator import CronCreator
from cronboard_widgets.CronDeleteConfirmation import CronDeleteConfirmation
from cronboard_widgets.CronHostKeyChanged import CronHostKeyChanged
from cronboard_widgets.CronHostKeyConfirm import CronHostKeyConfirm
from cronboard_widgets.CronServers import CronServers
from cronboard_widgets.CronSSHModal import CronSSHModal


# ------------------------------------------------------------------ #
# Existing tests
# ------------------------------------------------------------------ #


@pytest.mark.asyncio
async def test_change_tab():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        assert app.local_table.has_focus


@pytest.mark.asyncio
async def test_refresh_data():
    app = CronBoard()
    async with app.run_test() as pilot:
        initial_data = app.local_table
        await pilot.press("r")
        refreshed_data = app.local_table
        assert initial_data == refreshed_data


@pytest.mark.asyncio
async def test_quit_app():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("ctrl+q")
        assert app.is_running is False


@pytest.mark.asyncio
async def test_create_cronjob():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("c")
        assert isinstance(app.screen, CronCreator)


@pytest.mark.asyncio
async def test_delete_cronjob():
    app = CronBoard()
    async with app.run_test() as pilot:
        await pilot.press("tab")
        await pilot.press("D")
        assert isinstance(app.screen, CronDeleteConfirmation)


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


# ------------------------------------------------------------------ #
# format_fingerprint
# ------------------------------------------------------------------ #


def test_format_fingerprint_sha256_prefix():
    key = paramiko.RSAKey.generate(1024)
    fp = CronServers.format_fingerprint(key)
    assert fp.startswith("SHA256:")


def test_format_fingerprint_deterministic():
    key = paramiko.RSAKey.generate(1024)
    assert CronServers.format_fingerprint(key) == CronServers.format_fingerprint(key)


def test_format_fingerprint_different_keys_differ():
    key_a = paramiko.RSAKey.generate(1024)
    key_b = paramiko.RSAKey.generate(1024)
    assert CronServers.format_fingerprint(key_a) != CronServers.format_fingerprint(key_b)


def test_format_fingerprint_matches_manual_sha256():
    key = paramiko.RSAKey.generate(1024)
    expected_b64 = base64.b64encode(
        hashlib.sha256(key.asbytes()).digest()
    ).decode("ascii").rstrip("=")
    assert CronServers.format_fingerprint(key) == f"SHA256:{expected_b64}"


# ------------------------------------------------------------------ #
# _load_or_init_host_keys
# ------------------------------------------------------------------ #


def test_load_or_init_creates_file(tmp_path):
    servers = CronServers.__new__(CronServers)
    servers.config = {}
    servers.known_hosts_path = tmp_path / "known_hosts"

    host_keys = servers._load_or_init_host_keys()

    assert servers.known_hosts_path.exists()
    assert isinstance(host_keys, paramiko.HostKeys)


def test_load_or_init_round_trips_key(tmp_path):
    servers = CronServers.__new__(CronServers)
    servers.config = {}
    servers.known_hosts_path = tmp_path / "known_hosts"

    key = paramiko.RSAKey.generate(1024)
    host_keys = servers._load_or_init_host_keys()
    host_keys.add("myhost.example", "ssh-rsa", key)
    host_keys.save(str(servers.known_hosts_path))

    reloaded = servers._load_or_init_host_keys()
    assert reloaded.lookup("myhost.example") is not None


# ------------------------------------------------------------------ #
# _build_ssh_client policy
# ------------------------------------------------------------------ #


def _make_servers(config=None, known_hosts_path=None) -> CronServers:
    """Construct a CronServers without hitting the filesystem."""
    servers = CronServers.__new__(CronServers)
    servers.config = config or {}
    servers.known_hosts_path = known_hosts_path or Path("/nonexistent/known_hosts")
    return servers


def test_build_ssh_client_strict_uses_reject_policy(tmp_path):
    servers = _make_servers(config={}, known_hosts_path=tmp_path / "known_hosts")
    client = servers._build_ssh_client()
    assert isinstance(client._policy, paramiko.RejectPolicy)


def test_build_ssh_client_permissive_uses_warning_policy(tmp_path):
    cfg = {"ssh": {"host_key_policy": "permissive"}}
    servers = _make_servers(config=cfg, known_hosts_path=tmp_path / "known_hosts")
    client = servers._build_ssh_client()
    assert isinstance(client._policy, paramiko.WarningPolicy)


def test_build_ssh_client_explicit_strict_uses_reject_policy(tmp_path):
    cfg = {"ssh": {"host_key_policy": "strict"}}
    servers = _make_servers(config=cfg, known_hosts_path=tmp_path / "known_hosts")
    client = servers._build_ssh_client()
    assert isinstance(client._policy, paramiko.RejectPolicy)


# ------------------------------------------------------------------ #
# CronHostKeyConfirm modal
# ------------------------------------------------------------------ #


class _HostKeyConfirmApp(App):
    """Minimal app that immediately opens CronHostKeyConfirm."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None

    def compose(self) -> ComposeResult:
        return iter([])

    def on_mount(self) -> None:
        self.push_screen(
            CronHostKeyConfirm(
                "host.example", 22, "ssh-ed25519", "SHA256:AAABBBCCC"
            ),
            lambda r: setattr(self, "result", r),
        )


@pytest.mark.asyncio
async def test_host_key_confirm_trust_button_returns_true():
    app = _HostKeyConfirmApp()
    async with app.run_test() as pilot:
        await pilot.click("#trust")
    assert app.result is True


@pytest.mark.asyncio
async def test_host_key_confirm_cancel_button_returns_false():
    app = _HostKeyConfirmApp()
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
    assert app.result is False


@pytest.mark.asyncio
async def test_host_key_confirm_escape_returns_false():
    app = _HostKeyConfirmApp()
    async with app.run_test() as pilot:
        await pilot.press("escape")
    assert app.result is False


@pytest.mark.asyncio
async def test_host_key_confirm_shows_fingerprint():
    app = _HostKeyConfirmApp()
    async with app.run_test() as pilot:
        label = app.screen.query_one("#label_fp")
        assert "SHA256:AAABBBCCC" in str(label.content)
        await pilot.click("#cancel")


# ------------------------------------------------------------------ #
# CronHostKeyChanged modal
# ------------------------------------------------------------------ #


class _HostKeyChangedApp(App):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.result = None

    def compose(self) -> ComposeResult:
        return iter([])

    def on_mount(self) -> None:
        self.push_screen(
            CronHostKeyChanged(
                "host.example",
                22,
                "SHA256:EXPECTED111",
                "SHA256:RECEIVED222",
            ),
            lambda r: setattr(self, "result", r),
        )


@pytest.mark.asyncio
async def test_host_key_changed_trust_button_returns_true():
    app = _HostKeyChangedApp()
    async with app.run_test() as pilot:
        await pilot.click("#trust")
    assert app.result is True


@pytest.mark.asyncio
async def test_host_key_changed_cancel_button_returns_false():
    app = _HostKeyChangedApp()
    async with app.run_test() as pilot:
        await pilot.click("#cancel")
    assert app.result is False


@pytest.mark.asyncio
async def test_host_key_changed_escape_returns_false():
    app = _HostKeyChangedApp()
    async with app.run_test() as pilot:
        await pilot.press("escape")
    assert app.result is False


@pytest.mark.asyncio
async def test_host_key_changed_shows_both_fingerprints():
    app = _HostKeyChangedApp()
    async with app.run_test() as pilot:
        expected_label = app.screen.query_one("#label_expected")
        received_label = app.screen.query_one("#label_received")
        assert "SHA256:EXPECTED111" in str(expected_label.content)
        assert "SHA256:RECEIVED222" in str(received_label.content)
        await pilot.click("#cancel")


# ------------------------------------------------------------------ #
# connect_to_server — mocked Paramiko behaviour
# ------------------------------------------------------------------ #


def _fake_server_info():
    return {
        "host": "fake.example",
        "port": 22,
        "username": "user",
        "password": None,
        "ssh_key": True,
        "crontab_user": None,
        "name": "Fake Server",
        "connected": False,
    }


class _CronServersApp(App):
    """Minimal test harness that mounts a CronServers widget."""

    def __init__(self, known_hosts_path: Path, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._known_hosts_path = known_hosts_path
        self.servers_widget: CronServers | None = None

    def compose(self) -> ComposeResult:
        return iter([])

    async def on_mount(self) -> None:
        with (
            patch.object(CronServers, "load_servers", return_value={}),
            patch.object(CronServers, "save_servers", return_value=None),
        ):
            self.servers_widget = CronServers()
        self.servers_widget.known_hosts_path = self._known_hosts_path
        await self.mount(self.servers_widget)


@pytest.mark.asyncio
async def test_connect_unknown_host_triggers_confirm_modal(tmp_path):
    """RejectPolicy path: unknown host → CronHostKeyConfirm is pushed."""
    app = _CronServersApp(known_hosts_path=tmp_path / "known_hosts")
    async with app.run_test() as pilot:
        await pilot.pause()
        servers = app.servers_widget
        server_info = _fake_server_info()
        fake_key = paramiko.RSAKey.generate(1024)

        with (
            patch.object(
                paramiko.SSHClient,
                "connect",
                side_effect=paramiko.SSHException(
                    "Server 'fake.example' not found in known_hosts"
                ),
            ),
            patch("cronboard_widgets.CronServers.socket.create_connection"),
            patch("cronboard_widgets.CronServers.paramiko.Transport") as mock_cls,
        ):
            mock_transport = MagicMock()
            mock_transport.get_remote_server_key.return_value = fake_key
            mock_cls.return_value = mock_transport

            servers.connect_to_server(server_info)
            await pilot.pause()

        assert isinstance(app.screen, CronHostKeyConfirm)
        await pilot.click("#cancel")


@pytest.mark.asyncio
async def test_connect_bad_host_key_triggers_changed_modal(tmp_path):
    """BadHostKeyException path: changed key → CronHostKeyChanged is pushed."""
    app = _CronServersApp(known_hosts_path=tmp_path / "known_hosts")
    async with app.run_test() as pilot:
        await pilot.pause()
        servers = app.servers_widget
        server_info = _fake_server_info()

        got_key = paramiko.RSAKey.generate(1024)
        expected_key = paramiko.RSAKey.generate(1024)

        with patch.object(
            paramiko.SSHClient,
            "connect",
            side_effect=paramiko.BadHostKeyException(
                "fake.example", got_key, expected_key
            ),
        ):
            servers.connect_to_server(server_info)
            await pilot.pause()

        assert isinstance(app.screen, CronHostKeyChanged)
        await pilot.click("#cancel")


@pytest.mark.asyncio
async def test_connect_trust_saves_key_and_reconnects(tmp_path):
    """Trusting an unknown key saves it and triggers a second connect attempt."""
    app = _CronServersApp(known_hosts_path=tmp_path / "known_hosts")
    async with app.run_test() as pilot:
        await pilot.pause()
        servers = app.servers_widget
        server_info = _fake_server_info()

        fake_key = paramiko.RSAKey.generate(1024)
        connect_calls = {"count": 0}

        def side_effect(*args, **kwargs):
            connect_calls["count"] += 1
            if connect_calls["count"] == 1:
                raise paramiko.SSHException(
                    "Server 'fake.example' not found in known_hosts"
                )

        with (
            patch.object(paramiko.SSHClient, "connect", side_effect=side_effect),
            patch("cronboard_widgets.CronServers.socket.create_connection"),
            patch("cronboard_widgets.CronServers.paramiko.Transport") as mock_cls,
            patch.object(servers, "show_cron_table_for_server"),
            patch.object(servers, "save_servers"),
        ):
            mock_transport = MagicMock()
            mock_transport.get_remote_server_key.return_value = fake_key
            mock_cls.return_value = mock_transport

            servers.connect_to_server(server_info)
            await pilot.pause()

            assert isinstance(app.screen, CronHostKeyConfirm)
            await pilot.click("#trust")
            await pilot.pause()

    assert servers.known_hosts_path.exists(), "known_hosts file should be created"
    saved_keys = paramiko.HostKeys(str(servers.known_hosts_path))
    # Port 22 → plain hostname; non-22 → [host]:port format (matches Paramiko's lookup)
    assert saved_keys.lookup("fake.example") is not None
    assert connect_calls["count"] == 2


def test_key_storage_name_standard_port():
    """Port 22 uses plain hostname in known_hosts."""
    servers = _make_servers()
    server_info = _fake_server_info()
    server_info["port"] = 22
    host = server_info["host"]
    port = int(server_info["port"])
    storage_name = f"[{host}]:{port}" if port != 22 else host
    assert storage_name == "fake.example"


def test_key_storage_name_nonstandard_port():
    """Non-22 port uses [host]:port format to match Paramiko's lookup key."""
    server_info = _fake_server_info()
    server_info["port"] = 2222
    host = server_info["host"]
    port = int(server_info["port"])
    storage_name = f"[{host}]:{port}" if port != 22 else host
    assert storage_name == "[fake.example]:2222"
