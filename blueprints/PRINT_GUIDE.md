# Nereid — Print & Prototype Guide

All **18** designs have been built as CAD solids:

```text
blueprints/models/<ID>/
  *.stl          # FDM / SLA print
  *.step         # CNC / CAD import
  MANIFEST.json  # part list + print notes
```

**56 STL + 56 STEP** files (~12 MB). Rebuild anytime:

```bash
python blueprints/cad/build_all.py
```

## Print settings (prototype shells)

| Setting | Recommendation |
|---------|----------------|
| Material | PETG or ASA (not PLA for dunk tests) |
| Perimeters | 4–6 |
| Infill | 40–100% (walls matter more than infill) |
| Layer | 0.16–0.20 mm |
| Seams | Orient mating faces up; sand O-ring lands |
| Post | Marine epoxy or silicone on outer seams; COTS O-rings |

Window blanks are **dimensional stand-ins**. Install real glass / PC / spinel from each design BOM before any serious pressure work.

## What each design prints

| ID | Printed parts | Buy / make separately |
|----|---------------|------------------------|
| A1–A2, A4, B5–B9 | front, back, window blank | load cells / sensors, glass, BLE, seals |
| A3 | rib cage, cartridge, back, window | same + captive M3 screws |
| C10–C13 | front (w/ control bay), back, window | switches, encoder, IMU, PTT, boots |
| C11 | + tether_puck | marine bulkhead + cable |
| D14 | rigid bezel, fabric pattern plate | aramid/TPU body, RF weld |
| D15 | oil shell + lid | silicone oil, diaphragm, OLED — **not FDM-rated to 100 m** |
| D16 | A1 shells + foam_collar | syntactic foam cast or light filament |
| D17 | landscape shells + MOLLE back | dome keys, harness |
| D18 | gauntlet shells | compass repeater, strap |

## Assembly order (all rigid designs)

1. Dry-fit front + back; confirm phone cavity (~147×71×8 mm class).
2. Seat O-rings; clamp without window; leak-check with soapy air.
3. Install electronics per BOM (sensors → PCB → battery → BLE).
4. Bond / seat real window; re-check seal.
5. Pressure pot to **1.5×** design depth (air) before water.
6. Only then dunk / pool test.

## Safety

These are **digital prototypes**. They are **not** certified for immersion, diving, or life-critical use. Oilfill-100 and Titan-20 especially need PE-rated processes (metal / composite / optical) beyond desktop FDM.

## Gallery

Serve the folder and open the design pages:

```bash
npx --yes serve blueprints
```

Each design page lists STL/STEP download links from its `MANIFEST.json`.
