# Northstar Roll-Top Wallet — Design Spec v0.2

> **This document is the card wallet, not the phone pouch.** Two different
> products share this folder. This one is the locked v1 per `DECISION.md`: a
> 100 × 70 mm card wallet with a dry bag welded to its bottom edge, no window
> and no electronics. The window-bezel variant that `DECISION.md` parks as v1.1
> is drawing `D14-RT-003` — see `derived-dimensions-revC.md` and
> `renders/D14-RT-003-revC.png`. Do not cross-read dimensions between them.

> v0.2 reconciles this document with the parametric CAD model in `cad/`.
> Building the model corrected four things: the closure mechanism, the panel
> length, the loaded thickness and the sealed volume. See §9 for the log.

A slim everyday card wallet with a waterproof roll-top dry bag permanently
attached along one edge. Stowed, it reads as an ordinary minimalist wallet.
Deployed, it swallows a phone, keys and the wallet itself and seals watertight.

Source: hand sketch in `reference/original-sketch.png`.

---

## 1. Reading of the original sketch

| Sketch element | Interpretation carried into this spec |
| --- | --- |
| Hatched cylinder at the edge of the front view | Dry bag rolled into a compact cylinder, stowed flush against the wallet |
| Spiral in the side view | Roll cross-section, ~4–5 turns |
| Annotations "4" and circled "5" | Number of roll-downs required to seal |
| Long arm with curved arrow | Closure strap swinging over the roll to the buckle |
| Circled "1" / "2" on the flat strap | Strap and buckle hardware callouts |
| "Waterproof" | Welded-seam construction, no stitch penetrations below the waterline |

## 2. Core architecture

The wallet is the **anchor plate** for the closure. The bag welds to its full
bottom edge, and the strap that clamps the roll bar-tacks to the wallet itself,
so no separate closure hardware is needed and the roll always compresses
against a stiff flat surface.

An earlier draft of this spec claimed the wallet *was* the roll core. That is
not buildable: the wallet is 70 mm tall and stiffened with HDPE, so it cannot
wrap into a 25 mm roll. The bag's mouth rolls up against the wallet instead.

**Stowed.** The whole bag spirals into a 12.4 mm cylinder sitting flush under
the wallet's bottom edge, strap over the roll, buckle clipped on the front
face. Card slots stay accessible without unrolling.

**Deployed.** Unclip, unroll, and the bag opens downward into a 280 mm tube.
Load it, roll the mouth up against the wallet four times, and clip the strap
over the roll to compress it.

**Sealed.** 0.59 L enclosed, 176 mm of usable depth. Cards ride on the outside
in welded TPU slots; see §7 for why that is still an open question.

## 3. Dimensions

All values below are produced by `python -m cad.build`, which writes
`export/derived-dimensions.md` straight from the solid model.

### Wallet body

| Feature | Dimension |
| --- | --- |
| Width × height | 100 × 70 mm |
| Thickness, empty | 4.00 mm |
| Thickness, 6 cards + cash | 7.96 mm |
| Card capacity | 6–8 |

The 7.96 mm figure is the sum of the layer stack (0.6 shell + 0.8 stiffener +
0.6 liner + 0.2 slot film + 4.56 cards + 1.2 cash allowance). The 12 mm in v0.1
was a guess and was 50% too thick.

### Dry bag

| Feature | Dimension |
| --- | --- |
| Panel width (flat) | 100 mm — matches the wallet, so the roll sits flush |
| Panel length (unrolled) | 280 mm |
| Material consumed by the sealing roll | 104 mm |
| Usable depth when sealed | 176 mm |
| Cross-section, loaded | 100 × 35 mm, 14 mm corner radius |
| Sealed volume | 0.59 L |
| Fits | 6.9" phone (163 × 78 × 8.5), keys, cash |

Panel length is **sized backwards from the phone**: 163 mm of phone plus 12 mm
clearance plus the 104 mm the roll eats gives 279 mm, rounded to 280.

### Stowed envelope

| Feature | Dimension |
| --- | --- |
| Overall, including strap | 100 × 82 × 15.2 mm |
| Roll cylinder diameter | 12.4 mm |
| Roll turns | 10.9 |
| Target mass | ≤ 85 g |

Roll diameter is verified two ways and agrees to 0.2 mm: by conservation of
area (280 mm × 0.35 mm pitch spiralled around a 2.2 mm core) and by measuring
the bounding box of the swept solid.

## 4. Materials and BOM

