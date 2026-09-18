# PocketVault · D14 Rolltop

**Live site: https://bei22002-cpu.github.io/pocketvault-d14/**

Product proposal, business model, and engineering package for the D14 Rolltop — a waterproof phone pouch you can use through the window, sold wholesale to retail stores. BYU-Idaho IBC, Oct 12 – Dec 16 window.

## Start here

| Link | What it is |
|------|-----------|
| [Product proposal deck](https://bei22002-cpu.github.io/pocketvault-d14/blueprints/d14-product-pitch.html) | 11 core slides + 3 appendix pages + business model canvas |
| [One-page pre-read](https://bei22002-cpu.github.io/pocketvault-d14/blueprints/d14-product-pitch-brief.html) | Decision request, trade-offs, economics, yes-vs-no. Print-ready |
| [Business model canvas](https://bei22002-cpu.github.io/pocketvault-d14/blueprints/d14-product-pitch.html#15) | Osterwalder nine-block model |
| [Blueprint gallery](https://bei22002-cpu.github.io/pocketvault-d14/blueprints/index.html) | Drawings, orthographics, BOMs, CAD downloads |
| [Speaker notes](blueprints/manufacturing/D14-PRODUCT-PITCH-NOTES.md) | Timed script, objection table, deck rationale |

## Presenting the deck

| Key | Action |
|-----|--------|
| `←` `→` | Previous / next slide |
| `N` | Toggle presenter notes |
| `A` | Jump to appendix |
| `B` | Jump to business model canvas |
| `F` | Fullscreen |

The deck is a single self-contained HTML file. No build step, no dependencies beyond a webfont.

## Structure

```
index.html              Landing page
blueprints/             Site root — decks, gallery, assets
  d14-product-pitch*    Product proposal deck and pre-read
  d14-approval*         Manufacturing (P1) vote deck
  assets/ svg/ models/  Renders, orthographics, STL + STEP
  cad/                  Parametric CadQuery builder
  videos/ products/     Demo films and product shots
```

## Caveats

Renders are concept art and the drawings are pre-freeze. Unit economics are modeled planning bands (±30–50%), not factory quotes — they stay illustrative until an RFQ lands. No IP rating is claimed until certification testing is complete; waterproof language is gated on lot dunk-QC.
