#!/usr/bin/env python3
"""D14 Rev D — dimension derivation for the clamp-bar closure.

Rev C is kept intact as the record. Rev D acts on `closure-trade-study.md`:
the three-fold roll is replaced by a rigid bar clamping the mouth against a
gasket land, because that turns a spiral friction seal into a straight gasket
line and puts the load cells in the load path instead of behind the most
compliant element in the stack.

Two knock-on decisions follow from the trade study rather than being new
choices here:

  - The latches move inboard of the mouth edges. Bow goes as span to the
    fourth power, so three inboard latches beat two end latches by far more
    than any material change, and the small outboard overhang bows a
    negligible amount.
  - The electronics move out of the bezel and into the closure land, which is
    now the part that needs to be rigid and instrumented. That lets the bezel
    top revert to a plain frame face and takes 9 mm out of the bezel height.

Physics helpers and material data are shared with Rev C.

Run: python blueprints/rolltop/rev_d_dimensions.py
Writes: derived-dimensions-revD.md / .json
"""

from __future__ import annotations

import json
from pathlib import Path

from rev_c_dimensions import (
    AIR_GAP,
    BEZEL_BODY_T,
    BEZEL_FLANGE_REACH,
    BEZEL_FLANGE_T,
    BEZEL_FRAME_FACE,
    BEZEL_TO_BOTTOM,
    BEZEL_TO_SEAL_LINE,
    DEVICE,
    FABRIC_AREAL,
    FABRIC_MARGIN_OUTBOARD,
    FABRIC_PLY_T,
    FILM_AREAL,
    GLASS_ADHESIVE,
    GLASS_RECESS,
    GLASS_SEAT_LAND,
    PHONE_REGISTRATION_TOL,
    PROOF_FACTOR,
    RATED_DEPTH_M,
    RATED_DURATION_MIN,
    REAR_CLEARANCE,
    RHO_GLASS,
    RHO_PPA_GF30,
    RHO_SEAWATER,
    RHO_TPU,
    SEAL_PRESSURE_FACTOR,
    SIDE_LAP_WELD,
    SIGMA_ALLOW_GLASS,
    Dims,
    head_pressure_mpa,
    mass_g,
    plate_deflection,
    plate_stress,
    roark_coeffs,
)

HERE = Path(__file__).resolve().parent

DRAWING_NO = "D14-RT-004"
REVISION = "D"
DRAWING_DATE = "18 SEP 2026"
PRODUCT_NAME = "CLAMP-BAR"

E_PPA_GF30 = 11000.0  # MPa, flexural modulus

# --- closure inputs -----------------------------------------------------

SEAL_FACE_W = 6.0  # gasket contact strip on the land, mm
GASKET_SECTION = 1.5  # silicone bead diameter, mm
GASKET_SQUEEZE = 0.30  # fraction compressed at full clamp
BOW_BUDGET = 0.25  # allowable mid-span bow as a fraction of the squeeze

LATCH_COUNT = 3
LATCH_INSET = 8.0  # first and last latch centre, in from the mouth end, mm
BAR_FACE_Z = 8.0  # bar dimension along the pouch height, mm
BAR_STANDARD_STEPS = [4.0, 4.5, 5.0, 5.5, 6.0, 7.0, 8.0, 9.0, 10.0]

LAND_H = 14.0  # closure land height: the flat cell plus potting walls
LAND_T = 6.0  # land thickness through the pouch
LAND_END_CAP = 2.0  # moulded cap at each end of the land
MOUTH_FOLD = 25.0  # panel consumed by one fold over the land plus a welded hem

LOAD_CELL_COUNT = LATCH_COUNT  # one cell under each latch


def _next_step(value: float) -> float:
    for s in BAR_STANDARD_STEPS:
        if s >= value:
            return s
    return BAR_STANDARD_STEPS[-1]


def beam_inertia_for_bow(w: float, span: float, bow: float, E: float) -> float:
    """Simply supported, uniform load: delta = 5 w L^4 / (384 E I)."""
    return 5.0 * w * span**4 / (384.0 * E * bow)


