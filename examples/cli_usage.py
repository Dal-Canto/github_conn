#!/usr/bin/env python
"""
Example: Using github_conn CLI Tool

This example demonstrates the github_conn CLI Tool for easy GitHub API access from the terminal.

Installation:
    pip install github-conn[cli]

Usage Examples:
    # Get user profile
    github-conn user torvalds

    # Get user profile as JSON
    github-conn user torvalds --json

    # List repositories
    github-conn repos guido

    # List Python repositories for a user
    github-conn repos-by-language torvalds Python

    # Get followers
    github-conn followers torvalds

    # Create a new repository (requires authentication)
    GITHUB_TOKEN=your_token github-conn create-repo --name my-repo --description "My repo"

    # Verbose output
    github-conn -v user torvalds

    # Using token from environment variable
    export GITHUB_TOKEN=ghp_xxxxxxxxxxxx
    github-conn create-repo --name new-repo
"""

import subprocess
import json


def run_cli_command(args: list) -> dict:
    """Run a CLI command and return parsed JSON output."""
    cmd = ["github-conn"] + args + ["--json"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode == 0:
        try:
            return json.loads(result.stdout)
        except json.JSONDecodeError:
            return {"raw": result.stdout}
    else:
        print(f"Error: {result.stderr}")
        return {}


if __name__ == "__main__":
    print("=== github_conn CLI Tool Examples ===\n")

    # Example 1: Get user information
    print("1. Getting user information...")
    user_data = run_cli_command(["user", "torvalds"])
    if user_data:
        print(f"   User: {user_data.get('login')}")
        print(f"   Followers: {user_data.get('followers')}")
        print(f"   Public Repos: {user_data.get('public_repos')}\n")

    # Example 2: Get repositories
    print("2. Getting repositories...")
    repos_data = run_cli_command(["repos", "torvalds", "--per-page", "3"])
    if repos_data:
        for repo in repos_data[:3]:
            print(f"   - {repo.get('name')} ({repo.get('stargazers_count')} stars)")
        print()

    # Example 3: Get repository names
    print("3. Getting repository names...")
    names = run_cli_command(["repos-names", "torvalds"])
    if names:
        for name in names[:5]:
            print(f"   - {name}")
        print()

    # Example 4: Filter by language
    print("4. Getting C repositories...")
    c_repos = run_cli_command(["repos-by-language", "torvalds", "C"])
    if c_repos:
        for repo in c_repos[:3]:
            print(f"   - {repo.get('name')} ({repo.get('stargazers_count')} stars)")
        print()

    print("✓ CLI tool examples completed!")
    print("\nFor more examples, run: github-conn --help")
