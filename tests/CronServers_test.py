import pytest
from cronboard_widgets.CronServers import CronServers
import paramiko


@pytest.fixture
def servers_env(tmp_path, mocker):
    mocker.patch("cronboard_widgets.CronServers.Path.home", return_value=tmp_path)
    mocker.patch("cronboard_widgets.CronServers.encrypt_password", return_value="enc")
    mocker.patch("cronboard_widgets.CronServers.decrypt_password", return_value="dec")
    return tmp_path


def test_init_with_no_servers_file(servers_env):
    server = CronServers()
    assert server.servers == {}
    assert server.current_ssh_client is None


def test_load_servers_from_toml(servers_env, mocker):
    config = servers_env / ".config/cronboard/servers.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("""
[srv1]
name = "Test Server"
host = "example.com"
port = 22
username = "user"
encrypted_password = "encrypted"
ssh_key = false
connected = false
crontab_user = "user"
""")
    
    decrypt_mock = mocker.patch("cronboard_widgets.CronServers.decrypt_password", return_value="password123")
    server = CronServers()
    
    assert "srv1" in server.servers
    assert server.servers["srv1"]["host"] == "example.com"
    assert server.servers["srv1"]["password"] == "password123"
    decrypt_mock.assert_called_with("encrypted")


def test_save_servers_encrypts_passwords(servers_env, mocker):
    encrypt_mock = mocker.patch("cronboard_widgets.CronServers.encrypt_password", return_value="encrypted123")
    
    server = CronServers()
    server.servers = {
        "test@host:user": {
            "name": "test",
            "host": "host",
            "port": 22,
            "username": "user",
            "password": "secret",
            "ssh_key": False,
            "connected": False,
            "crontab_user": "user"
        }
    }
    server.save_servers()
    
    encrypt_mock.assert_called_with("secret")
    saved = (servers_env / ".config/cronboard/servers.toml").read_text()
    assert "encrypted123" in saved
    assert "secret" not in saved


def test_connect_with_password(servers_env, mocker):
    mock_ssh = mocker.MagicMock(spec=paramiko.SSHClient)
    mocker.patch("cronboard_widgets.CronServers.paramiko.SSHClient", return_value=mock_ssh)
    
    server = CronServers()
    mocker.patch.object(server, "show_cron_table_for_server")
    mocker.patch.object(server, "save_servers")
    mocker.patch.object(server, "notify")
    
    server_info = {
        "name": "test", "host": "example.com", "port": 22,
        "username": "user", "password": "pass", "ssh_key": False,
        "connected": False, "crontab_user": "user"
    }
    
    server.connect_to_server(server_info)
    
    mock_ssh.connect.assert_called_once_with(
        hostname="example.com", port=22, username="user", password="pass"
    )
    assert server.current_ssh_client == mock_ssh
    assert server_info["connected"] is True


def test_connect_with_ssh_key(servers_env, mocker):
    mock_ssh = mocker.MagicMock(spec=paramiko.SSHClient)
    mocker.patch("cronboard_widgets.CronServers.paramiko.SSHClient", return_value=mock_ssh)
    
    server = CronServers()
    mocker.patch.object(server, "show_cron_table_for_server")
    mocker.patch.object(server, "save_servers")
    mocker.patch.object(server, "notify")
    
    server_info = {
        "name": "test", "host": "example.com", "port": 22,
        "username": "user", "password": None, "ssh_key": True,
        "connected": False, "crontab_user": "user"
    }
    
    server.connect_to_server(server_info)
    
    mock_ssh.connect.assert_called_once_with(hostname="example.com", port=22, username="user")


def test_connect_handles_auth_failure(servers_env, mocker):
    mock_ssh = mocker.MagicMock(spec=paramiko.SSHClient)
    mock_ssh.connect.side_effect = paramiko.AuthenticationException("Auth failed")
    mocker.patch("cronboard_widgets.CronServers.paramiko.SSHClient", return_value=mock_ssh)
    
    server = CronServers()
    mocker.patch.object(server, "notify")
    
    server_info = {
        "name": "test", "host": "example.com", "port": 22,
        "username": "user", "password": "wrong", "ssh_key": False,
        "connected": False, "crontab_user": "user"
    }
    
    server.connect_to_server(server_info)
    server.notify.assert_called_with("Authentication failed. Please check your credentials.")


def test_disconnect_closes_client(servers_env, mocker):
    server = CronServers()
    mock_ssh = mocker.MagicMock(spec=paramiko.SSHClient)
    server.current_ssh_client = mock_ssh
    server.servers = {"srv1": {"name": "test", "connected": True}}
    
    mocker.patch.object(server, "show_disconnected_message")
    mocker.patch.object(server, "save_servers")
    mocker.patch.object(server, "notify")
    
    server.action_disconnect_server()
    
    mock_ssh.close.assert_called_once()
    assert server.current_ssh_client is None
    assert server.servers["srv1"]["connected"] is False


def test_add_server_to_tree(servers_env, mocker):
    server = CronServers()
    mock_tree = mocker.MagicMock()
    mocker.patch.object(server, "query_one", return_value=mock_tree)
    mocker.patch.object(server, "save_servers")
    
    server.add_server_to_tree("test@host", "host", "22", "test", "pass", "user")
    
    assert "test@host:user" in server.servers
    assert server.servers["test@host:user"]["password"] == "pass"
    assert server.servers["test@host:user"]["ssh_key"] is False
    mock_tree.root.add_leaf.assert_called_once()


@pytest.mark.parametrize("password,expected_ssh_key", [
    ("secret", False),
    (None, True)
])
def test_add_server_ssh_key_logic(servers_env, mocker, password, expected_ssh_key):
    server = CronServers()
    mock_tree = mocker.MagicMock()
    mocker.patch.object(server, "query_one", return_value=mock_tree)
    mocker.patch.object(server, "save_servers")
    
    server.add_server_to_tree("test@host", "host", "22", "test", password, "user")
    
    assert server.servers["test@host:user"]["ssh_key"] is expected_ssh_key


def test_load_handles_decryption_error(servers_env, mocker):
    config = servers_env / ".config/cronboard/servers.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("""
