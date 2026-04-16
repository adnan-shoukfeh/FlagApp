# Globule Design System Pipeline

**Purpose:** Step-by-step instructions for building a complete design system from 12 mood photographs, producing structured design tokens, component specifications, and agent-consumable documentation.

**Last Updated:** March 2026
**Status:** Pipeline Definition — Not Yet Executed

---

## Pipeline Overview

```
12 Swiss Road Sign Photographs
        │
        ▼
┌─────────────────────────┐
│ STAGE 1: Color Extraction│  ← Claude Code (vibrant-python script)
│ vibrant-python           │
└────────────┬────────────┘
             │ 6 semantic swatches × 12 images → aggregated palette
             ▼
┌─────────────────────────┐
│ STAGE 2: Palette Refine  │  ← Human (manual, browser-based)
│ Realtime Colors          │
└────────────┬────────────┘
             │ 5 semantic roles (Text, BG, Primary, Secondary, Accent)
             ▼
┌─────────────────────────┐
│ STAGE 3: Typography      │  ← Human (Fontjoy) + Claude Code (scale generation)
│ Fontjoy + Overpass       │
└────────────┬────────────┘
             │ Font pairing + modular type scale
             ▼
┌─────────────────────────┐
│ STAGE 4: Component Design│  ← Human (Figma) + Claude Code (token structuring)
│ Figma                    │
└────────────┬────────────┘
             │ Visual component library + design decisions
             ▼
┌─────────────────────────┐
│ STAGE 5: Token Structure │  ← Claude Code (W3C DTCG JSON + Style Dictionary)
│ W3C DTCG + Style Dict.   │
└────────────┬────────────┘
             │ tokens.css + tokens.ts + tokens.json
             ▼
┌─────────────────────────┐
│ STAGE 6: Documentation   │  ← Claude Code (markdown + HTML preview)
│ Markdown + HTML Preview  │
└────────────┬────────────┘
             │ Human-viewable style guide + agent-readable docs
             ▼
┌─────────────────────────┐
│ STAGE 7: Agent Integration│ ← Claude Code (CLAUDE.md + Skills + MCP)
│ Skills + Storybook MCP   │
└─────────────────────────┘
```

**Cost:** Figma Professional ($15/month). Everything else is free.

---

## Prerequisites

### Tools to Install/Set Up Before Starting

**Human tasks (do these first):**

1. **Figma account** — Sign up at figma.com, activate Professional plan ($15/month/editor). You can cancel after the design phase.
2. **Fontjoy** — No account needed. Browser tool at fontjoy.com.
3. **Realtime Colors** — No account needed. Browser tool at realtimecolors.com.
4. **12 mood photographs** — Collect your Swiss road sign / aesthetic reference images. Place them in the project at:
   ```
   design-system/
   └── inspiration/
       ├── 01.jpg
       ├── 02.jpg
       └── ... (up to 12.jpg)
   ```

**Claude Code tasks:**

1. Install vibrant-python: `uv add vibrant-python` (or `pip install vibrant-python`)
2. Install Pillow (dependency): `uv add Pillow`
3. Verify installation: `python -c "from vibrant import Vibrant; print('OK')"`

### File Structure (Target State)

After completing the full pipeline, your monorepo should look similar to:

```
project-root/
├── backend/                          # Existing Django backend
│
├── frontend/                         # React web app (to be scaffolded)
│   └── src/
│       └── tokens/                   # Generated token files go here
├── design-system/                    # NEW: Design system source of truth
│   ├── inspiration/                  # Your 12 reference photographs
│   │   └── *.jpg
│   ├── extraction/                   # Color extraction scripts + output
│   │   ├── extract_palette.py        # vibrant-python extraction script
│   │   └── raw_palette.json          # Raw extraction results
│   ├── tokens/                       # W3C DTCG token source files
│   │   ├── colors.tokens.json
│   │   ├── typography.tokens.json
│   │   ├── spacing.tokens.json
│   │   └── components.tokens.json
│   ├── docs/                         # Human-readable + agent-readable docs
│   │   ├── style-guide.md            # Master style guide (markdown)
│   │   ├── colors.md                 # Color palette documentation
│   │   ├── typography.md             # Typography system documentation
│   │   ├── components.md             # Component specifications
│   │   └── patterns.md               # UI patterns and usage guidelines
│   ├── preview/                      # Visual preview for human sign-off
│   │   └── index.html                # Standalone HTML style guide viewer
│   ├── build/                        # Style Dictionary output
│   │   ├── css/
│   │   │   └── tokens.css            # CSS custom properties
│   │   └── ts/
│   │       └── tokens.ts             # TypeScript constants
│   └── style-dictionary.config.js    # Style Dictionary build config
├── .claude/                          # Claude Code agent configuration
│   ├── skills/
│   │   └── design-system/
│   │       ├── SKILL.md              # Agent skill instructions
│   │       └── token-reference.json  # Quick-access token values
│   └── rules/
│       └── design-system.md          # Enforced design rules
├── CLAUDE.md                         # Updated with design system references
└── .storybook/                       # Storybook config (when frontend exists)
    └── main.js
```

