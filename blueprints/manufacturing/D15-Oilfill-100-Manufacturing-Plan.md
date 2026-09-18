# D15 Oilfill-100 — Manufacturing Plan (Rev A)

Companion to the interactive plan canvas. Source of truth for geometry:
`blueprints/models/D15/`, `designs.js` (D15), `cad/build_all.py` → `oilfill_housing()`.

**Approval packet for decision meeting**

| Artifact | Path |
|----------|------|
| Slide deck (present this) | `blueprints/d15-approval.html` |
| One-page leave-behind (print) | `blueprints/d15-approval-brief.html` |
| Speaker notes + Q&A | `blueprints/manufacturing/D15-SPEAKER-NOTES.md` |
| This plan | `blueprints/manufacturing/D15-Oilfill-100-Manufacturing-Plan.md` |

**Motion:** Authorize **P1 only** — CNC housings, fill station, hydro proof — ceiling **$28k**, ~**6 weeks**, success = **≥3 units at 15 bar**. Not authorizing molds, inventory, or certification claims.

## Critical warning

**Desktop FDM is fit-check only.** 100 m rating requires PE-rated PPA/PEI housing,
qualified oil/diaphragm, and hydrostatic proof at **15 bar (1.5×)**. Not certified
for dive use until that program passes.

## Product snapshot

| Item | Value |
|------|--------|
| Envelope | 170 × 90 × 35 mm |
| Wall | 1.0 mm PPA (pressure-compensated) |
| Design depth | 100 m → 10 bar |
| Proof | 15 bar |
| Mass target | 178 g |
| Sensing | Physical keys / encoder (phone screen unusable in oil) |
| Readout | Separate sealed OLED + BLE MCU |

## Principle

Rolling silicone diaphragm equalizes internal silicone-oil pressure with ambient
hydrostatic pressure so ΔP across the thin shell ≈ 0. Phone is immersed; UI is
OLED + keys only.

**Reservoir:** size ≥ 40 mL free volume for ~400 mL oil over −32…+71 °C
(CTE ~0.00095/°C × 103 °C), plus margin.

## CAD handoff

| File | Use |
|------|-----|
| `models/D15/oil_shell.step` | Body — CNC / mold |
| `models/D15/oil_lid.step` | Lid |
| `models/D15/*.stl` | FDM mock only |
| `models/D15/MANIFEST.json` | Volumes + notes |

Rebuild: `python blueprints/cad/build_all.py`

## BOM (summary)

1. PPA/PEI oil shell + lid  
2. Rolling VMQ diaphragm + retainer  
3. Silicone dielectric oil (~350–400 mL)  
4. Expansion reservoir / bladder (≥40 mL)  
5. Fill/bleed valve  
6. O-rings (double preferred)  
7. Sealed OLED + MCU + BLE  
8. Encoder + hat keys + boots  
9. Battery (prefer dry bay)  
10. Silicone cradle, 316 SS hardware  

Mass budget: shell 28 + oil/diaphragm/reservoir 52 + OLED/MCU 34 + keys 16 + battery/BLE 16 + seals/misc 32 = **178 g**.

## Process phases

0. Engineering freeze (STEP, oil calc, seals)  
1. Tooling & materials RFQ  
2. Housing manufacture (mold or CNC)  
3. Diaphragm, reservoir, valve, OLED bay  
4. Electronics SMT + firmware  
5. Dry assembly + air leak test  
6. Vacuum degas → oil fill → bleed  
7. Hydro proof 15 bar → working 10 bar  
8. Serialize, maintenance kit, pack  

## Assembly checklist

1. Incoming inspect glands (Ra ≤ 0.8 µm)  
2. Inserts / fasteners  
3. OLED dry-bay seal + leak check  
4. MCU, keys, battery feedthroughs  
5. Diaphragm + retainer; free stroke  
6. Cradle + phone clearance  
7. O-rings + lid; **air leak before oil**  
8. Degas oil; fill to mid-stroke diaphragm  
9. Bleed bubbles; weigh; log oil mass  
10. Firmware + BLE pair  
11. Hydro 15 bar / 15 min; then 10 bar functional  
12. Pack with top-off syringe kit  

## Test gates

| Test | When | Pass |
|------|------|------|
| Dimensional FAIR | First article | Glands/port vs STEP |
| Dry leak | 100% | 1 bar soap / decay |
| Hydro proof | 100% | 15 bar, 15 min, no weep |
| Hydro working | 100% | 10 bar + UI |
| Thermal soak | Lot sample | Diaphragm within stops |
| Field immersion | Pilots | Logged progression |

## Prototype ladder

| Gate | Build | Allowed |
|------|--------|---------|
| P0 | FDM dry | Fit only |
| P1 | CNC + oil | Bench hydro |
| P2 | Full electronics | Pool ≤ 5 m supervised |
| P3 | Molded samples | Quarry → rating |
| P4 | Production | After cert path |

## Cost planning bands (not quotes)

- NRE tooling + station + bring-up: roughly **$18k–$55k**  
- COGS @ ~100 pcs: roughly **$80–$170**/unit  

## Open risks

- Oil compatibility with phone seals / USB-C → 30-day soak on sacrificial units  
- Diaphragm fatigue → cycle test + inspect interval  
- User expects phone screen → OLED UX demos before sale  
- Undersized reservoir → measure oil mass then re-freeze volume  
- Mold knit lines on O-ring lands → mold-flow + gate plan  
- GF PPA killing BLE → RF window keep-out  

## Maintenance

Ship 20 mL oil + valve adapter. Top-off interval estimate 6–12 months. Fogged OLED
or oil weep → stop use, RMA.