def cantilever_bow(w: float, overhang: float, E: float, inertia: float) -> float:
    return w * overhang**4 / (8.0 * E * inertia)


def rect_inertia(face_z: float, h: float) -> float:
    return face_z * h**3 / 12.0


def derive() -> Dims:
    d = Dims()

    # -- 1. Window, glass and bezel ----------------------------------------
    # Unchanged from Rev C except that the bezel top reverts to a frame face.
    ap_w = d.set(
        "aperture_w",
        DEVICE.display_w + 2 * PHONE_REGISTRATION_TOL,
        f"display {DEVICE.display_w} + 2 x {PHONE_REGISTRATION_TOL} registration tolerance",
    )
    ap_l = d.set(
        "aperture_l",
        DEVICE.display_l + 2 * PHONE_REGISTRATION_TOL,
        f"display {DEVICE.display_l} + 2 x {PHONE_REGISTRATION_TOL} registration tolerance",
    )
    a_over_b = d.set("aperture_aspect", ap_l / ap_w, "long span / short span")

    proof_depth = d.set("proof_depth_m", RATED_DEPTH_M * PROOF_FACTOR, f"{PROOF_FACTOR:.0f} x rated depth")
    q_rated = d.set("p_rated_mpa", head_pressure_mpa(RATED_DEPTH_M), f"seawater head at {RATED_DEPTH_M:.0f} m")
    q_proof = d.set("p_proof_mpa", head_pressure_mpa(proof_depth), f"seawater head at {proof_depth:.0f} m")

    beta, alpha = roark_coeffs(a_over_b)
    t_min = d.set(
        "glass_t_min",
        (beta * q_proof * ap_w**2 / SIGMA_ALLOW_GLASS) ** 0.5,
        f"t = sqrt(beta*q*b^2/sigma_allow) at proof, sigma_allow = {SIGMA_ALLOW_GLASS:.0f} MPa",
    )
    glass_t = d.set("glass_t", 3.0, f"next standard pane above the {t_min:.2f} minimum")
    d.set("glass_stress_rated", plate_stress(q_rated, ap_w, glass_t, beta), "pane bending stress at rated depth")
    d.set("glass_stress_proof", plate_stress(q_proof, ap_w, glass_t, beta), "pane bending stress at proof depth")
    d.set("glass_defl_rated", plate_deflection(q_rated, ap_w, glass_t, alpha), "centre deflection at rated depth")
    defl_proof = d.set(
        "glass_defl_proof", plate_deflection(q_proof, ap_w, glass_t, alpha), "centre deflection at proof"
    )
    d.set("air_gap", AIR_GAP, f"exceeds the {defl_proof:.2f} proof deflection")

    glass_w = d.set("glass_w", ap_w + 2 * GLASS_SEAT_LAND, f"aperture + 2 x {GLASS_SEAT_LAND} bonded seat land")
    glass_l = d.set("glass_l", ap_l + 2 * GLASS_SEAT_LAND, f"aperture + 2 x {GLASS_SEAT_LAND} bonded seat land")

    bezel_w = d.set("bezel_w", glass_w + 2 * BEZEL_FRAME_FACE, f"pane + 2 x {BEZEL_FRAME_FACE} frame face")
    bezel_l = d.set(
        "bezel_l",
        glass_l + 2 * BEZEL_FRAME_FACE,
        f"pane + 2 x {BEZEL_FRAME_FACE} frame face; no electronics rail, they moved to the closure",
    )
    d.set("bezel_t", BEZEL_BODY_T, "rigid frame body thickness")
    flange_w = d.set("flange_w", bezel_w + 2 * BEZEL_FLANGE_REACH, f"bezel + 2 x {BEZEL_FLANGE_REACH} weld flange")
    flange_l = d.set("flange_l", bezel_l + 2 * BEZEL_FLANGE_REACH, f"bezel + 2 x {BEZEL_FLANGE_REACH} weld flange")

    # -- 2. Body -----------------------------------------------------------
    body_flat_w = d.set(
        "body_flat_w",
        flange_w + 2 * FABRIC_MARGIN_OUTBOARD,
        f"weld flange + 2 x {FABRIC_MARGIN_OUTBOARD} fabric margin",
    )
    cavity_depth = d.set(
        "cavity_depth",
        flange_l + BEZEL_TO_SEAL_LINE + BEZEL_TO_BOTTOM,
        f"flange height + {BEZEL_TO_SEAL_LINE} to the seal line + {BEZEL_TO_BOTTOM} to the bottom fold",
    )
    d.set("cavity_headroom", cavity_depth - DEVICE.l, "spare depth over the device")
    d.set(
        "cavity_t",
        AIR_GAP + DEVICE.t + REAR_CLEARANCE,
        f"air gap {AIR_GAP} + device {DEVICE.t} + rear clearance {REAR_CLEARANCE}",
    )
    d.set("loaded_internal_w", flange_w - 2 * 2.0, "fabric wraps just inboard of the weld flange edge")
    body_w = d.set("loaded_overall_w", flange_w + 2 * 3.0, "weld flange + fabric bulge either side")

    # -- 3. Closure: seal load --------------------------------------------
    mouth_w = d.set("mouth_w", body_flat_w, "the mouth clamps flat, so it is the flat panel width")
    line_w = d.set(
        "seal_line_load",
        SEAL_PRESSURE_FACTOR * q_rated * SEAL_FACE_W,
        f"{SEAL_PRESSURE_FACTOR:.0f} x internal pressure over a {SEAL_FACE_W:.0f} mm gasket face",
    )
    clamp_total = d.set("clamp_force_total", line_w * mouth_w, "line load x mouth width")
    d.set(
        "clamp_force_per_latch",
        clamp_total / LATCH_COUNT,
        f"seal-verify threshold, {LATCH_COUNT} latches each over a load cell",
    )
    d.set("latch_count", float(LATCH_COUNT), "usability ceiling; a fourth latch is one more thing to forget")

    # -- 4. Closure: bar sized by bow --------------------------------------
    squeeze = d.set("gasket_squeeze", GASKET_SECTION * GASKET_SQUEEZE, f"{GASKET_SECTION} bead at {GASKET_SQUEEZE:.0%}")
    bow = d.set("bow_budget", squeeze * BOW_BUDGET, f"{BOW_BUDGET:.0%} of the squeeze")
    span = d.set(
        "latch_span",
        (mouth_w - 2 * LATCH_INSET) / (LATCH_COUNT - 1),
        f"latches inset {LATCH_INSET} from each end, {LATCH_COUNT - 1} equal spans",
    )
    inertia_req = d.set("bar_inertia_req", beam_inertia_for_bow(line_w, span, bow, E_PPA_GF30), "I = 5wL^4/(384 E delta)")
    h_min = d.set("bar_t_min", (12.0 * inertia_req / BAR_FACE_Z) ** (1.0 / 3.0), "I = face_z * h^3 / 12, solved for h")
    bar_t = d.set("bar_t", _next_step(h_min), f"next standard section above the {h_min:.2f} minimum")
    inertia = rect_inertia(BAR_FACE_Z, bar_t)
    d.set("bar_bow_actual", 5.0 * line_w * span**4 / (384.0 * E_PPA_GF30 * inertia), "bow at the specified section")
    d.set(
        "bar_overhang_bow",
        cantilever_bow(line_w, LATCH_INSET, E_PPA_GF30, inertia),
        f"cantilever bow at the {LATCH_INSET} mm outboard overhang",
    )
    d.set(
        "bar_stress",
        (line_w * span**2 / 8.0) / (BAR_FACE_Z * bar_t**2 / 6.0),
        "peak bending stress; deflection governs, not strength",
    )
    bar_len = d.set("bar_l", mouth_w, "bar spans the full clamped mouth")
    d.set("bar_face_z", BAR_FACE_Z, "bar dimension along the pouch height")

    # -- 5. Closure envelope ----------------------------------------------
    d.set("land_h", LAND_H, "closure land: houses 3 load cells, PCB, flat cell and the LED")
    d.set("land_t", LAND_T, "land thickness through the pouch")
    closure_stack = d.set(
        "closure_stack_h",
        LAND_H + 2 * FABRIC_PLY_T + bar_t,
        f"land {LAND_H} + folded mouth {2 * FABRIC_PLY_T:.1f} + bar {bar_t}",
    )
    d.set("closure_t", LAND_T + 2 * FABRIC_PLY_T + bar_t, "land + fold + bar, through the pouch at the closure")

    sealed_h = d.set("sealed_h", cavity_depth + closure_stack, "cavity depth + the closure standing above it")
    d.set("overall_w_max", mouth_w + 2 * LAND_END_CAP, "widest point is the clamped mouth, not the body")
    sealed_t = d.set(
        "sealed_t",
        GLASS_RECESS + glass_t + AIR_GAP + DEVICE.t + REAR_CLEARANCE + FABRIC_PLY_T,
        "section stack from the bezel face to the outside of the rear ply",
    )
    d.set("packed_t", BEZEL_BODY_T + 2 * FABRIC_PLY_T, "rigid bezel + collapsed body, empty")
    d.set("packed_t_at_closure", LAND_T + 2 * FABRIC_PLY_T + bar_t, "closure does not collapse")

    panel_face = d.set("panel_len_face", cavity_depth + MOUTH_FOLD, f"cavity depth + {MOUTH_FOLD} mouth fold")
    d.set("panel_cut_l", 2 * panel_face, "single panel folded at the bottom")
    d.set("panel_cut_w", body_flat_w + 2 * SIDE_LAP_WELD, f"finished width + 2 x {SIDE_LAP_WELD} side lap weld")

    # -- 6. Mass -----------------------------------------------------------
    frame_ring = (bezel_w * bezel_l - ap_w * ap_l) * BEZEL_BODY_T
    rebate_ring = (glass_w * glass_l - ap_w * ap_l) * (glass_t + GLASS_ADHESIVE)
    flange_ring = (flange_w * flange_l - bezel_w * bezel_l) * BEZEL_FLANGE_T
    land_solid = bar_len * LAND_H * LAND_T
    land_cavity = (bar_len - 8.0) * (LAND_H - 4.0) * (LAND_T - 2.5)
    fabric_area_m2 = (d["panel_cut_w"] * d["panel_cut_l"]) / 1e6
    sleeve_area_m2 = 2 * (body_flat_w * (DEVICE.l + 15.0)) / 1e6

    budget = {
        "Tempered glass pane": mass_g(glass_w * glass_l * glass_t, RHO_GLASS),
        "Bezel frame, PPA GF30": mass_g(frame_ring - rebate_ring, RHO_PPA_GF30),
        "Bezel weld flange, TPU": mass_g(flange_ring, RHO_TPU),
        "Body laminate": fabric_area_m2 * FABRIC_AREAL,
        "Retention sleeve, TPU film": sleeve_area_m2 * FILM_AREAL,
        "Clamp bar, PPA GF30": mass_g(bar_len * BAR_FACE_Z * bar_t, RHO_PPA_GF30),
        "Closure land, PPA GF30": mass_g(land_solid - land_cavity, RHO_PPA_GF30),
        "Land end caps x2": mass_g(2 * LAND_END_CAP * LAND_H * LAND_T, RHO_PPA_GF30),
        "Gasket, silicone bead": mass_g(3.1416 * (GASKET_SECTION / 2) ** 2 * bar_len, 1.15),
        f"Over-centre latches x{LATCH_COUNT}": LATCH_COUNT * 3.0,
        f"Load cells x{LOAD_CELL_COUNT}": LOAD_CELL_COUNT * 1.2,
        "MCU + BLE PCB": 4.5,
        "Battery, 120 mAh LiPo": 2.8,
        "Seal-status LED + potting": 2.5,
        "Flex + wiring": 2.0,
        "Adhesive and weld consumables": 3.0,
    }
    d.values["mass_budget"] = budget
    total_mass = d.set("mass_total", sum(budget.values()), "sum of the mass budget")

    # -- 7. Buoyancy -------------------------------------------------------
    body_section = body_w * sealed_t * 0.85
    closure_block = d["overall_w_max"] * LAND_H * d["closure_t"]
    disp = d.set(
        "displaced_volume",
        body_section * cavity_depth + closure_block,
        "body section swept over the cavity depth, plus the closure block",
    )
    buoy = d.set("buoyant_mass", disp / 1000.0 * (RHO_SEAWATER / 1000.0), "seawater displaced, as mass")
    d.set("net_buoyancy", buoy - (total_mass + DEVICE.mass_g), "positive floats; negative sinks")

    return d


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

