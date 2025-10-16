# 🏎️ F1 Service System - Quick Start Guide

## Launch the UI (3 Steps)

### Step 1: Start the Application
```bash
./run_ui.sh
```

Or manually:
```bash
poetry run streamlit run src/ui/app.py
```

### Step 2: Open Your Browser
The UI will automatically open at:
```
http://localhost:8501
```

### Step 3: Start Asking Questions!

**Try these example queries:**

#### Circuit Queries 🏁
- "Show me the Monaco circuit"
- "Display Silverstone"
- "Miami track"
- "Vegas circuit layout"

#### Regulation Queries 📋
- "How many points for 1st place?"
- "What are the DRS rules?"
- "Safety car procedure"
- "Penalty for track limits"

#### Combined Queries ⚡
- "Show Silverstone and explain points system"
- "Monaco circuit and DRS rules"

---

## What You'll See

### Welcome Screen
The UI features a **Red Bull Racing theme** with:
- Futuristic red & black gradient background
- Orbitron font (F1-style titles)
- Racing stripe decorations
- Glowing red accents

### Chat Interface
- Type your question in the chat input
- Get responses in 2-13 seconds
- Circuit images display with red glow borders
- Expand "Technical Details" for metadata

### System Sidebar
- **Status**: Real-time system info
- **Quick Commands**: One-click example queries
- **Clear Chat**: Reset conversation

---

## Example Session

```
You: Show me the Monaco circuit

🏎️ Processing...