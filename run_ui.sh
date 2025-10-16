#!/bin/bash

# F1 Service System - Streamlit UI Launcher
# Red Bull Racing Theme - Futuristic Interface

echo "🏎️  F1 Service System - Launching UI..."
echo ""
echo "Theme: Red Bull Racing (Red & Black)"
echo "Style: Futuristic, Modern, Minimalistic"
echo ""

# Navigate to project root
cd "$(dirname "$0")"

# Run Streamlit app
poetry run streamlit run src/ui/app.py \
    --server.port 8501 \
    --server.address localhost \
    --theme.base dark \
    --theme.primaryColor "#dc0000" \
    --theme.backgroundColor "#0a0a0a" \
    --theme.secondaryBackgroundColor "#1a0000" \
    --theme.textColor "#ffffff" \
    --browser.gatherUsageStats false

echo ""
echo "✅ UI closed"