SECTIONS = [
    (
        "Window and glazing (carried from Rev C)",
        [
            ("aperture_w", "Window clear aperture, width", "mm"),
            ("aperture_l", "Window clear aperture, height", "mm"),
            ("glass_t", "Glass thickness", "mm"),
            ("glass_stress_proof", "Pane bending stress at proof", "MPa"),
            ("glass_defl_proof", "Pane centre deflection at proof", "mm"),
            ("air_gap", "Air gap, pane to display", "mm"),
        ],
    ),
    (
        "Rigid bezel",
        [
            ("bezel_w", "Bezel body width", "mm"),
            ("bezel_l", "Bezel body height", "mm"),
            ("bezel_t", "Bezel body thickness", "mm"),
            ("flange_w", "Weld flange width", "mm"),
            ("flange_l", "Weld flange height", "mm"),
        ],
    ),
    (
        "Clamp-bar closure",
        [
            ("mouth_w", "Clamped mouth width", "mm"),
            ("seal_line_load", "Required seal line load", "N/mm"),
            ("clamp_force_total", "Total clamp force", "N"),
            ("clamp_force_per_latch", "Clamp force per latch and cell", "N"),
            ("latch_count", "Latches", ""),
            ("latch_span", "Span between latches", "mm"),
            ("gasket_squeeze", "Gasket squeeze at full clamp", "mm"),
            ("bow_budget", "Allowable mid-span bow", "mm"),
            ("bar_inertia_req", "Bar second moment required", "mm4"),
            ("bar_t_min", "Bar thickness minimum", "mm"),
            ("bar_t", "Bar thickness specified", "mm"),
            ("bar_bow_actual", "Mid-span bow at specified section", "mm"),
            ("bar_overhang_bow", "Bow at the outboard overhang", "mm"),
            ("bar_stress", "Bar peak bending stress", "MPa"),
            ("bar_l", "Bar length", "mm"),
            ("land_h", "Closure land height", "mm"),
            ("land_t", "Closure land thickness", "mm"),
            ("closure_stack_h", "Closure height above the seal line", "mm"),
        ],
    ),
    (
        "Body and envelope",
        [
            ("body_flat_w", "Finished flat width", "mm"),
            ("cavity_depth", "Cavity depth", "mm"),
            ("cavity_headroom", "Cavity depth spare over the device", "mm"),
            ("cavity_t", "Cavity thickness, loaded", "mm"),
            ("loaded_overall_w", "Body width, loaded", "mm"),
            ("overall_w_max", "Overall width at the closure", "mm"),
            ("sealed_h", "Overall height, sealed", "mm"),
            ("sealed_t", "Overall thickness, sealed and loaded", "mm"),
            ("packed_t", "Thickness, empty and flat", "mm"),
            ("packed_t_at_closure", "Thickness at the closure", "mm"),
            ("panel_len_face", "Panel length per face, flat", "mm"),
            ("panel_cut_w", "Cut panel width", "mm"),
            ("panel_cut_l", "Cut panel length", "mm"),
            ("mass_total", "Mass, empty", "g"),
            ("buoyant_mass", "Seawater displaced", "g"),
            ("net_buoyancy", "Net buoyancy with device", "g"),
        ],
    ),
]


