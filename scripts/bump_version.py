#!/usr/bin/env python
"""
Version bumping script for PubMed MCP HTTP-vercel project.

This script updates the version in __init__.py and creates a git commit and tag.
GitHub release creation is optional and requires the gh CLI tool.
"""

import re
import sys
import subprocess
from pathlib import Path


def run_command(command, required=True):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, check=True, shell=True)
        return True
    except subprocess.CalledProcessError as e:
        if required:
            print(f"Error executing command: {command}")
            print(f"Error: {e}")
            sys.exit(1)
        else:
            print(f"Warning: Command failed: {command}")
            return False


def bump_version(version_type, create_release=False):
    """Bump version and create git commit/tag."""
    init_file = Path("src/pubmedmcp/__init__.py")

    # Read current version
    content = init_file.read_text()
    version_match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
    if not version_match:
        print("Error: Could not find version in __init__.py")
        sys.exit(1)

    current_version = version_match.group(1)
    major, minor, patch = map(int, current_version.split("."))

    # Update version based on argument
    if version_type == "major":
        new_version = f"{major + 1}.0.0"
    elif version_type == "minor":
        new_version = f"{major}.{minor + 1}.0"
    elif version_type == "patch":
        new_version = f"{major}.{minor}.{patch + 1}"
    else:
        print("Invalid version type. Use 'major', 'minor', or 'patch'")
        sys.exit(1)

    # Update __init__.py
    new_content = re.sub(
        r'__version__ = ["\']([^"\']+)["\']', f'__version__ = "{new_version}"', content
    )
    init_file.write_text(new_content)

    # Git operations
    run_command("git add src/pubmedmcp/__init__.py")
    run_command(f'git commit -m "Bump version to {new_version}"')
    run_command("git push")
    run_command(f"git tag v{new_version}")
    run_command("git push --tags")

    print(f"Version bumped from {current_version} to {new_version}")
    print("Git operations completed")

    # Create GitHub release if requested
    if create_release:
        success = run_command(
            f'gh release create v{new_version} --title "Release {new_version}" --generate-notes',
            required=False,
        )
        if success:
            print(f"GitHub release v{new_version} created")
        else:
            print("GitHub release creation failed (gh CLI may not be installed)")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: bump_version.py <major|minor|patch> [--release]")
        print("  --release: Create GitHub release (requires gh CLI)")
        sys.exit(1)

    version_type = sys.argv[1]
    create_release = "--release" in sys.argv

    bump_version(version_type, create_release)