[srv1]
name = "Test"
host = "example.com"
port = 22
username = "user"
encrypted_password = "bad"
ssh_key = false
connected = false
crontab_user = "user"
""")
    
    mocker.patch("cronboard_widgets.CronServers.decrypt_password", side_effect=Exception("Decrypt failed"))
    server = CronServers()
    
    assert server.servers["srv1"]["password"] is None


def test_load_handles_malformed_toml(servers_env, mocker):
    config = servers_env / ".config/cronboard/servers.toml"
    config.parent.mkdir(parents=True, exist_ok=True)
    config.write_text("invalid toml [[[")
    
    server = CronServers()
    assert server.servers == {}


def test_save_handles_write_error(servers_env, mocker):
    mocker.patch("cronboard_widgets.CronServers.tomlkit.dump", side_effect=PermissionError("No write"))
    
    server = CronServers()
    server.servers = {"test@host:user": {
        "name": "test", "host": "host", "port": 22, "username": "user",
        "password": None, "ssh_key": True, "connected": False, "crontab_user": "user"
    }}
    mocker.patch.object(server, "notify")
    
    server.save_servers()
    server.notify.assert_called_once()
    assert "Failed to save servers" in server.notify.call_args[0][0]


def test_roundtrip_preserves_data(servers_env, mocker):
    server1 = CronServers()
    server1.servers = {
        "user@host:cron": {
            "name": "Test Server", "host": "example.com", "port": 2222,
            "username": "user", "password": "secret", "ssh_key": False,
            "connected": False, "crontab_user": "cron"
        }
    }
    server1.save_servers()
    
    server2 = CronServers()
    assert "user@host:cron" in server2.servers
    assert server2.servers["user@host:cron"]["port"] == 2222
    assert server2.servers["user@host:cron"]["host"] == "example.com"