def _fmt(v: float, unit: str) -> str:
    if unit == "mm4":
        return f"{v:.0f} mm4"
    if unit == "mm":
        # Bow and squeeze values live well below 1 mm and are the whole point.
        if abs(v) < 0.01:
            return f"{v:.5f} mm"
        return f"{v:.3f} mm" if abs(v) < 1.0 else f"{v:.1f} mm"
    if unit in ("g", "N"):
        return f"{v:.1f} {unit}"
    if unit == "N/mm":
        return f"{v:.2f} N/mm"
    if unit == "MPa":
        return f"{v:.3f} MPa" if v < 1 else f"{v:.1f} MPa"
    if unit == "":
        return f"{v:.0f}"
    return f"{v:.2f}"


def report(d: Dims, c) -> str:
    out: list[str] = []
    out.append(f"# D14 {PRODUCT_NAME} — derived dimensions, Rev {REVISION}")
    out.append("")
    out.append(
        f"Generated by `rev_d_dimensions.py` for drawing {DRAWING_NO}. Rev D replaces the three-fold "
        "roll with a bar clamping the mouth against a gasket land, per `closure-trade-study.md`. "
        "Rev C is retained unchanged as the record."
    )
    out.append("")
    out.append(
        "**The name no longer describes the product.** `designs.js` still calls D14 *Rolltop*, and "
        "there is no roll in Rev D. That designation needs a decision before this reaches the catalogue."
    )
    out.append("")

    for title, rows in SECTIONS:
        out.append(f"## {title}")
        out.append("")
        out.append("| Dimension | Value | Derivation |")
        out.append("| --- | --- | --- |")
        for key, label, unit in rows:
            out.append(f"| {label} | {_fmt(d[key], unit)} | {d.notes[key]} |")
        out.append("")

    out.append("## Mass budget")
    out.append("")
    out.append("| Item | Mass |")
    out.append("| --- | --- |")
    for k, v in d["mass_budget"].items():
        out.append(f"| {k} | {v:.1f} g |")
    out.append(f"| **Total, empty** | **{d['mass_total']:.0f} g** |")
    out.append("")

    out.append("## Rev C to Rev D")
    out.append("")
    out.append("| Quantity | Rev C, roll-top | Rev D, clamp bar | Note |")
    out.append("| --- | --- | --- | --- |")
    out.append(
        f"| Clamp force | {c['clamp_force_total']:.0f} N total | {d['clamp_force_total']:.0f} N total | "
        f"{(1 - d['clamp_force_total'] / c['clamp_force_total']) * 100:.0f}% less for the user to generate |"
    )
    out.append(
        f"| Per sensor | {c['clamp_force_per_cell']:.0f} N over 4 | "
        f"{d['clamp_force_per_latch']:.0f} N over {LATCH_COUNT} | near-identical threshold, one fewer cell |"
    )
    out.append(
        f"| Bezel height | {c['bezel_l']:.1f} mm | {d['bezel_l']:.1f} mm | "
        "electronics left the bezel, so the top rail became a frame face |"
    )
    out.append(
        f"| Cavity depth | {c['cavity_depth']:.1f} mm | {d['cavity_depth']:.1f} mm | follows the shorter bezel |"
    )
    out.append(
        f"| Mouth material | {c['roll_consumed']:.0f} mm | {MOUTH_FOLD:.0f} mm | one fold instead of three |"
    )
    out.append(
        f"| Sealed height | {c['sealed_h']:.1f} mm | {d['sealed_h']:.1f} mm | "
        f"{d['sealed_h'] - c['sealed_h']:+.1f} mm |"
    )
    out.append(
        f"| Overall width | {c['loaded_overall_w']:.0f} mm | {d['overall_w_max']:.0f} mm | "
        "the clamped mouth is now the widest point |"
    )
    out.append(f"| Mass, empty | {c['mass_total']:.0f} g | {d['mass_total']:.0f} g | {d['mass_total'] - c['mass_total']:+.0f} g |")
    out.append(
        f"| Net buoyancy | {c['net_buoyancy']:+.0f} g | {d['net_buoyancy']:+.0f} g | still sinks; tether required |"
    )
    out.append("")

    out.append("## What the calculation actually decided")
    out.append("")
    out.append(
        f"- **Span, not material.** Bow goes as span to the fourth power. Moving the latches inboard "
        f"cut the span to {d['latch_span']:.1f} mm and the bar to {d['bar_t']:.1f} mm; the two-end-latch "
        f"arrangement in the trade study needed 20 mm in the same plastic. No material change comes close "
        "to that."
    )
    out.append(
        f"- **The overhang is free.** The {LATCH_INSET:.0f} mm outboard of the end latches bows "
        f"{d['bar_overhang_bow']:.5f} mm, which is nothing, because cantilever deflection also goes as "
        "the fourth power and the overhang is short. That is what makes inboard latches viable at all."
    )
    out.append(
        f"- **The bar is stiffness-limited by a wide margin.** Peak stress is {d['bar_stress']:.1f} MPa "
        "against a flexural strength in the hundreds. Nothing here is close to breaking; it is only "
        "about staying flat."
    )
    out.append(
        f"- **Relocating the electronics paid for the closure.** Taking the load cells and PCB out of "
        f"the bezel shortened it by {c['bezel_l'] - d['bezel_l']:.1f} mm, which very nearly offsets the "
        f"{d['closure_stack_h']:.0f} mm the closure adds. The product ends up "
        f"{abs(d['sealed_h'] - c['sealed_h']):.1f} mm "
        f"{'taller' if d['sealed_h'] > c['sealed_h'] else 'shorter'} than Rev C, which is nothing. A better "
        "closure came out mass- and size-neutral, exactly as the trade study predicted."
    )
    out.append("")

    out.append("## Still open")
    out.append("")
    out.append(
        f"- **Load cells under latches cannot see mid-span bow.** Each cell reports what its own latch "
        f"delivered. The {d['bow_budget']:.3f} mm bow budget is therefore a design guarantee, not a "
        "sensed quantity, and a cracked or over-compliant bar would read as fully sealed."
    )
    out.append(
        "- **Grit is a regression.** A roll closes over sand; a gasket does not. The land needs a "
        "wipeable, exposed sealing face rather than a groove that traps debris."
    )
    out.append(
        "- **The bezel weld and the glass bond are unchanged and still the longest unvalidated seal "
        "paths on the product.** Rev D fixes the closure only. The pouch is not waterproof until all "
        "three joints are tested."
    )
    out.append(
        "- Nothing has been submerged. The depth rating remains a design target pending proof and "
        "dunk testing."
    )
    out.append("")
    return "\n".join(out)