| # | Part | Material | Notes |
| --- | --- | --- | --- |
| 1 | Bag body | 70D nylon, 0.10 mm TPU lamination both faces, ~140 g/m² | RF-weldable, must be TPU not PVC for cold-crack and recyclability |
| 2 | Wallet shell | X-Pac VX21 or 210D recycled nylon with TPU face | Matte charcoal, abrasion resistant |
| 3 | Wallet stiffener | 0.8 mm HDPE sheet | Encapsulated, gives the roll its batten |
| 4 | Card slots | 0.2 mm clear/black TPU film | Welded, not stitched |
| 5 | Lip batten | 1.5 mm semi-rigid TPU rod in welded channel | Keeps the mouth flat so the roll seals evenly |
| 6 | Strap | 15 mm nylon webbing | Bar-tacked above the waterline only |
| 7 | Buckle | 15 mm acetal side-release, low-profile (Duraflex Stealth class) | Matte black, no logo |
| 8 | Seams | 10 mm RF-welded lap | No stitching below the fold line |

Colourway: charcoal-black wallet, deep ocean blue bag, matte black hardware.

## 5. Construction sequence

1. Weld card slots to the wallet inner panel.
2. Encapsulate the HDPE stiffener between wallet outer and inner panels; weld
   the perimeter on three sides.
3. Weld the bag panel's top edge into the wallet's open fourth edge — this is
   the single critical joint and it is a continuous lap weld, never a seam.
4. Weld bag side seams, 10 mm lap, bottom corners boxed and radiused.
5. Weld the batten channel at the bag mouth, insert TPU rod, cap both ends.
6. Bar-tack the clamp strap to the wallet back face at Z=30 mm, and the buckle
   tab to the front face at Z=58 mm. These are the only two stitch lines.
7. Attach buckle halves; heat-seal webbing ends.

## 6. Waterproofing strategy

The only stitch penetrations are the two bar-tacks that anchor the clamp strap
and the buckle tab. Both sit on the wallet at Z=30 mm and Z=58 mm, well above
the roll line, therefore above the waterline. Everything below is welded.

Target claim: **IPX7 — 1 m submersion, 30 minutes, with 4 rolls buckled.**
This is a target, not a verified rating. Validate before it goes on packaging.

Test plan:

- Static submersion, 1 m / 30 min, 3 and 4 rolls, tissue-paper witness inside.
- Roll-count sensitivity: find the minimum rolls that hold, publish rolls + 1.
- Weld peel strength on the wallet-to-bag joint, before and after cycling.
- 5,000-cycle roll/unroll fatigue at the fold line — this is the likely failure
  point, as repeated creasing at a fixed radius will eventually craze the TPU.
- Cold-crack at −20 °C.
- 72 h UV exposure, check for embrittlement and colour shift.

## 7. Open risks

- **Fold-line fatigue.** The bag always creases in roughly the same place.
  Consider a slightly softer, thinner laminate in a 20 mm band at the fold, or
  a deliberately varied roll start point.
- **Wallet-to-bag weld.** Dissimilar materials (X-Pac face vs TPU bag) may not
  weld reliably. Fallback is a common TPU carrier strip welded to both.
- **Stowed bulk.** 15.2 mm including the wrapped strap, 12.4 mm at the roll
  alone. Fine for a front pocket, tight for a back pocket. The roll diameter
  scales directly with panel length, so any extra depth costs bulk: the
  280 mm panel needed to fit a phone already added 1 mm over the first draft.
- **Cards when sealed.** They ride outside the dry volume. Acceptable if the
  welded slots hold, but worth prototyping a variant where the wallet inverts
  inward and rides inside the seal.
- **Bag depth when stowed.** The 35 mm loaded cross-section is what a phone
  plus keys needs, but the roll maths assumes the bag flattens to two plies.
  Confirm on a mock-up that a 35 mm bag rolls down to 12.4 mm cleanly.

## 8. Next steps

1. Paper/tape mock-up at full scale to confirm roll diameter and the 4-roll
   usable depth.
2. Source a TPU laminate swatch set; run weld trials for part 3 above.
3. Soft prototype, then run the section 6 test plan.
4. Resolve the cards-outside-the-seal question before tooling the buckle.

## 9. What the CAD model changed

Building `cad/` falsified four claims in v0.1. Each was caught by a test or by
measuring a solid, not by opinion.

| v0.1 claim | v0.2 | Why |
| --- | --- | --- |
| Wallet is the roll core | Wallet is the anchor plate | A 70 mm stiffened panel cannot roll into a 25 mm closure |
| Panel 105 × 230 mm | 100 × 280 mm | 230 mm left 126 mm usable — a 163 mm phone did not fit. 105 mm made the roll overhang the wallet |
| Loaded thickness 12 mm | 7.96 mm | Derived from the layer stack instead of guessed |
| Sealed volume 1.1 L | 0.59 L | Computed on the true rounded cross-section |

Unchanged and now confirmed by measurement: the 100 × 70 mm wallet, the 4.00 mm
empty stack, the ~82 mm stowed height, and the roll diameter agreeing with the
conservation-of-area calculation to within 0.2 mm.

---

## Renders

- `renders/hero-render.png` — stowed and deployed states
- `renders/construction-diagram.png` — side-profile cross-section and front elevation
- `renders/deployment-sequence.png` — four-step stow → unroll → load → seal

## CAD

See [`docs/cad.md`](cad.md). Build with `python -m cad.build`.
