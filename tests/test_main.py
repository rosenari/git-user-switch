import os
import json
import pytest
import subprocess
from git_user_switch.main import get_config_path, validate_config, switch_user


@pytest.fixture
def config_env(tmp_path, monkeypatch):
    config_data = {
        "user1": {
            "ssh_key": "~/.ssh/id_rsa_user1",
            "git_name": "User One",
            "git_email": "user1@example.com"
        },
        "user2": {
            "ssh_key": "~/.ssh/id_rsa_user2",
            "git_name": "User Two",
            "git_email": "user2@example.com"
        }
    }
    config_path = tmp_path / "config.json"
    with open(config_path, "w") as f:
        json.dump(config_data, f, indent=4)

    monkeypatch.setenv("GIT_USER_SWITCH_CONFIG", str(config_path))
    return config_path


def test_get_config_path_env_set(config_env):
    config_path = get_config_path()
    assert config_path == config_env


def test_get_config_path_env_not_set(monkeypatch):
    monkeypatch.delenv("GIT_USER_SWITCH_CONFIG", raising=False)
    with pytest.raises(SystemExit):
        get_config_path()


def test_validate_config_valid(config_env):
    config = validate_config(config_env)
    assert "user1" in config
    assert "user2" in config
    assert config["user1"]["ssh_key"] == "~/.ssh/id_rsa_user1"


def test_validate_config_invalid_structure(tmp_path):
    invalid_config_path = tmp_path / "invalid_config.json"
    with open(invalid_config_path, "w") as f:
        f.write("[]")

    with pytest.raises(SystemExit):
        validate_config(invalid_config_path)


def test_validate_config_missing_fields(tmp_path):
    incomplete_config = {
        "user1": {
            "ssh_key": "~/.ssh/id_rsa_user1",
            "git_name": "User One"
            # Missing 'git_email'
        }
    }
    incomplete_config_path = tmp_path / "incomplete_config.json"
    with open(incomplete_config_path, "w") as f:
        json.dump(incomplete_config, f, indent=4)

    with pytest.raises(SystemExit):
        validate_config(incomplete_config_path)


def test_switch_user_valid(config_env):
    config = validate_config(config_env)

    switch_user("user1", config)

    ssh_command = subprocess.check_output(
        ["git", "config", "--global", "core.sshCommand"], text=True
    ).strip()
    user_name = subprocess.check_output(
        ["git", "config", "--global", "user.name"], text=True
    ).strip()
    user_email = subprocess.check_output(
        ["git", "config", "--global", "user.email"], text=True
    ).strip()

    expected_ssh_command = f"ssh -i {os.path.expanduser('~/.ssh/id_rsa_user1')} -o IdentitiesOnly=yes"
    assert ssh_command == expected_ssh_command
    assert user_name == "User One"
    assert user_email == "user1@example.com"


def test_switch_user_invalid_user(config_env):
    config = validate_config(config_env)
    with pytest.raises(SystemExit):
        switch_user("user3", config)