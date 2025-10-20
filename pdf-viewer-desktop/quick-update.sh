#!/bin/bash

# Quick Update Script - Fast rebuild and install
# Use this for quick iterations during development

set -e

echo "⚡ Quick Update - Rebuilding and installing..."
echo ""

# Build
echo "🔨 Building..."
npm run build:mac > /dev/null 2>&1

# Install
echo "📥 Installing..."
rm -rf "/Applications/AI Masters PDF Viewer.app"
cp -R "dist/mac-arm64/AI Masters PDF Viewer.app" "/Applications/"

echo "✅ Done! App updated in /Applications"
echo ""
