# D14 Rolltop — Manufacturer Shortlist

Research date: 2026-09-18. Public OEM capability pages only — **get quotes before treating as committed**.

Interactive version: canvas `d14-manufacturer-shortlist.canvas.tsx`

## The important constraint

D14 is a **hybrid**:
1. Soft RF-welded TPU-aramid body + roll-top  
2. Rigid force-sensed bezel (glass + 4 load cells + BLE)

Almost no phone-pouch factory will build (2). Split the BOM.

| Path | When to use |
|------|-------------|
| **A — Split BOM** | Real D14. Soft OEM + your CNC bezel + your electronics |
| **B — Window clone** | Fast campus demos: clear TPU touch film, no load cells |
| **C — US RF shop** | P1 (8–12 pcs) welding fabric to your CNC flange |

## Tier 1 — Contact this week

| Company | Location | Capable of | Willingness | MOQ cue | Contact |
|---------|----------|------------|-------------|---------|---------|
| **Vancharli Outdoor** | Quanzhou, CN | RF-weld TPU/PVC phone pouches, roll-top, touch window, OEM engineering | High | ~100 custom | service@vancharli.com · +86 187 5041 0800 · vancharlioutdoor.com |
| **Szoneier** | CN | OEM dry/wet bags, RF/heat weld, TPU, fast samples | High | ~100; samples ~10–14d | szoneier.com |
| **KeepDryBag** | Quanzhou, CN | HF/RF dry bags, IPX6–8, welding jigs | High | Custom ~300–500 | keepdrybag.com |
| **SealWerks** | Illinois, US | RF weld TPU/PVC/urethane; **prototypes** | Med–High | Quote / short run | radiofrequencywelding.com · 847-439-4565 |
| **Carolina CoverTech** | South Carolina, US | RF weld + heat seal + sewing; in-house dies; proto→volume | Med–High | Quote | carolinacovertech.com |

## Tier 2 — Volume backups

| Company | Notes |
|---------|--------|
| HoneyDryBag / Dawnjoint | Phone pouches OEM; MOQ 500; often ABS frame openings |
| Tianjin Sijia | High-volume IPX8 TPU/PVC pouches; demand real test reports |
| XMBAG (Xiamen) | TPU/nylon pouches; MOQ 500; 40–50d lead |
| DERFLEX | Coated textiles + dry bag OEM; confirm finished-bag vs roll goods |
| Vinyl Technology (CA) | US mil-grade RF dry bags; likely expensive for IBC volume |

## Practical recommendation

1. **This week:** RFQ Vancharli + Szoneier + KeepDryBag (Path A pricing at 100/250).  
2. **Same week:** Quote SealWerks **or** Carolina CoverTech for Path C P1 hybrids (your CNC bezel + their weld).  
3. **Do not** ask Asia OEMs to integrate load cells on the first email — they will pivot you to a capacitive clear pouch (Path B). Use Path B only if you consciously want a demo SKU.

## RFQ email

```
Subject: RFQ — custom roll-top phone dry pouch, RF-weld to rigid bezel flange (10 pcs sample → 100–250)

We are developing a soft-goods phone dry pouch (Nereid D14 / PocketVault). Need OEM capability for:
(1) TPU-coated nylon/aramid body
(2) RF/HF weld of body to a rigid polymer bezel with continuous seal lip (we supply CNC bezel STEP for samples)
(3) Roll-top closure: 3 folds + dual side-release buckles
(4) Bezel window opening 148×70 mm (glass/sensors by us unless you quote window bond)

Please quote: 10 prototypes; MOQ for 100 and 250; lead time; TPU grade options; air/immersion test method.

Attachments: bezel STEP, dimension sheet, fold spec.
Target: US campus / outdoor retail.
```

## Attachments to send

- `blueprints/models/D14/rigid_bezel.step`
- Outer envelope 175×95×40 mm; aperture 148×70
- Fold spec: 3 rolls minimum + dual buckles
- Material target: TPU-coated 500D; no stitches below waterline
