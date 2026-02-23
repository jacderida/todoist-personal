#!/usr/bin/env bash
set -euo pipefail

echo "============================================"
echo "Syncing Release Process Enhancements project"
echo "============================================"
todoist dev sync-todoist-from-linear \
    --linear-team Infrastructure \
    --linear-project "Release Process Enhancements" \
    --todoist-project "CI/Release"

echo "================================"
echo "Syncing Testnet Registry project"
echo "================================"
todoist dev sync-todoist-from-linear \
    --linear-team Tech \
    --linear-project "Testnet Registry" \
    --todoist-project "Testnet Registry"

echo "========================================"
echo "Syncing Platform Reach Expansion project"
echo "========================================"
todoist dev sync-todoist-from-linear \
    --linear-team Tech \
    --linear-project "Platform Reach Expansion" \
    --todoist-project "Platform Reach Expansion"

echo "======================================"
echo "Syncing Launchpad Improvements project"
echo "======================================"
todoist dev sync-todoist-from-linear \
    --linear-team Tech \
    --linear-project "Launchpad Improvements" \
    --todoist-project "Node Launchpad"

echo "=========================================="
echo "Syncing Antnode Automatic Upgrades project"
echo "=========================================="
todoist dev sync-todoist-from-linear \
    --linear-team Tech \
    --linear-project "Antnode Automatic Upgrades" \
    --todoist-project "Automatic Upgrades"

echo "=================================================="
echo "Syncing General Infrastructure Maintenance project"
echo "=================================================="
todoist dev sync-todoist-from-linear \
    --linear-team Infrastructure \
    --linear-project "General Infrastructure Maintenance" \
    --todoist-project "Maintenance"

echo "========================================================="
echo "Syncing Troubleshooting Production Network Issues project"
echo "========================================================="
todoist dev sync-todoist-from-linear \
    --linear-team Tech \
    --linear-project "Troubleshooting Production Network Issues" \
    --todoist-project "Troubleshooting Production Network Issues"

echo "========================================="
echo "Syncing Saorsa Testnet Registry project"
echo "========================================="
todoist dev sync-todoist-from-linear \
    --linear-team "V2.0" \
    --linear-project "Saorsa Testnet Registry" \
    --todoist-project "Saorsa Testnet Registry"
