#!/usr/bin/env bash
set -euo pipefail

echo "Syncing Release Process Enhancements project..."
todoist dev linear-sync \
    --linear-team Infrastructure \
    --linear-project "Release Process Enhancements" \
    --todoist-project "CI/Release"

echo "Syncing Testnet Registry project..."
todoist dev linear-sync \
    --linear-team Tech \
    --linear-project "Testnet Registry" \
    --todoist-project "Testnet Registry"

echo "Syncing Platform Reach Expansion project..."
todoist dev linear-sync \
    --linear-team Tech \
    --linear-project "Platform Reach Expansion" \
    --todoist-project "Platform Reach Expansion"

echo "Syncing Launchpad Improvements project..."
todoist dev linear-sync \
    --linear-team Tech \
    --linear-project "Launchpad Improvements" \
    --todoist-project "Node Launchpad"

echo "Syncing Antnode Automatic Upgrades project..."
todoist dev linear-sync \
    --linear-team Tech \
    --linear-project "Antnode Automatic Upgrades" \
    --todoist-project "Automatic Upgrades"