---

## Stage 1: Color Extraction with vibrant-python

**Who:** Claude Code builds the script and runs it. Human provides the images.

### Context for Claude Code

vibrant-python extracts six semantic color swatches from each image:
- **Vibrant** — the most saturated, visually prominent color
- **Muted** — a desaturated version of the dominant color
- **DarkVibrant** — a dark, saturated color
- **DarkMuted** — a dark, desaturated color
- **LightVibrant** — a light, saturated color
- **LightMuted** — a light, desaturated color

Each swatch includes the color itself plus recommended title/body text colors for WCAG contrast compliance.

### Task: Create `design-system/extraction/extract_palette.py`

**Claude Code should implement:**

```python
"""
Color palette extraction from mood photographs using vibrant-python.

Processes all images in design-system/inspiration/ and produces:
1. Per-image swatch data (6 semantic swatches each)
2. Aggregated palette with frequency-weighted clustering
3. Structured JSON output at design-system/extraction/raw_palette.json

Usage:
    python design-system/extraction/extract_palette.py

Dependencies:
    - vibrant-python (uv add vibrant-python)
    - Pillow (uv add Pillow)
"""
```

**Requirements for the script:**

1. Scan `design-system/inspiration/` for all `.jpg`, `.jpeg`, `.png` files
2. For each image, extract all 6 swatches using vibrant-python's `Vibrant.from_filename()` method
3. Store per-image results with the swatch name, hex color, RGB values, population (pixel count), and recommended text colors
4. Aggregate across all images:
   - Group all extracted colors by swatch category (all Vibrant colors together, all Muted together, etc.)
   - For each category, find the most frequently occurring color (highest total population)
   - Also compute the average color per category as a fallback
5. Output `raw_palette.json` with this structure:

```json
{
  "extraction_date": "2026-03-11T...",
  "image_count": 12,
  "per_image": {
    "01.jpg": {
      "Vibrant": {"hex": "#2D6A4F", "rgb": [45, 106, 79], "population": 12450, "title_text": "#FFFFFF", "body_text": "#FFFFFF"},
      "Muted": {"hex": "...", ...},
      "DarkVibrant": {"hex": "...", ...},
      "DarkMuted": {"hex": "...", ...},
      "LightVibrant": {"hex": "...", ...},
      "LightMuted": {"hex": "...", ...}
    }
  },
  "aggregated": {
    "Vibrant": {"dominant": {"hex": "...", "rgb": [...], "frequency": 8}, "average": {"hex": "...", "rgb": [...]}},
    "Muted": {"dominant": {...}, "average": {...}},
    "DarkVibrant": {"dominant": {...}, "average": {...}},
    "DarkMuted": {"dominant": {...}, "average": {...}},
    "LightVibrant": {"dominant": {...}, "average": {...}},
    "LightMuted": {"dominant": {...}, "average": {...}}
  },
  "suggested_palette": {
    "primary": "#...",
    "secondary": "#...",
    "accent": "#...",
    "background_light": "#...",
    "background_dark": "#...",
    "text_primary": "#...",
    "text_secondary": "#...",
    "text_on_primary": "#..."
  }
}
```

6. The `suggested_palette` section should map the aggregated semantic swatches to UI roles:
   - `primary` ← Vibrant (dominant)
   - `secondary` ← Muted (dominant)
   - `accent` ← LightVibrant or DarkVibrant (whichever has higher contrast with primary)
   - `background_light` ← LightMuted (dominant)
   - `background_dark` ← DarkMuted (dominant)
   - `text_primary` ← DarkMuted or DarkVibrant (whichever is darker)
   - `text_secondary` ← Muted (average)
   - `text_on_primary` ← Use Vibrant's recommended title_text color

7. Print a summary table to stdout showing the suggested palette with hex values and a visual preview hint

### Verification

