#!/bin/bash
# This script runs after Streamlit Cloud installs Python dependencies
# It ensures Playwright downloads its browser binaries

echo "🔧 Installing Playwright browsers..."
playwright install
