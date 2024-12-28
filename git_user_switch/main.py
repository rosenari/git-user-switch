import os
import json
import subprocess
from pathlib import Path
import argparse

REQUIRED_FIELDS = {"ssh_key", "git_name", "git_email"}


def get_config_path():
    config_path = os.environ.get("GIT_USER_SWITCH_CONFIG")

    if not config_path:
        print("Error: Environment variable 'GIT_USER_SWITCH_CONFIG' is not set.")
        print("Please set it to the path of your configuration file.")
        exit(1)
    return Path(os.path.expanduser(config_path))


def validate_config(config_path):
    if not config_path.exists():
        print(f"Error: Configuration file not found at {config_path}")
        exit(1)

    try:
        with open(config_path, "r") as f:
            config = json.load(f)
    except json.JSONDecodeError:
        print(f"Error: Configuration file at {config_path} is not valid JSON.")
        exit(1)

    if not isinstance(config, dict):
        print(f"Error: Configuration file must be a JSON object (dictionary).")
        exit(1)

    for user, fields in config.items():
        if not isinstance(fields, dict):
            print(f"Error: User '{user}' configuration must be a JSON object.")
            exit(1)
        missing_fields = REQUIRED_FIELDS - fields.keys()
        if missing_fields:
            print(f"Error: User '{user}' is missing required fields: {', '.join(missing_fields)}")
            exit(1)

    return config


def switch_user(user, config):
    if user not in config:
        print(f"Error: User '{user}' not found in the configuration.")
        exit(1)

    user_config = config[user]
    ssh_key = os.path.expanduser(user_config["ssh_key"])
    git_name = user_config["git_name"]
    git_email = user_config["git_email"]

    subprocess.run(["git", "config", "--global", "user.name", git_name], check=True)
    subprocess.run(["git", "config", "--global", "user.email", git_email], check=True)

    ssh_command = f"ssh -i {ssh_key} -o IdentitiesOnly=yes"
    subprocess.run(["git", "config", "--global", "core.sshCommand", ssh_command], check=True)

    print(f"Switched to user: {user}")
    print(f"Git name: {git_name}")
    print(f"Git email: {git_email}")
    print(f"SSH key set for Git: {ssh_key}")


def main():
    parser = argparse.ArgumentParser(description="Switch Git users easily.")
    parser.add_argument("user", help="The user profile to switch to.")
    args = parser.parse_args()

    config_path = get_config_path()
    config = validate_config(config_path)
    switch_user(args.user, config)


if __name__ == "__main__":
    main()
