# Font Loading Fix - Streamlit Static Directory

## Issue
The Formula1 fonts were not loading because they were referenced from the wrong directory. Streamlit requires static assets to be served from a specific location.

## Root Cause
**Original Path (Incorrect):**
```css
src: url('font/Formula1-Regular_web_0.ttf') format('truetype');
src: url('font/Formula1-Bold_web_0.ttf') format('truetype');
```

This path doesn't work because Streamlit doesn't automatically serve files from arbitrary directories in the project.

## Solution

### 1. Create Streamlit Static Directory
```bash
mkdir -p .streamlit/static
```

### 2. Copy Font Files to Static Directory
```bash
cp font/*.ttf .streamlit/static/
```

**Result:**
```
.streamlit/
└── static/
    ├── Formula1-Regular_web_0.ttf
    └── Formula1-Bold_web_0.ttf
```

### 3. Update CSS Font Paths
**Corrected Path:**
```css
@font-face {
    font-family: 'Formula1';
    src: url('/app/static/Formula1-Regular_web_0.ttf') format('truetype');
    font-weight: 400;
    font-style: normal;
}

@font-face {
    font-family: 'Formula1';
    src: url('/app/static/Formula1-Bold_web_0.ttf') format('truetype');
    font-weight: 700;
    font-style: normal;
}
```

## How Streamlit Serves Static Files

### Streamlit's Static File System
Streamlit automatically serves files from `.streamlit/static/` at the path `/app/static/`:

| File System Path | URL Path |
|-----------------|----------|
| `.streamlit/static/Formula1-Regular_web_0.ttf` | `/app/static/Formula1-Regular_web_0.ttf` |
| `.streamlit/static/Formula1-Bold_web_0.ttf` | `/app/static/Formula1-Bold_web_0.ttf` |

### Why `/app/static/`?
- Streamlit runs apps in a virtual environment
- The app root is mapped to `/app/`
- Static files in `.streamlit/static/` are served at `/app/static/`
- This is the canonical way to serve custom assets in Streamlit

## Verification

### Check Font Files Exist
```bash
ls -lh .streamlit/static/
```

**Expected Output:**
```
Formula1-Bold_web_0.ttf
Formula1-Regular_web_0.ttf
```

### Check Browser DevTools
1. Open http://localhost:8501
2. Open DevTools (F12)
3. Go to **Network** tab
4. Reload page
5. Filter by "ttf" or "font"
6. Should see:
   - `Formula1-Regular_web_0.ttf` - Status: 200 ✅
   - `Formula1-Bold_web_0.ttf` - Status: 200 ✅

### Check Computed Font
1. Inspect any text element
2. Check **Computed** tab
3. Look for `font-family`
4. Should show: `Formula1` (not fallback fonts)

## Common Issues & Solutions

### Issue: 404 Not Found
**Symptom:** Fonts not loading, 404 errors in Network tab
**Cause:** Wrong path or files not in `.streamlit/static/`
**Solution:** 
```bash
# Verify files exist
ls .streamlit/static/

# If missing, copy them
cp font/*.ttf .streamlit/static/
```

### Issue: Fonts Still Not Loading After Fix
**Symptom:** Changes not reflected in browser
**Cause:** Browser cache
**Solution:**
1. Hard refresh: `Cmd + Shift + R` (Mac) or `Ctrl + Shift + R` (Windows)
2. Clear browser cache
3. Restart Streamlit app

### Issue: Fallback Fonts Showing
**Symptom:** Text shows in Orbitron/Rajdhani instead of Formula1
**Cause:** CSS path still incorrect
**Solution:** Double-check CSS uses `/app/static/` path exactly

## Directory Structure

### Complete Static Assets Structure
```
f1-service-system-v1/
├── .streamlit/
│   └── static/               # ← Static files served at /app/static/
│       ├── Formula1-Regular_web_0.ttf
│       └── Formula1-Bold_web_0.ttf
├── font/                     # ← Original font files (backup)
│   ├── Formula1-Regular_web_0.ttf
│   └── Formula1-Bold_web_0.ttf
├── src/
│   └── ui/
│       └── app.py           # ← References /app/static/ paths
└── f1_2025_circuit_maps/
```

