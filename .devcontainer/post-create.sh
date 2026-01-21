#!/usr/bin/env bash

set -euo pipefail

# Ensure theme submodules are present for Hugo shortcodes and templates.
git submodule update --init --recursive

# Install Node.js dev dependencies when available.
if [ -f package.json ]; then
	npm install
fi
