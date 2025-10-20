#!/bin/bash

# AI Masters PDF Viewer - Build and Install Pipeline
# This script builds the app and installs it to /Applications

set -e  # Exit on error

echo "🚀 AI Masters PDF Viewer - Build & Install Pipeline"
echo "=================================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Step 1: Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo -e "${RED}❌ Error: package.json not found${NC}"
    echo "Please run this script from the pdf-viewer-desktop directory"
    exit 1
fi

echo -e "${BLUE}📋 Step 1: Checking environment...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}❌ npm not found. Please install Node.js${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Environment OK${NC}"
echo ""

# Step 2: Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo -e "${BLUE}📦 Step 2: Installing dependencies...${NC}"
    npm install
    echo -e "${GREEN}✅ Dependencies installed${NC}"
    echo ""
else
    echo -e "${BLUE}📦 Step 2: Dependencies already installed${NC}"
    echo ""
fi

# Step 3: Clean previous build
echo -e "${BLUE}🧹 Step 3: Cleaning previous build...${NC}"
if [ -d "dist" ]; then
    rm -rf dist
    echo -e "${GREEN}✅ Previous build cleaned${NC}"
else
    echo -e "${GREEN}✅ No previous build to clean${NC}"
fi
echo ""

# Step 4: Build the app
echo -e "${BLUE}🔨 Step 4: Building application...${NC}"
echo -e "${YELLOW}This may take 1-2 minutes...${NC}"
npm run build:mac

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Build completed successfully${NC}"
else
    echo -e "${RED}❌ Build failed${NC}"
    exit 1
fi
echo ""

# Step 5: Check if DMG was created
DMG_FILE=$(find dist -name "*.dmg" -type f | head -n 1)
APP_FILE="dist/mac-arm64/AI Masters PDF Viewer.app"

if [ -z "$DMG_FILE" ]; then
    echo -e "${RED}❌ DMG file not found${NC}"
    exit 1
fi

echo -e "${BLUE}📦 Step 5: Build artifacts created${NC}"
echo -e "   DMG: ${GREEN}$DMG_FILE${NC}"
echo -e "   App: ${GREEN}$APP_FILE${NC}"
echo ""

# Step 6: Install to Applications
echo -e "${BLUE}📥 Step 6: Installing to /Applications...${NC}"

INSTALL_PATH="/Applications/AI Masters PDF Viewer.app"

# Remove old version if exists
if [ -d "$INSTALL_PATH" ]; then
    echo -e "${YELLOW}⚠️  Removing old version...${NC}"
    rm -rf "$INSTALL_PATH"
fi

# Copy new version
if [ -d "$APP_FILE" ]; then
    cp -R "$APP_FILE" "/Applications/"
    echo -e "${GREEN}✅ App installed to /Applications${NC}"
else
    echo -e "${RED}❌ App file not found${NC}"
    exit 1
fi
echo ""

# Step 7: Verify installation
if [ -d "$INSTALL_PATH" ]; then
    echo -e "${GREEN}✅ Installation verified${NC}"
    APP_SIZE=$(du -sh "$INSTALL_PATH" | cut -f1)
    echo -e "   Location: ${BLUE}$INSTALL_PATH${NC}"
    echo -e "   Size: ${BLUE}$APP_SIZE${NC}"
else
    echo -e "${RED}❌ Installation verification failed${NC}"
    exit 1
fi
echo ""

# Summary
echo "=================================================="
echo -e "${GREEN}🎉 Success! AI Masters PDF Viewer installed${NC}"
echo "=================================================="
echo ""
echo -e "${BLUE}📍 Installed at:${NC} /Applications/AI Masters PDF Viewer.app"
echo -e "${BLUE}📦 DMG available:${NC} $DMG_FILE"
echo ""
echo -e "${YELLOW}💡 Tips:${NC}"
echo "   • Launch from Applications folder or Spotlight"
echo "   • DMG file can be used to share with others"
echo "   • Run this script again after code changes"
echo ""
echo -e "${GREEN}Happy studying! 🎓${NC}"
