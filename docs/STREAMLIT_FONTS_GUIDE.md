# Formula1 Fonts - Final Implementation Guide

## ✅ Correct Implementation (Using Streamlit's config.toml)

This is the **proper way** to add custom fonts to Streamlit apps using the built-in configuration system.

## Directory Structure

```
f1-service-system-v1/
├── .streamlit/
│   └── config.toml              # ← Font configuration
├── src/
│   └── ui/
│       ├── app.py               # ← Main Streamlit app
│       └── static/              # ← Fonts location (same directory as app.py)
│           ├── Formula1-Regular_web_0.ttf
│           └── Formula1-Bold_web_0.ttf
└── font/                        # ← Original font files (backup)
    ├── Formula1-Regular_web_0.ttf
    └── Formula1-Bold_web_0.ttf
```

## Configuration Files

### 1. `.streamlit/config.toml`

```toml
# Streamlit Configuration for F1 Service System

[server]
enableStaticServing = true

# Formula 1 Official Fonts Configuration
[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Regular_web_0.ttf"
weight = 400
style = "normal"

[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Bold_web_0.ttf"
weight = 700
style = "normal"

[theme]
# Use Formula1 font for main body text
font = "Formula1"

# Red Bull Racing Theme Colors
primaryColor = "#dc0000"        # Red Bull Red
backgroundColor = "#0a0a0a"      # Deep Black
secondaryBackgroundColor = "#1a1a1a"  # Slightly lighter black
textColor = "#ffffff"            # White text
```

### 2. `src/ui/app.py` (CSS Section)

```python
# Custom CSS - Red Bull Racing Theme (Red & Black)
# Note: Formula1 fonts are loaded via .streamlit/config.toml
st.markdown("""
<style>
    /* Main background - Dark theme */
    .stApp {
        background: linear-gradient(135deg, #0a0a0a 0%, #1a0000 100%);
        color: #ffffff;
        font-family: 'Formula1', sans-serif;
    }
    
    /* Title styling - Futuristic */
    h1 {
        font-family: 'Formula1', sans-serif;
        font-weight: 700;
        font-size: 3.5rem !important;
        ...
    }
</style>
""", unsafe_allow_html=True)
```

## Key Points

### ✅ What Works
1. **Static folder location**: Must be in the same directory as `app.py` → `src/ui/static/`
2. **Config.toml location**: In `.streamlit/` directory at project root
3. **Font URL format**: `app/static/filename.ttf` (Streamlit handles the path automatically)
4. **Server setting**: `enableStaticServing = true` is required
5. **Font family**: Use simple name "Formula1" (no quotes in config.toml)

### ❌ What Doesn't Work
1. **Wrong static location**: Fonts at project root `/static/` - Streamlit won't find them
2. **Missing config.toml**: @font-face in CSS doesn't work reliably in Streamlit
3. **Wrong URL path**: Using `/app/static/` or absolute paths in config.toml
4. **Multiple locations**: Having fonts in multiple places causes confusion

## How It Works

### Streamlit's Font Loading Process

1. **Streamlit reads `config.toml`** on startup
2. **Enables static file serving** (`server.enableStaticServing = true`)
3. **Looks for `static/` folder** in the same directory as the running `.py` file
4. **Registers custom fonts** from `[[theme.fontFaces]]` sections
5. **Applies font** to UI elements based on `[theme]` settings
6. **Serves font files** at URL path `app/static/filename.ttf`

### Font Application Hierarchy

```
config.toml [theme] font = "Formula1"
    ↓
Applied to all Streamlit UI components
    ↓
CSS font-family: 'Formula1'
    ↓
Overrides specific elements as needed
```

## Setup Steps

### Step 1: Create Static Directory
```bash
mkdir -p src/ui/static
```

### Step 2: Copy Font Files
```bash
cp font/*.ttf src/ui/static/
```

### Step 3: Create config.toml
```bash
# Create if doesn't exist
mkdir -p .streamlit

# Add configuration (see above)
cat > .streamlit/config.toml << 'EOF'
[server]
enableStaticServing = true

[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Regular_web_0.ttf"
weight = 400
style = "normal"

[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Bold_web_0.ttf"
weight = 700
style = "normal"

[theme]
font = "Formula1"
EOF
```

### Step 4: Update CSS
Remove `@font-face` declarations from `app.py` - config.toml handles this now.

### Step 5: Restart Streamlit
```bash
./run_ui.sh
```

## Verification

### Check 1: No Warning Messages
✅ **Expected**: UI starts without warnings
❌ **Problem**: Warning about missing static folder
```
WARNING: Static file serving is enabled, but no static folder found...
```
**Fix**: Ensure `static/` is in the same directory as `app.py`

### Check 2: Font Files Accessible
Test in browser: http://localhost:8501/app/static/Formula1-Regular_web_0.ttf

✅ **Expected**: Font file downloads
❌ **Problem**: 404 error
**Fix**: Check `static/` folder location and `enableStaticServing` setting

