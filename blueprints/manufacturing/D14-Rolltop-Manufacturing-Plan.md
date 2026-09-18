# D14 Rolltop — Manufacturing Plan (Rev A)

Companion to the interactive plan canvas. Source of truth for geometry:
`blueprints/models/D14/`, `designs.js` (D14), `cad/build_all.py` → `rolltop_bezel()`.

**Approval packet for decision meeting**

| Artifact | Path |
|----------|------|
| Slide deck (present this) | `blueprints/d14-approval.html` |
| One-page leave-behind (print) | `blueprints/d14-approval-brief.html` |
| Speaker notes + Q&A | `blueprints/manufacturing/D14-SPEAKER-NOTES.md` |
| This plan | `blueprints/manufacturing/D14-Rolltop-Manufacturing-Plan.md` |

**Motion:** Authorize **P1 only** — CNC/soft-tool bezels, RF-weld fabric bodies, window + load-cell stack, dunk proof 1.5× — ceiling **$18k**, ~**5 weeks**, success = **≥5 units dunk-pass**. Not authorizing production molds, inventory, or IPX8 claims.

## Critical warning

**Printed bezels are fit-check / soft-tool only until FAIR.** Production depth rating (6 m) requires RF-welded TPU-aramid to a qualified flange, real glass, calibrated load cells, and dunk proof at **1.5× design**. Not certified for dive use until that program passes. Campus demos only on passed serials.

## Product snapshot

| Item | Value |
|------|--------|
| Envelope (deployed) | 175 × 95 × 40 mm |
| Aperture | 148 × 70 mm |
| Body | 500D aramid + TPU coat |
| Bezel | Rigid PPA/Mg + fabric clamp flange |
| Sensing | A1-style 4 load cells in bezel |
| Closure | 3 rolls + 2 side-release buckles |
| Mass target | 122 g |
| Design depth | 6 m |
| Packed volume | ~40% of rigid Nereid cases |

## Principle

Soft fabric body absorbs impact and collapses for packability. The only hard assembly is the force-sensed window bezel. Waterproofing is owned by (1) continuous RF weld at the bezel lip and (2) trained roll-and-clamp closure. Phone remains usable through glass.

**Known weak point:** hard bezel edge under direct impact — pad / bumper before calling structure done.

## Mass budget (122 g)

| Part | Mass |
|------|------|
| Aramid/TPU body + roll | 34 g |
| Bezel + window + load cells | 61 g |
| Battery + BLE | 16 g |
| Buckles + misc | 11 g |

## CAD handoff

| File | Use |
|------|-----|
| `models/D14/rigid_bezel.step` | Bezel CNC / mold cavity |
| `models/D14/window_blank.step` | Glass stand-in → real glass |
| `models/D14/fabric_cut_pattern.step` | Pattern reference / DXF export |
| `models/D14/*.stl` | FDM fit-check bezel only |

Rebuild: `python blueprints/cad/build_all.py`

## BOM (summary)

1. TPU-coated 500D aramid body (RF-weldable)  
2. Rigid bezel with continuous seal lip / flange  
3. Glass 1.5 mm + silicone mount  
4. Four load cells + flex / PCB  
5. Roll bar / clamp strip  
6. Dual side-release buckles + webbing  
7. Battery + BLE in dry pocket  
8. Edge bumper / pad (recommended)  
9. Care card: 3-fold diagram  

## Process phases

0. Engineering freeze (STEP, DXF pattern, fold spec)  
1. Materials RFQ (2 sources fabric, buckles, glass, cells)  
2. Bezel manufacture (FAIR flange flatness ≤ 0.05 mm)  
3. Fabric cut + RF weld to lip (peel coupons)  
4. Window + load cells (dry calibration)  
5. Electronics dry pocket  
6. Fold training (&lt;15 s to seal)  
7. Dunk proof 1.5× design  
8. Serialize + fold card + care kit  

## Assembly checklist

1. Incoming inspect bezel flange (flatness, finish)  
2. Cut fabric per pattern; mark fold lines  
3. RF-weld body to bezel lip; dye-pen inspect  
4. Peel coupon from same weld lot  
5. Install glass + four load cells; dry cal  
6. Mount battery/BLE dry pocket  
7. Install buckles + roll bar  
8. Operator fold drill ×10  
9. Dunk 1.5× timed; inspect fog/weep  
10. Log serial, peel, fold time, dunk result  
11. Pack with care card  

## Test gates

| Test | When | Pass |
|------|------|------|
| Dimensional FAIR | First article | Flange / pockets vs STEP |
| Peel strength | Every weld lot | ≥ process minimum (set in P1) |
| Dry force cal | 100% | Touch usable dry |
| Fold time | 100% | ≤15 s trained |
| Dunk 1.5× | 100% | No weep / no fog |
| Gloved wet touch | Sample / lot | Usable under water film |
| Sand / abrasion | Sample | No weld lift |
| Drop on bezel edge | Sample | Bumper decision |

## Prototype ladder

| Gate | Build | Allowed |
|------|--------|---------|
| P0 | Print bezel + fabric mock | Fit only |
| P1 | CNC bezel + RF weld + dunk | Bench / tank proof |
| P2 | Live cells + campus dunk demos | Supervised demos |
| P3 | Production tooling | After P1/P2 pass |
| P4 | Production SPC | Peel + dunk yield |

## Cost planning bands (not quotes)

- P1 authorization: **$7k–$18k** (midpoint ~$11k)  
- Later NRE bezel mold: roughly **$5k–$20k** (separate vote)  
- Unit COGS @ 100–250: planning **$8–$22** depending on cells/glass (re-estimate after P1 actuals)

## Open risks

- RF pinholes at lip → peel + dye-pen every lot  
- User under-rolls → stencil + training card; treat as product risk  
- Bezel edge crack → bumper options in P1  
- Weak wet touch → dunk cal reject gate  
- Abrasion → sand sample before P3  
- COGS vs $19.99 list → price/scope gate before inventory  

## Maintenance

Rinse after salt; inspect weld lip; re-train fold if new user. Do not machine-dry on high heat. Replace if glass spidered or weld lifted.
