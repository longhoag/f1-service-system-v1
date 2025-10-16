# F1 Service System - Streamlit UI

## Red Bull Racing Theme 🏎️

Futuristic, modern, minimalistic interface with Red Bull Racing colors (red & black).

## Features

✨ **Design Elements:**
- Dark gradient background (black to dark red)
- Red Bull Racing red (#dc0000) accents
- Futuristic Orbitron & Rajdhani fonts
- Glowing borders and shadows
- Racing stripe decorations
- Minimalistic card-based layout

🎨 **UI Components:**
- Chat interface with message history
- Circuit image display with futuristic frames
- Collapsible technical details panel
- System status sidebar
- Quick command buttons
- Real-time performance metrics

## Running the UI

### Option 1: Quick Launch (Recommended)
```bash
./run_ui.sh
```

### Option 2: Manual Launch
```bash
poetry run streamlit run src/ui/app.py
```

### Option 3: Custom Port
```bash
poetry run streamlit run src/ui/app.py --server.port 8080
```

## UI Layout

```
┌─────────────────────────────────────────────────────────┐
│  🏎️ F1 SERVICE SYSTEM                                   │
│  POWERED BY AI · REAL-TIME INTELLIGENCE                 │
│  ─────────────────────────────────────────────────      │
│                                                         │
│  ┌─────────────────────────────────────────────┐       │
│  │  READY TO ASSIST                            │       │
│  │  • Query F1 circuit layouts                 │       │
│  │  • Access official FIA regulations          │       │
│  │  • Get instant, accurate answers            │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  ┌─ USER ──────────────────────────────────────┐       │
│  │ Show me the Monaco circuit                  │       │
│  └─────────────────────────────────────────────┘       │
│                                                         │
│  ┌─ ASSISTANT ──────────────────────────────────┐      │
│  │ Here's the Monaco circuit map               │      │
│  │ [Circuit Image with red glow border]        │      │
│  │ 🔍 Technical Details ▼                      │      │
│  └─────────────────────────────────────────────┘      │
│                                                         │
│  [Ask about F1 circuits or regulations...]            │
└─────────────────────────────────────────────────────────┘
```

## Sidebar Features

```
┌─ SYSTEM ───────────────┐
│ Status: 🟢 Online      │
│ Model: gpt-4o          │
│ Tools: 2               │
│ Queries: 5             │
│                        │
│ Quick Commands:        │
│ ┌──────────────────┐  │
│ │ 🏁 Monaco        │  │
│ │ 📋 Points        │  │
│ │ ⚡ DRS Rules     │  │
│ └──────────────────┘  │
│                        │
│ ┌──────────────────┐  │
│ │ 🗑️ Clear Chat    │  │
│ └──────────────────┘  │
└────────────────────────┘
```

## Theme Customization

The UI uses a custom Red Bull Racing theme defined in CSS:

**Primary Colors:**
- Background: `#0a0a0a` (pure black) → `#1a0000` (dark red)
- Accent: `#dc0000` (Red Bull red)
- Text: `#ffffff` (white), `#e0e0e0` (light gray)
- Borders: `rgba(220, 0, 0, 0.3)` (semi-transparent red)

**Fonts:**
- Titles: `Orbitron` (futuristic, racing-inspired)
- Body: `Rajdhani` (clean, modern, technical)

**Effects:**
- Red glow shadows: `box-shadow: 0 0 20px rgba(220, 0, 0, 0.3)`
- Gradient backgrounds: `linear-gradient(135deg, #dc0000 0%, #aa0000 100%)`
- Backdrop blur: `backdrop-filter: blur(10px)`

## Example Queries

The UI supports natural language queries:

**Circuit Queries:**
- "Show me the Monaco circuit"
- "Display Silverstone layout"
- "Miami track map"
- "Vegas circuit"

**Regulation Queries:**
- "How many points for 1st place?"
- "What are the DRS rules?"
- "Safety car procedure"
- "Penalty for track limits"

**Combined Queries:**
- "Show Silverstone and explain the points system"
- "Monaco circuit and DRS rules"

## Performance Metrics

The UI displays technical details for each response:

- **Tools Used:** Number of tools called (1-2)
- **Iterations:** LLM iterations (typically 2)
- **Model:** GPT-4o or GPT-5 Mini
- **Response Time:** Total processing time
- **Citations:** Number of regulation sources (if applicable)

## Architecture

```
User Input
    ↓
Streamlit Chat Interface
    ↓
Orchestrator (GPT-4o)
    ↓
Tools:
  • get_circuit_image()     → Circuit map .webp
  • query_regulations()     → AWS Bedrock RAG
    ↓
Streamlit Display:
  • Text responses
  • Circuit images with red glow
  • Metadata expandable panel
```

## Browser Compatibility

Tested on:
- ✅ Chrome (recommended)
- ✅ Firefox
- ✅ Safari
- ✅ Edge

**Note:** Custom scrollbar styling works best in Chrome/Edge.

## Troubleshooting

### Images not displaying
```python
# Check circuit maps directory
ls -la f1_2025_circuit_maps/
```

### Slow responses
- Normal: 2-13 seconds (includes Bedrock API calls)
- Check LangSmith traces for bottlenecks

### CSS not loading
- Clear browser cache
- Hard refresh: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)

## Future Enhancements

- [ ] Conversation memory (session-based)
- [ ] Image zoom/fullscreen for circuits
- [ ] Response streaming for real-time feedback
- [ ] Dark/light theme toggle
- [ ] Export chat history
- [ ] Voice input support
- [ ] Multi-language support

## Credits

**Design Inspiration:** Red Bull Racing F1 Team  
**Theme Colors:** Red Bull Racing livery (#dc0000)  
**Fonts:** Orbitron (futuristic), Rajdhani (technical)  
**Icons:** Emoji racing theme 🏎️🏁⚡

---

**Version:** 1.0  
**Status:** ✅ Production Ready  
**Theme:** Red Bull Racing (Red & Black)  
**Style:** Futuristic, Modern, Minimalistic
