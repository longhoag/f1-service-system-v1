# F1 Service System UI - Visual Design Preview

## 🎨 Red Bull Racing Theme Showcase

### Color Palette

```
┌──────────────────────────────────────────┐
│  PRIMARY COLORS                          │
├──────────────────────────────────────────┤
│  #0a0a0a  ██████  Pure Black            │
│  #1a0000  ██████  Dark Red              │
│  #dc0000  ██████  Red Bull Red          │
│  #ff4444  ██████  Bright Red (accents)  │
│  #ffffff  ██████  White (text)          │
│  #e0e0e0  ██████  Light Gray (body)     │
│  #888888  ██████  Medium Gray (labels)  │
│  #666666  ██████  Dark Gray (subtle)    │
└──────────────────────────────────────────┘
```

### Typography

```
┌──────────────────────────────────────────────┐
│  ORBITRON FONT (Titles)                      │
│  🏎️ F1 SERVICE SYSTEM                       │
│  Weight: 900, Size: 3.5rem                   │
│  Usage: Main title, section headers         │
├──────────────────────────────────────────────┤
│  RAJDHANI FONT (Body)                        │
│  Clean, technical, modern typography         │
│  Weight: 400-600, Size: 1.1rem              │
│  Usage: Messages, descriptions, labels       │
└──────────────────────────────────────────────┘
```

### Visual Effects

```
┌────────────────────────────────────────────────┐
│  GRADIENTS                                     │
│  ╔════════════════════════════════════╗        │
│  ║  Background: #0a0a0a → #1a0000   ║        │
│  ║  (Black to Dark Red, 135deg)      ║        │
│  ╚════════════════════════════════════╝        │
│                                                │
│  GLOWS                                         │
│  ╔════════════════════════════════════╗        │
│  ║ ░░░ Red Glow Effect ░░░           ║        │
│  ║ box-shadow: 0 0 20px #dc0000      ║        │
│  ╚════════════════════════════════════╝        │
│                                                │
│  RACING STRIPES                                │
│  ════════════════════════════════════          │
│  Red gradient line with glow                   │
└────────────────────────────────────────────────┘
```

## 📱 UI Layout Mockup

### Main Screen (Desktop)

```
┌───────────────────────────────────────────────────────────────────┐
│                                                                   │
│          🏎️ F1 SERVICE SYSTEM                                    │
│       POWERED BY AI · REAL-TIME INTELLIGENCE                     │
│       ═══════════════════════════════════════                    │
│                                                                   │
│   ┌─────────────────────────────────────────────────────┐       │
│   │              READY TO ASSIST                        │       │
│   │                                                       │       │
│   │     • Query F1 circuit layouts and maps             │       │
│   │     • Access official FIA regulations               │       │
│   │     • Get instant, accurate answers                 │       │
│   │                                                       │       │
│   │         Powered by GPT-4o + AWS Bedrock            │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                   │
│   ┌─ USER ──────────────────────────────────────────────┐       │
│   │ Show me the Monaco circuit                          │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                   │
│   ┌─ ASSISTANT ─────────────────────────────────────────┐       │
│   │ Here's the Monaco circuit map.                      │       │
│   │                                                       │       │
│   │ ╔═════════════════════════════════════════════╗     │       │
│   │ ║                                             ║     │       │
│   │ ║        [Monaco Circuit Image]              ║     │       │
│   │ ║        with red glowing border             ║     │       │
│   │ ║                                             ║     │       │
│   │ ╚═════════════════════════════════════════════╝     │       │
│   │ 🏁 Monaco Circuit                                   │       │
│   │                                                       │       │
│   │ 🔍 Technical Details ▼                              │       │
│   └─────────────────────────────────────────────────────┘       │
│                                                                   │
│   ╔═══════════════════════════════════════════════════╗         │
│   ║ Ask about F1 circuits or regulations...          ║         │
│   ╚═══════════════════════════════════════════════════╝         │
│                                                                   │
└───────────────────────────────────────────────────────────────────┘
```

### Sidebar (Collapsed by default)

```
┌──────────────────────┐
│      SYSTEM          │
│  ═══════════════     │
│                      │
│  Status: 🟢 Online   │
│  Model: gpt-4o       │
│  Tools: 2            │
│  Queries: 3          │
│                      │
│  ═══════════════     │
│                      │
│  Quick Commands:     │
│  ┌────────────────┐  │
│  │ 🏁 Monaco      │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ 📋 Points      │  │
│  └────────────────┘  │
│  ┌────────────────┐  │
│  │ ⚡ DRS Rules   │  │
│  └────────────────┘  │
│                      │
│  ═══════════════     │
│                      │
│  ┌────────────────┐  │
│  │ 🗑️ Clear Chat  │  │
│  └────────────────┘  │
│                      │
│  ─────────────────   │
│  F1 Service v1.0     │
│  OpenAI + Bedrock    │
└──────────────────────┘
```

### Technical Details Panel (Expanded)