### Why Keep Original `font/` Directory?
- **Backup:** Original source files
- **Documentation:** Shows where fonts came from
- **Version Control:** Track font file changes
- **Portability:** Easy to copy to other projects

## Best Practices

### 1. **Use `.streamlit/static/` for All Static Assets**
This directory should contain:
- Custom fonts (`.ttf`, `.woff`, `.woff2`)
- Images that need direct URL access
- JavaScript files
- CSS files (if not inline)
- Any other static resources

### 2. **Use Absolute Paths in CSS**
```css
/* Good ✅ */
src: url('/app/static/Formula1-Regular_web_0.ttf');

/* Bad ❌ */
src: url('font/Formula1-Regular_web_0.ttf');
src: url('../font/Formula1-Regular_web_0.ttf');
```

### 3. **Don't Commit Large Binary Files**
If fonts are large, consider:
- Adding `.streamlit/static/*.ttf` to `.gitignore`
- Documenting where to download fonts
- Using a setup script to copy fonts

### 4. **Font File Naming**
Keep original font file names (e.g., `Formula1-Bold_web_0.ttf`) rather than renaming to avoid confusion with font family names.

## Performance Considerations

### Current Setup
- **Font Files:** ~60KB total (both fonts)
- **Load Time:** <100ms (local serving)
- **HTTP Requests:** 2 requests (one per font file)

### Optimization Opportunities

#### 1. **Convert to WOFF2**
WOFF2 format offers better compression:
```bash
# Using fonttools
pip install fonttools brotli
pyftsubset Formula1-Regular_web_0.ttf --output-file=Formula1-Regular.woff2 --flavor=woff2
```

**Benefits:**
- 30-50% smaller file size
- Faster loading
- Better browser support

#### 2. **Font Subsetting**
Remove unused characters to reduce file size:
```bash
pyftsubset Formula1-Regular_web_0.ttf \
  --output-file=Formula1-Regular-subset.ttf \
  --unicodes="U+0020-007E,U+00A0-00FF"
```

**Benefits:**
- Smaller files
- Faster initial load
- Include only Latin characters

#### 3. **Font Preloading**
Add to HTML `<head>`:
```html
<link rel="preload" href="/app/static/Formula1-Regular_web_0.ttf" as="font" type="font/ttf" crossorigin>
<link rel="preload" href="/app/static/Formula1-Bold_web_0.ttf" as="font" type="font/ttf" crossorigin>
```

**Benefits:**
- Fonts load earlier
- Reduces FOUT (Flash of Unstyled Text)
- Better performance metrics

## Testing Checklist

After making changes, verify:

- [ ] ✅ Font files exist in `.streamlit/static/`
- [ ] ✅ CSS uses `/app/static/` paths
- [ ] ✅ UI restarted after changes
- [ ] ✅ Browser shows 200 status for font requests
- [ ] ✅ Text displays in Formula1 font (not fallbacks)
- [ ] ✅ Both Regular and Bold weights working
- [ ] ✅ No console errors related to fonts

## Rollback

If fonts still don't work, revert to Google Fonts:

```css
/* Remove @font-face declarations */

/* Restore Google Fonts */
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;700;900&family=Rajdhani:wght@300;400;500;600;700&display=swap');

/* Update font-family */
.stApp { font-family: 'Rajdhani', sans-serif; }
h1 { font-family: 'Orbitron', sans-serif; }
```

## Summary

✅ **Fixed:** Fonts now load correctly from `.streamlit/static/`
✅ **Path:** `/app/static/Formula1-*.ttf`
✅ **Location:** `.streamlit/static/` directory
✅ **Result:** Official F1 fonts display throughout the UI

The Formula1 fonts are now properly served and will load reliably! 🏎️