After running, confirm:
- `raw_palette.json` exists and is valid JSON
- All 12 images were processed (check `image_count`)
- No swatch categories are entirely null (some images may not yield all 6, that's OK — but the aggregated values should all be populated)
- The `suggested_palette` values look reasonable (greens and reds should dominate given Swiss road sign imagery)

### Human Review Point

**After Stage 1, the human should:**
1. Open `raw_palette.json` and review the `suggested_palette` section
2. Note which colors feel right and which feel off
3. These values are a starting point — Stage 2 refines them

---

## Stage 2: Palette Refinement with Realtime Colors

**Who:** Human only. This is a manual, visual refinement step.

### Instructions for Human

1. Go to **realtimecolors.com**
2. Enter the `suggested_palette` values from Stage 1:
   - **Text color** ← `text_primary` hex value
   - **Background color** ← `background_light` hex value
   - **Primary color** ← `primary` hex value
   - **Secondary color** ← `secondary` hex value
   - **Accent color** ← Use `accent` hex value, or the Swiss red (#C1121F) if the extraction didn't surface a strong red
3. The tool renders these colors on a realistic website layout in real-time
4. Toggle between **light mode** and **dark mode** to verify both work
5. Adjust colors until the palette feels cohesive and matches the Swiss road sign aesthetic
6. Use the **Fonts** panel to set Overpass as the primary font (this confirms typography feels right with the palette)

### Key Adjustments to Consider

- **Swiss green** should be the primary color. If vibrant-python extracted something too bright or too muted, manually adjust toward the classic Swiss road sign green range (~#2D6A4F to #1B4332)
- **Swiss red** should appear as accent or secondary. Classic range: ~ #C1121F to #A4161A
- **Background** should be neutral — off-white or warm gray, not pure white
- **Dark mode** background should be a very dark green-gray, not pure black

### Export Your Palette

When satisfied:
1. Click the **Export** button in Realtime Colors
2. Export as **CSS Variables** — save this output
3. Also export as **Tailwind CSS** config — save this output
4. Create a file `design-system/palette-final.json` with your final 5 colors plus their tint/shade scales:

```json
{
  "finalized_date": "2026-03-XX",
  "source": "Realtime Colors (manual refinement of vibrant-python extraction)",
  "colors": {
    "text": {"hex": "#f5fffb", "role": "Primary text color"},
    "background": {"hex": "#064127", "role": "Page background"},
    "primary": {"hex": "#017e42", "role": "Swiss green — buttons, links, primary actions"},
    "secondary": {"hex": "#3d773c", "role": "Swiss red — alerts, badges, streaks"},
    "accent": {"hex": "#9c2b2d", "role": "Warm accent — highlights, active states"}
  },
  "css_export": "--text: #f5fffb; 
  --background: #064127; 
  --primary: #017e42;
  --secondary: #3d773c;
  --accent: #9c2b2d;",
  "tailwind_export": "colors: {
 'text': '#f5fffb',
 'background': '#064127',
 'primary': '#017e42',
 'secondary': '#3d773c',
 'accent': '#9c2b2d',
},
"
}
```

> **Note:** The hex values above are illustrative. Use your actual finalized values.

---

## Stage 3: Typography System

**Who:** Human picks the font pairing on Fontjoy. Claude Code generates the type scale tokens.

### Part A: Font Pairing (Human)

1. Go to **fontjoy.com**
2. Click **Lock** on the first font slot and type **Overpass**
3. Click **Generate** to get AI-suggested complementary fonts
4. You're looking for a secondary font — most likely used for:
   - Long-form body text on the country info pages
   - Subtle contrast for descriptive content vs. UI chrome
5. Good pairings to look for: a readable serif (Merriweather, Source Serif Pro) or a complementary sans-serif (Inter, Work Sans) that doesn't clash with Overpass
6. You may decide Overpass alone is sufficient (many apps use a single font family). That's a valid choice.
7. Record your decision:

```
Primary font: Overpass (Google Fonts, SIL Open Font License)
Secondary font: Kameron
Monospace font: Palanquin
```

### Part B: Type Scale Generation (Claude Code)

**After the human confirms font choices**, Claude Code should generate the type scale.

**Task: Create `design-system/tokens/typography.tokens.json`**

Use a **Major Third (1.250)** modular scale with a 16px base size. Generate these levels:

| Token Name    | Scale Step | Desktop Size | Mobile Size | Usage                     |
|---------------|-----------|-------------|-------------|---------------------------|
| `display`     | +5        | 48.83px     | 39.06px     | Hero headings             |
| `h1`          | +4        | 39.06px     | 31.25px     | Page titles               |
| `h2`          | +3        | 31.25px     | 25.00px     | Section headings          |
| `h3`          | +2        | 25.00px     | 20.00px     | Card titles               |
| `h4`          | +1        | 20.00px     | 18.00px     | Subsection headings       |
| `body`        | 0 (base)  | 16.00px     | 16.00px     | Body text                 |
| `body-small`  | -1        | 12.80px     | 13.00px     | Secondary text, captions  |
| `caption`     | -2        | 10.24px     | 11.00px     | Labels, fine print        |

**Implementation notes for Claude Code:**
- Desktop sizes use the exact Major Third ratio (16 × 1.25^n)
- Mobile sizes are slightly compressed — use floor of desktop values with a minimum of 11px for readability
- Include line heights: 1.1 for display/h1, 1.2 for h2/h3/h4, 1.5 for body, 1.4 for body-small/caption
- Include font weights: display/h1 = 700, h2/h3 = 600, h4 = 500, body = 400, body-small/caption = 400
- Letter spacing: display/h1 = -0.02em (tight), body = 0 (normal), caption = 0.02em (slightly loose)
- Format as W3C DTCG tokens (see Stage 5 for format spec)

### Verification

- Confirm the scale produces readable sizes at both breakpoints
- Verify line heights ensure comfortable reading
- Check that display heading doesn't exceed viewport width on 375px screens

---

## Stage 4: Component Design in Figma

**Who:** Primarily human (visual design). Claude Code assists with structuring the output.

### Part A: Figma Setup (Human)

1. Create a new Figma project: **"Globule Design System"**
2. Create a **Color Styles** library with your finalized palette from Stage 2:
   - Name them: `primary/default`, `primary/light`, `primary/dark`, `secondary/default`, etc.
   - Include your tint/shade scales if you generated them
3. Create **Text Styles** using the type scale from Stage 3:
   - `display`, `h1`, `h2`, `h3`, `h4`, `body`, `body-small`, `caption`
   - Set Overpass as the font for all (load from Google Fonts plugin)
4. Set up **two frames**:
   - Desktop frame: 1440 × 900
   - Mobile frame: 375 × 812 (iPhone standard)

### Part B: Component Design (Human)

Design the following core components in Figma. These are the minimum needed for Globule's MVP screens:

**Layout Components:**
- [ ] Navigation bar (top bar with logo, nav links, user avatar)
- [ ] Bottom tab bar (mobile — Home, Encyclopedia, Profile)
- [ ] Page container (max-width, padding, responsive breakpoints)

**Content Components:**
- [ ] Flag display card (large flag image + country name + metadata)
- [ ] Country info card (stat label + value, used on country detail pages)
- [ ] Search bar (with icon, placeholder text, clear button)
- [ ] Search result row (flag thumbnail + country name + region)

**Interactive Components:**
- [ ] Primary button (Swiss green, used for main actions)
- [ ] Secondary button (outlined, used for secondary actions)
- [ ] Danger/alert button (Swiss red, used for destructive actions)
- [ ] Text input field (with label, placeholder, error state, focus state)
- [ ] Guess input (specialized text input for the daily challenge)

**Feedback Components:**
- [ ] Streak badge (red national route badge shape — shows streak count)
- [ ] Difficulty badge (green European route badge shape — shows tier)
- [ ] Toast notification (success, error, info variants)
- [ ] Attempt indicator (3 dots/circles showing remaining attempts)

**Data Display Components:**
- [ ] Stats card (icon + number + label, used on profile)
- [ ] Country detail section (heading + grid of stat rows)
- [ ] Map container (placeholder for Leaflet embed)

### Design Guidance

- **Swiss road sign aesthetic:** Clean, functional, high-contrast. Think highway signage — clear typography, strong color blocking, rounded corners but not excessively soft.
- **Badge shapes:** The red badge (national route) is a rectangle with pointed ends (like a horizontal hexagon). The green badge (European route) is a vertical rectangle with rounded top corners. Reference Swiss road sign standards for proportions.
- **Spacing:** Use an 8px base grid. Components should snap to 8px increments for padding and margins.
- **Border radius:** Suggest 4px for small elements (buttons, inputs), 8px for cards, 12px for modals/large containers.
- **Shadows:** Minimal — the Swiss sign aesthetic is flat. Use subtle shadows only for elevation (modals, dropdowns). Prefer border-based separation.
- **Icons:** Plan to use Lucide icons (the animated variant you already selected). Design with 24px icon slots.

### Part C: Export Design Decisions (Human → Claude Code)

After completing the Figma designs, document the key decisions so Claude Code can translate them into tokens:

Create `design-system/figma-decisions.md`:

```markdown
# Figma Design Decisions

## Spacing
- Base unit: 8px
- Component padding: [inner padding values you used]
- Section gaps: [gap values between major sections]
- Card padding: [padding inside cards]

## Border Radius
- Small (buttons, inputs): Xpx
- Medium (cards): Xpx
- Large (modals, containers): Xpx
- Full (avatars, circular elements): 50%

## Shadows
- Elevation 1 (cards): [shadow values]
- Elevation 2 (dropdowns): [shadow values]
- Elevation 3 (modals): [shadow values]

## Component Specs
For each component designed, note:
- Fixed dimensions (if any)
- Min/max widths
- Responsive behavior (what changes between desktop and mobile)
- States (default, hover, active, disabled, focus, error)
- Which color tokens are used where

## Responsive Breakpoints
- Mobile: 0–767px
- Tablet: 768–1023px
- Desktop: 1024px+
```

---

## Stage 5: Token Structuring (W3C DTCG Format)

**Who:** Claude Code. Uses outputs from Stages 2, 3, and 4 as input.

### Context: W3C DTCG Token Format

The W3C Design Tokens Community Group format (stable version 2025.10) uses JSON with these conventions:

```json
{
  "color": {
    "primary": {
      "$value": "#2D6A4F",
      "$type": "color",
      "$description": "Swiss green — primary brand color for buttons and links"
    }
  }
}
```

Key rules:
- Token properties are prefixed with `$` (`$value`, `$type`, `$description`)
- Group tokens by category using nested objects
- Supported `$type` values include: `color`, `dimension`, `fontFamily`, `fontWeight`, `number`, `duration`, `cubicBezier`, `shadow`, `typography` (composite), `border` (composite)

### Task: Create Token Files

Claude Code should create these files based on the finalized values from previous stages:

**`design-system/tokens/colors.tokens.json`**
- Map all colors from `palette-final.json` (Stage 2 output)
- Include tint/shade scales (50 through 950) for primary, secondary, and neutral
- Include semantic aliases: `color.success`, `color.error`, `color.warning`, `color.info`
- Include surface colors: `color.surface.default`, `color.surface.elevated`, `color.surface.sunken`

**`design-system/tokens/typography.tokens.json`**
- Already created in Stage 3 Part B
- Verify it follows DTCG format

**`design-system/tokens/spacing.tokens.json`**
- 8px base grid: `spacing.1` = 4px, `spacing.2` = 8px, `spacing.3` = 12px, `spacing.4` = 16px, ... up to `spacing.16` = 128px
- Named aliases: `spacing.page-padding`, `spacing.card-padding`, `spacing.section-gap` (values from Figma decisions)

**`design-system/tokens/borders.tokens.json`**
- Border radius values from Figma decisions
- Border widths: `thin` = 1px, `medium` = 2px, `thick` = 3px

**`design-system/tokens/shadows.tokens.json`**
- Shadow definitions from Figma decisions
- Use DTCG composite `shadow` type

**`design-system/tokens/components.tokens.json`**
- Component-level tokens that reference the primitives above
- Example: `component.button.primary.background` → `{color.primary.default}`
- Example: `component.card.border-radius` → `{border.radius.medium}`

### Task: Configure Style Dictionary

**Create `design-system/style-dictionary.config.js`:**

```javascript
// Style Dictionary configuration for Globule design system
// Reads W3C DTCG tokens and outputs platform-specific formats

module.exports = {
  source: ["design-system/tokens/**/*.tokens.json"],
  platforms: {
    css: {
      transformGroup: "css",
      buildPath: "design-system/build/css/",
      files: [
        {
          destination: "tokens.css",
          format: "css/variables",
          options: {
            selector: ":root"
          }
        }
      ]
    },
    ts: {
      transformGroup: "js",
      buildPath: "design-system/build/ts/",
      files: [
        {
          destination: "tokens.ts",
          format: "javascript/es6"
        }
      ]
    },
    json: {
      transformGroup: "js",
      buildPath: "design-system/build/json/",
      files: [
        {
          destination: "tokens.json",
          format: "json/flat"
        }
      ]
    }
  }
};
```

**Install and run:**
```bash
npm install -g style-dictionary
# or in the project: npm install --save-dev style-dictionary
cd project-root
style-dictionary build --config design-system/style-dictionary.config.js
```

### Verification

After building:
- `design-system/build/css/tokens.css` exists and contains `:root { --color-primary-default: #...; ... }`
- `design-system/build/ts/tokens.ts` exists and contains `export const ColorPrimaryDefault = "#...";`
- `design-system/build/json/tokens.json` exists as a flat key-value map
- All token values resolve correctly (no unresolved references like `{color.primary.default}` in output)

---

## Stage 6: Documentation

**Who:** Claude Code generates all files. Human reviews and signs off.

### Part A: Markdown Style Guide (Agent-Readable)

Claude Code should generate focused, concise markdown files under `design-system/docs/`. Each file should be under 300 lines to keep within comfortable context window limits.

**`design-system/docs/style-guide.md`** — Master overview:
- Project name, aesthetic direction ("Swiss road sign inspired")
- Links to all sub-documents
- Quick-reference palette table (token name | hex | usage)
- Quick-reference type scale table
- Summary of key design principles

**`design-system/docs/colors.md`**:
- Full color palette with hex, RGB, and OKLCH values
- Semantic role mapping (which color is used for what)
- Contrast ratios for all text-on-background combinations
- Do's and don'ts (e.g., "Never use primary green on secondary red — insufficient contrast")

**`design-system/docs/typography.md`**:
- Font families and where to load them
- Complete type scale with all properties
- Usage guidance per level (when to use h2 vs h3)
- Font loading strategy for web (Fontsource) and React Native (expo-google-fonts)

**`design-system/docs/components.md`**:
- Component inventory with props/variants
- For each component: when to use it, what tokens it consumes
- Responsive behavior notes
- Accessibility requirements (ARIA roles, focus management)

**`design-system/docs/patterns.md`**:
- Page layout patterns (daily challenge page, country info page, encyclopedia)
- Form patterns (guess input, search)
- Navigation patterns (desktop top nav, mobile bottom tabs)
- Responsive breakpoint behavior

### Part B: HTML Visual Preview (Human Sign-Off)

**Task: Create `design-system/preview/index.html`**

This is a standalone HTML file that the human opens in a browser to visually inspect the entire design system. It should:

1. Load the generated `tokens.css` file
2. Load Overpass from Google Fonts CDN (and the secondary font if one was chosen)
3. Display sections for:
   - **Color palette** — swatches with hex labels, light/dark mode toggle
   - **Typography scale** — each level rendered with actual text
   - **Spacing scale** — visual blocks showing each spacing value
   - **Component previews** — rendered HTML/CSS approximations of each component:
     - Buttons (all variants and states)
     - Input fields (default, focus, error, disabled)
     - Cards (flag card, stat card, info card)
     - Badges (streak badge, difficulty badge)
     - Navigation (top bar, bottom tabs)
     - Toast notifications
4. Be fully responsive (demonstrates both desktop and mobile layouts)
5. Include a dark mode toggle that switches CSS custom properties
6. Be self-contained (no build step, no npm — just open the HTML file)

**This HTML file is the primary visual sign-off artifact.** The human reviews it in a browser and provides feedback. Claude Code iterates on the design system based on that feedback.

### Verification

- HTML preview loads correctly when opened as a local file
- All colors match the finalized palette
- Typography renders with correct fonts, sizes, and weights
- Dark mode toggle works and all colors adapt appropriately
- Components look reasonable on both desktop (1440px) and mobile (375px) viewport widths

---

## Stage 7: Agent Integration

**Who:** Claude Code sets everything up. Human verifies.

### Part A: Update CLAUDE.md

Add a design system section to the existing `CLAUDE.md`:

```markdown
## Design System

The Globule design system is documented at `design-system/docs/`.
Token source files are at `design-system/tokens/` in W3C DTCG format.
Built token outputs are at `design-system/build/`.

**Rules:**
- ALWAYS use design tokens from the design system — never hardcode colors, spacing, font sizes, or shadows
- Import CSS tokens via `design-system/build/css/tokens.css`
- Import TS tokens via `design-system/build/ts/tokens.ts`
- Reference `design-system/docs/components.md` before creating any new UI component
- Reference `design-system/docs/patterns.md` for page layout decisions
- When in doubt about a design decision, check `design-system/docs/style-guide.md`
- The visual aesthetic is "Swiss road sign" — clean, functional, high-contrast
- Primary font is Overpass. Secondary font is [CHOSEN FONT or "none"].
- Primary color is Swiss green. Secondary/accent is Swiss red.
```

### Part B: Create Claude Code Agent Skill

**Create `.claude/skills/design-system/SKILL.md`:**

```markdown
# Design System Skill

## Purpose
Apply the Globule design system consistently when building frontend components.

## When to Use
- Creating any React component
- Styling any HTML element
- Choosing colors, fonts, spacing, or shadows
- Building page layouts
- Implementing responsive behavior

## Token Access
- CSS: `design-system/build/css/tokens.css` (import in stylesheets)
- TypeScript: `design-system/build/ts/tokens.ts` (import in components)
- Raw JSON: `design-system/build/json/tokens.json` (for programmatic access)
- Source (DTCG): `design-system/tokens/*.tokens.json` (for reference)

## Quick Reference

### Colors
[Claude Code: paste the color table from style-guide.md here]

### Type Scale
[Claude Code: paste the type scale table here]

### Spacing
[Claude Code: paste the spacing scale here]

## Component Patterns
See `design-system/docs/components.md` for the full component library.

Key components:
- Buttons: Always use token colors, never hardcode. Primary = green, Danger = red.
- Cards: Use `border.radius.medium` and `shadow.elevation-1`.
- Inputs: Include focus ring using `color.primary.default` with 2px offset.
- Badges: Streak = red badge shape, Difficulty = green badge shape.

## Responsive Rules
- Mobile-first approach
- Breakpoints: 768px (tablet), 1024px (desktop)
- Use CSS Grid for page layouts, Flexbox for component internals
- Font sizes compress on mobile (see typography tokens)
```

**Create `.claude/skills/design-system/token-reference.json`:**

This should be a copy of `design-system/build/json/tokens.json` — the flat key-value token map for fast lookups.

### Part C: Design System Enforcement Rules

**Create `.claude/rules/design-system.md`:**

```markdown
# Design System Enforcement

## Hard Rules (Never Break)
- Never hardcode hex colors — always use CSS custom properties or TS token constants
- Never hardcode pixel values for spacing — use spacing tokens
- Never use fonts other than Overpass (and the chosen secondary font)
- Never set font sizes directly — use the type scale tokens
- Always include dark mode support using CSS custom properties
- All interactive elements must have visible focus indicators
- All text-on-background combinations must meet WCAG AA contrast (4.5:1 for body text, 3:1 for large text)

## Soft Rules (Prefer, but Exceptions Allowed)
- Prefer 8px grid alignment for all spacing
- Prefer CSS Grid for layouts, Flexbox for alignment within components
- Prefer mobile-first responsive development
- Prefer semantic HTML elements over generic divs
```

### Part D: Storybook MCP Integration (When Frontend Exists)

> **Note:** This step happens AFTER the React frontend is scaffolded. Include it in the pipeline doc now so the setup instructions are captured.

When the frontend is ready:

1. Install Storybook:
   ```bash
   cd frontend
   npx storybook@latest init
   ```

2. Install the MCP addon:
   ```bash
   npm install --save-dev @storybook/addon-mcp
   ```

3. Configure in `.storybook/main.js`:
   ```javascript
   module.exports = {
     addons: [
       '@storybook/addon-mcp',
       // ... other addons
     ],
   };
   ```

4. The MCP addon exposes a Component Manifest — a structured representation of your Storybook components (props, variants, descriptions) — that Claude Code can query via the Model Context Protocol. This means Claude Code will have live access to your component library when implementing features.

### Part E: Figma MCP Integration

1. Install the Figma MCP server for Claude Code:
   ```bash
   # In your Claude Code MCP configuration, add:
   # Server: Figma MCP
   # This connects Claude Code to your Figma files for reading design context
   ```

2. This enables Claude Code to:
   - Read your Figma component designs directly
   - Extract spacing, colors, and layout relationships
   - Reference your visual designs while generating code

> **Note:** Figma MCP requires the Figma Dev Mode (included in Professional plan). The exact MCP server setup depends on your Claude Code configuration — check Claude Code docs for current MCP server management instructions.

---

## Pipeline Execution Checklist

Use this to track progress:

### Stage 1: Color Extraction
- [ ] 12 mood images placed in `design-system/inspiration/`
- [ ] vibrant-python installed (`uv add vibrant-python Pillow`)
- [ ] `extract_palette.py` script created by Claude Code
- [ ] Script executed successfully
- [ ] `raw_palette.json` generated and reviewed
- [ ] Human noted which colors feel right and which need adjustment

### Stage 2: Palette Refinement
- [ ] Colors entered in Realtime Colors
- [ ] Light mode reviewed and adjusted
- [ ] Dark mode reviewed and adjusted
- [ ] CSS Variables exported
- [ ] Tailwind config exported
- [ ] `palette-final.json` created with finalized values

### Stage 3: Typography
- [ ] Overpass confirmed as primary font
- [ ] Secondary font selected on Fontjoy (or decided "Overpass only")
- [ ] Type scale tokens generated by Claude Code
- [ ] `typography.tokens.json` created

### Stage 4: Component Design
- [ ] Figma project created with color and text styles
- [ ] Desktop and mobile frames set up
- [ ] All layout components designed
- [ ] All content components designed
- [ ] All interactive components designed
- [ ] All feedback components designed
- [ ] All data display components designed
- [ ] `figma-decisions.md` written with spacing, radius, shadow values

### Stage 5: Token Structuring
- [ ] `colors.tokens.json` created
- [ ] `spacing.tokens.json` created
- [ ] `borders.tokens.json` created
- [ ] `shadows.tokens.json` created
- [ ] `components.tokens.json` created
- [ ] Style Dictionary installed and configured
- [ ] Build runs successfully
- [ ] CSS, TS, and JSON outputs generated

### Stage 6: Documentation
- [ ] `style-guide.md` written
- [ ] `colors.md` written
- [ ] `typography.md` written
- [ ] `components.md` written
- [ ] `patterns.md` written
- [ ] `preview/index.html` created
- [ ] HTML preview reviewed in desktop browser
- [ ] HTML preview reviewed in mobile viewport (DevTools)
- [ ] Dark mode verified in HTML preview
- [ ] **Human sign-off on visual preview**

### Stage 7: Agent Integration
- [ ] CLAUDE.md updated with design system section
- [ ] `.claude/skills/design-system/SKILL.md` created
- [ ] `.claude/skills/design-system/token-reference.json` created
- [ ] `.claude/rules/design-system.md` created
- [ ] Storybook MCP configured (after frontend scaffold)
- [ ] Figma MCP configured

---

## Important Notes

### Relationship to Existing Tech Stack Decisions

Your CLAUDE.md currently specifies **MUI (Material-UI) for web** and **React Native Paper for mobile**. The design system pipeline produces custom tokens that can theme MUI/Paper OR replace them. Here are your options — this decision can wait until frontend scaffolding:

1. **Theme MUI/Paper with your tokens** — Use MUI's `createTheme()` and Paper's `MD3LightTheme` with your Swiss road sign colors and Overpass font. Fastest path, leverages existing component libraries. Components will look "Material-ish" with your branding.

2. **Build custom components with tokens** — Skip MUI/Paper entirely, build components from scratch using your tokens + Tailwind (or CSS modules). Most control, truest to the Swiss aesthetic, but more work.

3. **Hybrid** — Use MUI/Paper for complex components (data tables, dialogs) but build hero components (flag cards, badges, navigation) custom. Practical middle ground.

This decision doesn't affect the pipeline — the tokens work with any approach.

### Iterative Refinement

This pipeline isn't strictly linear. Expect to loop:
- After Stage 4 (Figma), you may revisit Stage 2 (colors) if something doesn't work visually
- After Stage 6 (HTML preview), you may revisit Stage 4 (Figma) to adjust components
- After building real screens, you'll add tokens and update docs

The design system is a living document. The pipeline gets you to v1.0 — expect ongoing evolution.

### Browser Optimization (Desktop + Mobile)

All components in this design system target browser rendering (both desktop and mobile Safari/Chrome). This means:
- CSS is the primary styling mechanism (not React Native StyleSheet)
- Responsive design uses CSS media queries and container queries
- Touch targets should be minimum 44×44px for mobile
- Font rendering should be tested on both macOS and iOS Safari
- When you later build the React Native app, the TS tokens provide the same values for React Native's StyleSheet, but the component implementations will differ

### MCP Availability Note

Storybook MCP and Figma MCP are relatively new (late 2025 / early 2026). If you encounter setup issues:
- Storybook MCP: Check https://storybook.js.org/addons/@storybook/addon-mcp for current docs
- Figma MCP: Check Claude Code's MCP server configuration docs
- Both are optional enhancements — the markdown docs + Claude Skills provide the core agent integration even without MCP
