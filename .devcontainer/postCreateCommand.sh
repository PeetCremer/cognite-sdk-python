#!/usr/bin/env bash

# Copy in default VSCode settings file as part of initial devcontainer create process.
# This avoids overwriting user-provided settings for normal local dev setups.
mkdir -p .vscode
cp .devcontainer/vscode.default.settings.json .vscode/settings.json

# Sync dependencies with uv and install pre-commit hooks
uv sync --all-extras
uv run pre-commit install
