#!/usr/bin/env bash
set -euo pipefail

echo "================================"
echo "Syncing Testnet Registry project"
echo "================================"
uv run todoist dev sync-todoist-from-linear \
    --linear-team Tech \
    --linear-project "Testnet Registry" \
    --todoist-project "Testnet Registry"

echo "========================================"
echo "Syncing Platform Reach Expansion project"
echo "========================================"
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Platform Reach Expansion" \
    --todoist-project "Platform Reach Expansion"

echo "======================================"
echo "Syncing Launchpad Improvements project"
echo "======================================"
uv run todoist dev sync-todoist-from-linear \
    --linear-team Tech \
    --linear-project "Launchpad Improvements" \
    --todoist-project "Node Launchpad"

echo "=================================================="
echo "Syncing General Infrastructure Maintenance project"
echo "=================================================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team Infrastructure \
    --linear-project "General Infrastructure Maintenance" \
    --todoist-project "Maintenance"

echo "========================================================="
echo "Syncing Troubleshooting Production Network Issues project"
echo "========================================================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team Tech \
    --linear-project "Troubleshooting Production Network Issues" \
    --todoist-project "Troubleshooting Production Network Issues"

echo "========================================="
echo "Syncing Saorsa Testnet Registry project"
echo "========================================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Saorsa Testnet Registry" \
    --todoist-project "Saorsa Testnet Registry"

echo "=========================================="
echo "Syncing Automatic Upgrades for Saorsa Node"
echo "=========================================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Automatic Upgrades for Saorsa Node" \
    --todoist-project "Automatic Upgrades"

echo "==================="
echo "Syncing Unified CLI"
echo "==================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Unified CLI" \
    --todoist-project "Unified CLI"

echo "===================="
echo "Syncing Testnet Runs"
echo "===================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Testnet Runs" \
    --todoist-project "Testnet Runs"

echo "==========="
echo "Syncing x0x"
echo "==========="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "x0x" \
    --todoist-project "x0x"

echo "============================="
echo "Syncing Repository Migrations"
echo "============================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Repository Migrations" \
    --todoist-project "Repository Migrations"

echo "=============="
echo "Syncing Saorsa"
echo "=============="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Saorsa" \
    --todoist-project "Saorsa"

echo "========================"
echo "Syncing Autonomi Desktop"
echo "========================"
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Autonomi Desktop" \
    --todoist-project "Autonomi Desktop"

echo "========================"
echo "Syncing Infrastructure"
echo "========================"
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Infrastructure" \
    --todoist-project "Infrastructure"

echo "========================"
echo "Syncing User Support"
echo "========================"
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "User Support" \
    --todoist-project "Support"

echo "==================================="
echo "Syncing Release Process Extensions"
echo "==================================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Release Process Extensions" \
    --todoist-project "CI/Release"

echo "==================================="
echo "Syncing Releases"
echo "==================================="
uv run todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Releases" \
    --todoist-project "CI/Release"