```
┌─ 🔍 Technical Details ────────────────────────────────────┐
│                                                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐               │
│  │ Tools    │  │ Iterations│  │ Model    │               │
│  │   1      │  │     2     │  │  GPT     │               │
│  └──────────┘  └──────────┘  └──────────┘               │
│                                                            │
│  Tools Executed:                                          │
│  • get_circuit_image                                      │
│                                                            │
│  Response Time: 2.34s                                     │
└────────────────────────────────────────────────────────────┘
```

## 🎭 Component Styles

### Chat Message - User

```
┌─ USER MESSAGE ────────────────────────────────────┐
│ ▌                                                 │
│ ▌ Show me the Monaco circuit                     │
│ ▌                                                 │
└───────────────────────────────────────────────────┘
  ↑
  Red accent border (4px solid #dc0000)
  Dark background with slight transparency
  Rounded corners (15px)
  Box shadow with glow effect
```

### Chat Message - Assistant

```
┌─ ASSISTANT MESSAGE ───────────────────────────────┐
│ ▌                                                 │
│ ▌ Here's the Monaco circuit map.                 │
│ ▌                                                 │
│ ▌ [Circuit Image with red glow border]           │
│ ▌                                                 │
│ ▌ 🔍 Technical Details ▼                         │
│ ▌                                                 │
└───────────────────────────────────────────────────┘
  ↑
  Gray accent border (4px solid #444444)
  Same card styling as user message
  Can contain images and expandable sections
```

### Button - Primary (Red Bull Style)

```
┌──────────────────────┐
│  🏁 SHOW MONACO     │  ← Hover effect: Brighter glow
└──────────────────────┘
       ↑
  Red gradient background
  Orbitron font, uppercase
  Red glow shadow
  Smooth hover transition
```

### Input Field

```
╔═══════════════════════════════════════════╗
║ Ask about F1 circuits or regulations...  ║
╚═══════════════════════════════════════════╝
  ↑
  Red border (2px solid #dc0000)
  Dark background with transparency
  Red glow effect on focus
  White text, gray placeholder
```

## 🖼️ Image Display

### Circuit Image Frame

```
╔═════════════════════════════════════════╗
║                                         ║
║        ░░░░░░░░░░░░░░░░░░░░░           ║
║        ░ Circuit Layout    ░           ║
║        ░ [Actual .webp]    ░           ║
║        ░░░░░░░░░░░░░░░░░░░░░           ║
║                                         ║
╚═════════════════════════════════════════╝
🏁 Monaco Circuit
  ↑
  Red glow border (2px solid #dc0000)
  Shadow: 0 0 30px rgba(220, 0, 0, 0.4)
  Rounded corners (15px)
  Caption with checkered flag emoji
```

## 📊 Metrics Display

```
┌─────────────┐  ┌─────────────┐  ┌─────────────┐
│ TOOLS USED  │  │ ITERATIONS  │  │   MODEL     │
│             │  │             │  │             │
│      1      │  │      2      │  │    GPT      │
│             │  │             │  │             │
└─────────────┘  └─────────────┘  └─────────────┘
     ↑                ↑                  ↑
  Red numbers    Red numbers        Red text
  Gray labels    Dark background    Uppercase
  Border with subtle red glow
```

## 🎬 Animation & Interactions

### Loading Spinner
```
    🏎️ Processing...
    ◐  Red spinning indicator
    
    Smooth rotation animation
    Red color (#dc0000)
```

### Hover Effects
```
Button:
  Normal   → Red gradient
  Hover    → Brighter red + lift effect
  Duration → 0.3s ease transition

Expander:
  Normal   → Subtle red border
  Hover    → Bright red border + glow
```

### Scroll Behavior
```
Custom Scrollbar:
  Track:  Black (#0a0a0a)
  Thumb:  Red gradient (#dc0000 → #aa0000)
  Hover:  Brighter red (#ff0000 → #cc0000)
  Width:  10px
```

## 🌈 Theme Variations

### Dark Mode (Default)
- Background: Pure black → Dark red gradient
- Cards: Semi-transparent dark with red borders
- Text: White/light gray for readability

### Accent Highlights
- Primary actions: Red Bull red (#dc0000)
- Secondary text: Medium gray (#888888)
- Success states: Green retained for status

## 🎯 Design Principles

1. **Minimalism**: Clean, uncluttered interface
2. **Contrast**: Dark background, bright accents
3. **Consistency**: Red theme throughout
4. **Hierarchy**: Clear visual structure
5. **Responsiveness**: Adapts to screen sizes
6. **Performance**: Fast load times, smooth animations
7. **Accessibility**: High contrast ratios

## 🚀 Performance Optimizations

- CSS in single `<style>` block (no external files)
- Cached orchestrator singleton
- Efficient state management
- Optimized image loading
- Minimal re-renders

---

**Preview Status**: ✅ Complete  
**Theme**: Red Bull Racing (Red & Black)  
**Style**: Futuristic, Modern, Minimalistic  
**Ready for Production**: YES 🏁