def main() -> None:
    import rev_c_dimensions

    d = derive()
    c = rev_c_dimensions.derive()
    (HERE / "derived-dimensions-revD.md").write_text(report(d, c), encoding="utf-8")
    (HERE / "derived-dimensions-revD.json").write_text(
        json.dumps({k: v for k, v in d.values.items()}, indent=2), encoding="utf-8"
    )
    print(f"D14 Rev {REVISION} ({DRAWING_NO})")
    print(f"  closure        bar {d['bar_t']:.1f} mm over {LATCH_COUNT} latches, span {d['latch_span']:.1f} mm")
    print(f"  clamp          {d['clamp_force_total']:.0f} N total, {d['clamp_force_per_latch']:.0f} N per latch")
    print(f"  bow            {d['bar_bow_actual']:.3f} mm mid-span against a {d['bow_budget']:.3f} budget")
    print(f"  envelope       {d['overall_w_max']:.0f} x {d['sealed_h']:.0f} x {d['sealed_t']:.1f} mm")
    print(f"  mass empty     {d['mass_total']:.0f} g  (Rev C {c['mass_total']:.0f} g)")
    print(f"  net buoyancy   {d['net_buoyancy']:+.0f} g")
    print("  wrote derived-dimensions-revD.md / .json")


if __name__ == "__main__":
    main()
