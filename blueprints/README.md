# Nereid Interface Catalog — Build Package

Static build blueprints + **fabricated CAD** for all **18** Nereid designs (Rev A).

## Status

| Deliverable | Count |
|-------------|------:|
| Concept PNG blueprints | 18 |
| SVG orthographic sheets | 18 |
| STL print files | 56 |
| STEP CAD files | 56 |
| Designs with full BOM + assembly | 18 |

## Open locally

```bash
npx --yes serve blueprints
```

Or open `blueprints/index.html` (use a local server for CAD manifest fetch).

## Rebuild 3D models

```bash
python blueprints/cad/build_all.py
```

Requires: `cadquery` (Python).

## Layout

| Path | What |
|------|------|
| `index.html` | Gallery: PNG + SVG + BOM + CAD downloads |
| `d14-product-pitch.html` | D14 product proposal — 11 core slides + 3 appendix (← → nav, `N` notes, `A` appendix, `F` fullscreen) |
| `d14-product-pitch-brief.html` | One-page pre-read / leave-behind with the yes-vs-no decision |
| `manufacturing/D14-PRODUCT-PITCH-NOTES.md` | Timed script, objection table, and why the deck is structured this way |
| `designs.js` | Dimensions, BOM, assembly |
| `assets/` | Concept blueprint PNGs |
| `svg/` | Printable orthographics |
| `models/<ID>/` | STL + STEP + MANIFEST |
| `cad/build_all.py` | Parametric CadQuery builder |
| `PRINT_GUIDE.md` | How to print and assemble |

## Shared envelope

- Phone cavity: ~147 × 71 × 8 mm class
- Rigid standard outer: ~168 × 88 × 26 mm
- Full-screen aperture: ~148 × 70 mm

Weights/depths are engineering targets. Prototypes must be pressure-tested before water use.
