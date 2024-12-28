# Git User Switch

A CLI tool to switch Git user profiles easily.

## Installation

Install the package using `pipx`:

```bash
pipx install git-user-switch
```

## Configuration

Set the GIT_USER_SWITCH_CONFIG environment variable to the path of your configuration file

```
export GIT_USER_SWITCH_CONFIG="/Users/user/config.json"
```

The configuration file should look like this
```json
{
    "user1": {
        "ssh_key": "~/.ssh/id_rsa_user1",
        "git_name": "user-1",
        "git_email": "user1@example.com"
    },
    "user2": {
        "ssh_key": "~/.ssh/id_rsa_user2",
        "git_name": "user-2",
        "git_email": "user2@example.com"
    }
}
```

## Usage

```bash
git-user-switch user1
```

Try adding it to your zshrc or bashrc file and use it.

```bash
export GIT_USER_SWITCH_CONFIG="/Users/user/config.json"
git-user-switch user1
```