### Check 3: Font Applied to UI
Inspect any text element in browser DevTools:

✅ **Expected**: `font-family: Formula1`
❌ **Problem**: Falls back to default fonts
**Fix**: Check config.toml syntax and restart Streamlit

### Check 4: Terminal Output
```bash
🏎️  F1 Service System - Launching UI...
  You can now view your Streamlit app in your browser.
  URL: http://localhost:8501

# No warnings about static folder ✅
```

## Troubleshooting

### Issue: Fonts Not Loading

**Symptoms:**
- UI shows default fonts (sans-serif, serif)
- No Formula1 font in DevTools

**Diagnosis:**
```bash
# 1. Check static folder exists
ls -lh src/ui/static/
# Should show: Formula1-Bold_web_0.ttf, Formula1-Regular_web_0.ttf

# 2. Check config.toml exists
cat .streamlit/config.toml
# Should show font configuration

# 3. Check file permissions
ls -la src/ui/static/*.ttf
# Should be readable (not 0000 or similar)
```

**Solutions:**
1. Ensure `static/` is next to `app.py`
2. Verify `enableStaticServing = true` in config.toml
3. Check font file names match config.toml exactly
4. Restart Streamlit completely (kill process and restart)

### Issue: Config Changes Not Applied

**Symptoms:**
- Modified config.toml but no changes in UI
- Old fonts still showing

**Solution:**
```bash
# Hard restart Streamlit
lsof -ti:8501 | xargs kill -9
./run_ui.sh

# Clear browser cache
# Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

### Issue: Static Folder Warning

**Symptoms:**
```
WARNING: Static file serving is enabled, but no static folder found...
```

**Cause:** Static folder in wrong location

**Solution:**
```bash
# Streamlit looks for static/ relative to app.py
# If app.py is at: src/ui/app.py
# Then static should be: src/ui/static/

# Check current location
pwd
# Should be: /path/to/f1-service-system-v1

# Move fonts to correct location
mkdir -p src/ui/static
cp font/*.ttf src/ui/static/
```

## Benefits of This Approach

### 1. **Official Streamlit Method**
- Uses built-in font system (not CSS hacks)
- More reliable and maintainable
- Updates automatically with Streamlit versions

### 2. **Cleaner Code**
- No `@font-face` CSS cluttering the app
- Configuration separate from application logic
- Easy to change fonts (just edit config.toml)

### 3. **Better Performance**
- Fonts loaded once at startup
- Streamlit optimizes font delivery
- No duplicate font loading

### 4. **Theme Integration**
- Fonts part of Streamlit theme system
- Consistent with other theme settings
- Can be changed per environment (dev/prod)

## Advanced Configuration

### Multiple Font Weights

```toml
[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Light.ttf"
weight = 300
style = "normal"

[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Regular.ttf"
weight = 400
style = "normal"

[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Bold.ttf"
weight = 700
style = "normal"

[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Black.ttf"
weight = 900
style = "normal"
```

### Italic Styles

```toml
[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-Italic.ttf"
weight = 400
style = "italic"

[[theme.fontFaces]]
family = "Formula1"
url = "app/static/Formula1-BoldItalic.ttf"
weight = 700
style = "italic"
```

### Code Font (Monospace)

```toml
[theme]
font = "Formula1"              # Body text
codeFont = "Monaco"            # Code blocks (use monospace font)
```

### Environment-Specific Fonts

**Development** (`.streamlit/config.toml`):
```toml
[theme]
font = "Formula1"
```

**Production** (`.streamlit/config.production.toml`):
```toml
[theme]
font = "Formula1"
# Use different font or settings for production
```

## File Checklist

Before deployment, ensure:

- [ ] ✅ `src/ui/static/` directory exists
- [ ] ✅ `Formula1-Regular_web_0.ttf` in `src/ui/static/`
- [ ] ✅ `Formula1-Bold_web_0.ttf` in `src/ui/static/`
- [ ] ✅ `.streamlit/config.toml` exists
- [ ] ✅ `enableStaticServing = true` in config.toml
- [ ] ✅ `[[theme.fontFaces]]` sections defined
- [ ] ✅ `font = "Formula1"` in `[theme]` section
- [ ] ✅ No `@font-face` in CSS (removed)
- [ ] ✅ CSS uses `font-family: 'Formula1'`
- [ ] ✅ UI starts without warnings
- [ ] ✅ Fonts load in browser DevTools

## Summary

✅ **Correct Setup:**
- Fonts in `src/ui/static/` (next to app.py)
- Configuration in `.streamlit/config.toml`
- `enableStaticServing = true`
- Font URL: `app/static/filename.ttf`
- No `@font-face` in CSS

✅ **Result:**
- Official Formula1 fonts load perfectly
- Clean, maintainable code
- Streamlit handles font serving
- No warnings or errors

The Formula1 fonts now load using Streamlit's official theming system! 🏎️🏁
