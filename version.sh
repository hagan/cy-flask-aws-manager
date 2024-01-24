#!/bin/bash

new_version=$1

if [ -z "$new_version" ]; then
  echo "Usage: $0 <new_version>"
  exit 1
fi

# Ensure the working directory is clean
if [ -n "$(git status --porcelain)" ]; then
  echo "Error: Working directory is not clean. Please commit or stash your changes."
  exit 1
fi

# Bump the version with Poetry
poetry version $new_version

# Commit the changes
git add pyproject.toml poetry.lock
git commit -m "Bump version to $new_version"

# Create a git tag
git tag v$new_version

# Push the changes and tag
git push origin main
git push origin v$new_version