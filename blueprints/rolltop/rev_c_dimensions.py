#!/usr/bin/env python3
"""D14 Rolltop Rev C — dimension derivation.

Single source of truth for every number on drawing D14-RT-003. Nothing here is
typed in as a finished dimension: each value is computed from the device datum,
the material stack, or a stress/pressure calculation, so the sheet and the spec
cannot drift apart.

Rev C differs from Rev B in two directed ways:
  - the window is sized to expose the whole display, not a porthole
  - the rating is 10 m for 30 min, proofed to 30 m

Run: python blueprints/rolltop/rev_c_dimensions.py
Writes: derived-dimensions-revC.md

Units: mm, N, MPa, g. Pressures converted to MPa for the plate formulas.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent

DRAWING_NO = "D14-RT-003"
REVISION = "C"
DRAWING_DATE = "18 SEP 2026"

# ---------------------------------------------------------------------------
# Physical constants
# ---------------------------------------------------------------------------

G = 9.81  # m/s^2
RHO_SEAWATER = 1025.0  # kg/m^3

# Densities, g/cm^3
RHO_GLASS = 2.48  # chemically strengthened aluminosilicate
RHO_PPA_GF30 = 1.55  # 30% glass-filled polyphthalamide
RHO_TPU = 1.20
RHO_ACETAL = 1.41

# Glass properties, MPa
E_GLASS = 71000.0
# Design allowable tensile stress at PROOF pressure. Chemically strengthened
# aluminosilicate has a modulus of rupture well above 600 MPa, but glass fails
# from edge and surface flaws, so the allowable is held to a fifth of that.
SIGMA_ALLOW_GLASS = 120.0

# Areal mass of the body laminate, g/m^2: 500D aramid plain weave plus 0.10 mm
# TPU each face.
FABRIC_AREAL = 420.0
FILM_AREAL = 240.0  # 0.20 mm clear TPU film, g/m^2

# ---------------------------------------------------------------------------
# Datum: target device class
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Device:
    """6.9 in flagship class, plus an allowance for a slim protective case."""

    bare_l: float = 163.0
    bare_w: float = 77.6
    bare_t: float = 8.3
    display_l: float = 152.0
    display_w: float = 70.0
    case_l: float = 2.0
    case_w: float = 2.4
    case_t: float = 2.7
    mass_g: float = 240.0

    @property
    def l(self) -> float:
        return self.bare_l + self.case_l

    @property
    def w(self) -> float:
        return self.bare_w + self.case_w

    @property
    def t(self) -> float:
        return self.bare_t + self.case_t


DEVICE = Device()

# ---------------------------------------------------------------------------
# Directed design inputs (the choices, as opposed to the consequences)
# ---------------------------------------------------------------------------

RATED_DEPTH_M = 10.0
PROOF_FACTOR = 3.0
RATED_DURATION_MIN = 30.0

# The phone is held in a welded TPU retention sleeve, so it registers to the
# aperture instead of floating. That is what lets the window be display-sized
# without a large tolerance ring.
PHONE_REGISTRATION_TOL = 2.0

GLASS_SEAT_LAND = 3.0  # bonded overlap of pane onto the bezel rebate, per side
GLASS_ADHESIVE = 0.3
GLASS_RECESS = 1.0  # pane sits below the bezel face so it is not the first thing to hit
BEZEL_FRAME_FACE = 4.5  # structure outboard of the glass rebate, per side
# The top of the bezel is not a frame face but an electronics rail: it has to
# swallow four 8 x 8 x 4 load cells, the PCB, the cell and the status LED, and
# 4.5 mm of frame cannot. The rail is the tallest component across it plus
# potting walls, and the whole body length follows from it, so the battery is
# specified flat (40 x 10 x 4, ~120 mAh) rather than square. A 25 x 20 x 4 cell
# of the same capacity would force a 22 mm rail and cost 8 mm of body length.
# Rails down the sides instead would be 171 mm long against this one's 89, so
# they cost more frame material per mm of width than they save in length.
BEZEL_TOP_RAIL = 14.0
BEZEL_BODY_T = 8.0
BEZEL_FLANGE_REACH = 8.0  # RF weld land projecting outboard of the bezel body
BEZEL_FLANGE_T = 1.2

FABRIC_PLY_T = 0.50  # 0.30 aramid base + 0.10 TPU each face
SIDE_LAP_WELD = 10.0
FABRIC_MARGIN_OUTBOARD = 7.0  # fabric beyond the weld flange, per side
BEZEL_TO_SEAL_LINE = 8.0  # flange top edge up to the roll/seal line
BEZEL_TO_BOTTOM = 8.0  # flange bottom edge down to the bottom fold

AIR_GAP = 1.5  # glass inner face to display
REAR_CLEARANCE = 1.5  # phone back to rear fabric inner face

ROLL_FOLDS = 3
ROLL_BAR_W = 4.0  # semi-rigid TPU batten at the mouth, also the roll core
ROLL_BAR_T = 3.0
MOUTH_HEM = 12.0  # folded and welded batten channel
ROLL_COMPRESSION = 0.70  # clamped bundle thickness as a fraction of free diameter

WEBBING_W = 15.0
BUCKLE_MASS_G = 5.5
LOAD_CELL_COUNT = 4
SEAL_PRESSURE_FACTOR = 3.0  # roll contact pressure as a multiple of internal pressure
ROLL_CONTACT_W = 8.0  # strap bearing width across the clamped roll

# ---------------------------------------------------------------------------
# Roark table 11.4 case 1a — rectangular plate, all edges simply supported,
# uniform pressure. sigma = beta*q*b^2/t^2 ; delta = alpha*q*b^4/(E*t^3)
# ---------------------------------------------------------------------------

_ROARK_AB = [1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 3.0, 1e9]
_ROARK_BETA = [0.2874, 0.3762, 0.4530, 0.5172, 0.5688, 0.6102, 0.7134, 0.7500]
_ROARK_ALPHA = [0.0444, 0.0616, 0.0770, 0.0906, 0.1017, 0.1110, 0.1335, 0.1421]


def _interp(x: float, xs: list[float], ys: list[float]) -> float:
    if x <= xs[0]:
        return ys[0]
    for i in range(len(xs) - 1):
        if xs[i] <= x <= xs[i + 1]:
            f = (x - xs[i]) / (xs[i + 1] - xs[i])
            return ys[i] + f * (ys[i + 1] - ys[i])
    return ys[-1]


def roark_coeffs(a_over_b: float) -> tuple[float, float]:
    return _interp(a_over_b, _ROARK_AB, _ROARK_BETA), _interp(a_over_b, _ROARK_AB, _ROARK_ALPHA)


def head_pressure_mpa(depth_m: float) -> float:
    """Gauge pressure of a seawater column, in MPa."""
    return RHO_SEAWATER * G * depth_m / 1e6


def plate_stress(q: float, b: float, t: float, beta: float) -> float:
    return beta * q * b * b / (t * t)


def plate_deflection(q: float, b: float, t: float, alpha: float) -> float:
    return alpha * q * b**4 / (E_GLASS * t**3)


def mass_g(volume_mm3: float, density_g_cm3: float) -> float:
    return volume_mm3 / 1000.0 * density_g_cm3


# ---------------------------------------------------------------------------
# Derivation
# ---------------------------------------------------------------------------


@dataclass
class Dims:
    values: dict = field(default_factory=dict)
    notes: dict = field(default_factory=dict)

    def set(self, key: str, value: float, note: str) -> float:
        self.values[key] = value
        self.notes[key] = note
        return value

    def __getitem__(self, key: str):
        return self.values[key]


def derive() -> Dims:
    d = Dims()

    # -- 1. Window clear aperture ------------------------------------------
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
    a_over_b = d.set("aperture_aspect", ap_l / ap_w, "long span / short span, drives the plate coefficients")

    # -- 2. Glass thickness from proof pressure -----------------------------
    proof_depth = d.set("proof_depth_m", RATED_DEPTH_M * PROOF_FACTOR, f"{PROOF_FACTOR:.0f} x rated depth")
    q_rated = d.set("p_rated_mpa", head_pressure_mpa(RATED_DEPTH_M), f"seawater head at {RATED_DEPTH_M:.0f} m")
    q_proof = d.set("p_proof_mpa", head_pressure_mpa(proof_depth), f"seawater head at {proof_depth:.0f} m")

    beta, alpha = roark_coeffs(a_over_b)
    d.set("roark_beta", beta, f"Roark 11.4 case 1a, interpolated at a/b = {a_over_b:.3f}")
    d.set("roark_alpha", alpha, f"Roark 11.4 case 1a, interpolated at a/b = {a_over_b:.3f}")

    t_min = d.set(
        "glass_t_min",
        (beta * q_proof * ap_w**2 / SIGMA_ALLOW_GLASS) ** 0.5,
        f"t = sqrt(beta*q*b^2/sigma_allow) at proof, sigma_allow = {SIGMA_ALLOW_GLASS:.0f} MPa",
    )
    glass_t = d.set("glass_t", 3.0, f"next standard pane above the {t_min:.2f} minimum")

    d.set(
        "glass_stress_proof",
        plate_stress(q_proof, ap_w, glass_t, beta),
        f"bending stress at {proof_depth:.0f} m proof",
    )
    d.set("glass_stress_rated", plate_stress(q_rated, ap_w, glass_t, beta), f"bending stress at {RATED_DEPTH_M:.0f} m")
    defl_proof = d.set(
        "glass_defl_proof", plate_deflection(q_proof, ap_w, glass_t, alpha), "centre deflection at proof"
    )
    d.set("glass_defl_rated", plate_deflection(q_rated, ap_w, glass_t, alpha), "centre deflection at rated depth")
    d.set(
        "air_gap",
        AIR_GAP,
        f"exceeds the {defl_proof:.2f} proof deflection, so the pane never touches the display",
    )

    # -- 3. Glass pane and bezel -------------------------------------------
    glass_w = d.set("glass_w", ap_w + 2 * GLASS_SEAT_LAND, f"aperture + 2 x {GLASS_SEAT_LAND} bonded seat land")
    glass_l = d.set("glass_l", ap_l + 2 * GLASS_SEAT_LAND, f"aperture + 2 x {GLASS_SEAT_LAND} bonded seat land")
    d.set("glass_rebate_depth", glass_t + GLASS_ADHESIVE, "pane thickness + adhesive bead")

    bezel_w = d.set("bezel_w", glass_w + 2 * BEZEL_FRAME_FACE, f"pane + 2 x {BEZEL_FRAME_FACE} frame face")
    bezel_l = d.set(
        "bezel_l",
        glass_l + BEZEL_FRAME_FACE + BEZEL_TOP_RAIL,
        f"pane + {BEZEL_FRAME_FACE} frame face below + {BEZEL_TOP_RAIL} electronics rail above",
    )
    d.set("bezel_top_rail", BEZEL_TOP_RAIL, "houses 4 load cells, PCB, battery and the status LED")
    d.set("bezel_t", BEZEL_BODY_T, "rigid frame body thickness")
    flange_w = d.set("flange_w", bezel_w + 2 * BEZEL_FLANGE_REACH, f"bezel + 2 x {BEZEL_FLANGE_REACH} weld flange")
    flange_l = d.set("flange_l", bezel_l + 2 * BEZEL_FLANGE_REACH, f"bezel + 2 x {BEZEL_FLANGE_REACH} weld flange")

    # -- 4. Body panel ------------------------------------------------------
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
    d.set(
        "cavity_headroom",
        cavity_depth - DEVICE.l,
        "spare depth over the device; the bezel flange sets the cavity, not the phone",
    )

    cavity_t = d.set(
        "cavity_t",
        AIR_GAP + DEVICE.t + REAR_CLEARANCE,
        f"air gap {AIR_GAP} + device {DEVICE.t} + rear clearance {REAR_CLEARANCE}",
    )
    # The rigid bezel is nearly as wide as the panel, so it governs the loaded
    # section rather than the fabric: the front face stays flat and only the
    # back bows. A free stadium section would over-state the internal width.
    internal_w = d.set(
        "loaded_internal_w",
        flange_w - 2 * 2.0,
        "fabric wraps just inboard of the weld flange edge; the bezel holds the front face flat",
    )
    d.set(
        "device_side_clearance",
        (internal_w - DEVICE.w) / 2.0,
        "clear either side of the device inside the cavity",
    )
    d.set("loaded_overall_w", flange_w + 2 * 3.0, "weld flange + fabric bulge either side")

    # -- 5. Roll ------------------------------------------------------------
    # The mouth is a flattened tube, so every turn of the roll wraps two plies.
    per_turn = 2 * (2 * FABRIC_PLY_T)
    dia = ROLL_BAR_W
    consumed = 0.0
    for _ in range(ROLL_FOLDS):
        consumed += 3.14159265 * (dia + per_turn / 2.0)
        dia += per_turn
    roll_dia = d.set(
        "roll_dia",
        dia,
        f"{ROLL_BAR_W} batten core + {ROLL_FOLDS} folds, each adding {per_turn:.1f} "
        f"(two plies of {FABRIC_PLY_T} top and bottom)",
    )
    roll_consumed = d.set(
        "roll_consumed",
        consumed + MOUTH_HEM,
        f"sum of {ROLL_FOLDS} turn circumferences ({consumed:.1f}) + {MOUTH_HEM} batten channel hem",
    )
    # Clamped, the bundle flattens at constant section area.
    area = 3.14159265 * (roll_dia / 2.0) ** 2
    roll_clamped_t = d.set(
        "roll_clamped_t",
        roll_dia * ROLL_COMPRESSION,
        f"free diameter compressed to {ROLL_COMPRESSION:.0%} under the clamp straps",
    )
    d.set("roll_clamped_depth", area / roll_clamped_t, "section area preserved as the bundle flattens")

    # -- 6. Panel and overall envelope --------------------------------------
    panel_len_face = d.set(
        "panel_len_face", cavity_depth + roll_consumed, "cavity depth + material the roll consumes"
    )
    d.set("panel_cut_l", 2 * panel_len_face, "single panel folded at the bottom, so no bottom seam")
    d.set("panel_cut_w", body_flat_w + 2 * SIDE_LAP_WELD, f"finished width + 2 x {SIDE_LAP_WELD} side lap weld")

    sealed_h = d.set(
        "sealed_h", cavity_depth + d["roll_clamped_depth"], "cavity depth + the clamped roll standing above it"
    )
    sealed_t = d.set(
        "sealed_t",
        GLASS_RECESS + glass_t + AIR_GAP + DEVICE.t + REAR_CLEARANCE + FABRIC_PLY_T,
        "section stack from the bezel face to the outside of the rear ply",
    )
    d.set("packed_t", BEZEL_BODY_T + 2 * FABRIC_PLY_T, "rigid bezel + collapsed body, empty")
    d.set("packed_t_at_roll", BEZEL_BODY_T + 2 * FABRIC_PLY_T + roll_clamped_t, "thickest point when stored rolled")

    # -- 7. Clamp force from seal mechanics ---------------------------------
    required_contact = d.set(
        "roll_contact_pressure",
        SEAL_PRESSURE_FACTOR * q_rated,
        f"{SEAL_PRESSURE_FACTOR:.0f} x internal pressure at {RATED_DEPTH_M:.0f} m",
    )
    patch = d.set("roll_contact_area", ROLL_CONTACT_W * body_flat_w, "strap bearing width x roll length")
    total_clamp = d.set("clamp_force_total", required_contact * patch, "contact pressure x contact patch")
    d.set(
        "clamp_force_per_cell",
        total_clamp / LOAD_CELL_COUNT,
        f"seal-verify threshold, {LOAD_CELL_COUNT} cells sharing the clamp",
    )
    d.set("clamp_force_per_cell_max", 200.0, "upper limit before the bezel top rail is over-stressed")

    # -- 8. Mass budget -----------------------------------------------------
    frame_ring = (bezel_w * bezel_l - ap_w * ap_l) * BEZEL_BODY_T
    rebate_ring = (glass_w * glass_l - ap_w * ap_l) * (glass_t + GLASS_ADHESIVE)
    rail_cavity = (bezel_w - 8.0) * (BEZEL_TOP_RAIL - 4.0) * (BEZEL_BODY_T - 2.5)
    flange_ring = (flange_w * flange_l - bezel_w * bezel_l) * BEZEL_FLANGE_T
    fabric_area_m2 = (d["panel_cut_w"] * d["panel_cut_l"]) / 1e6
    sleeve_area_m2 = 2 * (body_flat_w * (DEVICE.l + 15.0)) / 1e6

    budget = {
        "Tempered glass pane": mass_g(glass_w * glass_l * glass_t, RHO_GLASS),
        "Bezel frame, PPA GF30": mass_g(frame_ring - rebate_ring - rail_cavity, RHO_PPA_GF30),
        "Bezel weld flange, TPU": mass_g(flange_ring, RHO_TPU),
        "Body laminate": fabric_area_m2 * FABRIC_AREAL,
        "Retention sleeve, TPU film": sleeve_area_m2 * FILM_AREAL,
        "Mouth batten, TPU": mass_g(ROLL_BAR_W * ROLL_BAR_T * body_flat_w, RHO_TPU),
        "Clamp webbing x2": 4.0,
        "Side-release buckles x2": 2 * BUCKLE_MASS_G,
        "Load cells x4": 4.8,
        "MCU + BLE PCB": 4.5,
        "Battery, 120 mAh LiPo": 2.8,
        "Seal-status LED + potting": 2.5,
        "Flex + wiring": 2.0,
        "Adhesive and weld consumables": 3.0,
    }
    d.values["mass_budget"] = budget
    total_mass = d.set("mass_total", sum(budget.values()), "sum of the mass budget")

    # -- 9. Buoyancy --------------------------------------------------------
    # Displaced volume of the loaded pouch, section area derated for the
    # rounded edges rather than taken as a full bounding box.
    section_area = d["loaded_overall_w"] * sealed_t * 0.85
    disp = d.set(
        "displaced_volume",
        section_area * cavity_depth + d["loaded_overall_w"] * roll_clamped_t * d["roll_clamped_depth"],
        "loaded section swept over the cavity depth, plus the clamped roll bundle",
    )
    buoyancy = d.set("buoyant_mass", disp / 1000.0 * (RHO_SEAWATER / 1000.0), "seawater displaced, as mass")
    d.set(
        "net_buoyancy",
        buoyancy - (total_mass + DEVICE.mass_g),
        "positive floats; negative sinks and needs the tether or a float collar",
    )

    return d


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

SECTIONS = [
    (
        "Window and glazing",
        [
            ("aperture_w", "Window clear aperture, width", "mm"),
            ("aperture_l", "Window clear aperture, height", "mm"),
            ("aperture_aspect", "Aperture aspect a/b", ""),
            ("glass_t_min", "Glass minimum thickness required", "mm"),
            ("glass_t", "Glass thickness specified", "mm"),
            ("glass_w", "Pane width", "mm"),
            ("glass_l", "Pane height", "mm"),
            ("glass_rebate_depth", "Bezel rebate depth", "mm"),
            ("glass_stress_rated", "Pane bending stress at rated depth", "MPa"),
            ("glass_stress_proof", "Pane bending stress at proof depth", "MPa"),
            ("glass_defl_rated", "Pane centre deflection at rated depth", "mm"),
            ("glass_defl_proof", "Pane centre deflection at proof depth", "mm"),
            ("air_gap", "Air gap, pane to display", "mm"),
        ],
    ),
    (
        "Rigid bezel",
        [
            ("bezel_w", "Bezel body width", "mm"),
            ("bezel_l", "Bezel body height", "mm"),
            ("bezel_top_rail", "Electronics rail height", "mm"),
            ("bezel_t", "Bezel body thickness", "mm"),
            ("flange_w", "Weld flange width", "mm"),
            ("flange_l", "Weld flange height", "mm"),
        ],
    ),
    (
        "Soft body",
        [
            ("body_flat_w", "Finished flat width", "mm"),
            ("cavity_depth", "Cavity depth, seal line to bottom fold", "mm"),
            ("cavity_headroom", "Cavity depth spare over the device", "mm"),
            ("cavity_t", "Cavity thickness, loaded", "mm"),
            ("loaded_internal_w", "Internal clear width", "mm"),
            ("device_side_clearance", "Clearance either side of the device", "mm"),
            ("loaded_overall_w", "Overall width, loaded", "mm"),
            ("panel_len_face", "Panel length per face, flat", "mm"),
            ("panel_cut_w", "Cut panel width", "mm"),
            ("panel_cut_l", "Cut panel length", "mm"),
        ],
    ),
    (
        "Roll closure",
        [
            ("roll_dia", "Roll bundle diameter, free", "mm"),
            ("roll_consumed", "Panel length consumed by the roll", "mm"),
            ("roll_clamped_t", "Roll thickness, clamped", "mm"),
            ("roll_clamped_depth", "Roll depth, clamped", "mm"),
            ("roll_contact_pressure", "Required roll contact pressure", "MPa"),
            ("roll_contact_area", "Roll contact patch", "mm2"),
            ("clamp_force_total", "Total clamp force to verify seal", "N"),
            ("clamp_force_per_cell", "Clamp force per load cell, minimum", "N"),
            ("clamp_force_per_cell_max", "Clamp force per load cell, maximum", "N"),
        ],
    ),
    (
        "Envelope, mass and buoyancy",
        [
            ("sealed_h", "Overall height, sealed", "mm"),
            ("sealed_t", "Overall thickness, sealed and loaded", "mm"),
            ("packed_t", "Thickness, empty and flat", "mm"),
            ("packed_t_at_roll", "Thickness, empty, at the stored roll", "mm"),
            ("mass_total", "Mass, empty", "g"),
            ("displaced_volume", "Displaced volume, loaded", "mm3"),
            ("buoyant_mass", "Seawater displaced", "g"),
            ("net_buoyancy", "Net buoyancy with device", "g"),
        ],
    ),
]


def report(d: Dims) -> str:
    out: list[str] = []
    out.append(f"# D14 Rolltop — derived dimensions, Rev {REVISION}")
    out.append("")
    out.append(
        f"Generated by `rev_c_dimensions.py` for drawing {DRAWING_NO}. "
        "Do not edit by hand; change the inputs at the top of that script instead."
    )
    out.append("")
    out.append(
        "> **Superseded by Rev D.** The roll-top closure below was replaced by a clamped bar per "
        "`closure-trade-study.md`; see `derived-dimensions-revD.md` and drawing `D14-RT-004`. Rev C is "
        "kept as the record of how the roll was sized, and its window, glazing and section stack carry "
        "forward unchanged."
    )
    out.append("")
    out.append("## Datum")
    out.append("")
    out.append("| Quantity | Value | mm |")
    out.append("| --- | --- | --- |")
    out.append(f"| Device class | 6.9 in flagship, bare | {DEVICE.bare_l} x {DEVICE.bare_w} x {DEVICE.bare_t} |")
    out.append(f"| Device with slim case | accommodated | {DEVICE.l} x {DEVICE.w} x {DEVICE.t} |")
    out.append(f"| Display active area | exposed in full | {DEVICE.display_l} x {DEVICE.display_w} |")
    out.append(f"| Rated depth | {RATED_DEPTH_M:.0f} m for {RATED_DURATION_MIN:.0f} min | — |")
    out.append(f"| Proof depth | {d['proof_depth_m']:.0f} m | — |")
    out.append("")

    for title, rows in SECTIONS:
        out.append(f"## {title}")
        out.append("")
        out.append("| Dimension | Value | Derivation |")
        out.append("| --- | --- | --- |")
        for key, label, unit in rows:
            v = d[key]
            if unit in ("mm", "g", "N", "mm2"):
                val = f"{v:.1f} {unit}".strip()
            elif unit == "MPa":
                val = f"{v:.3f} MPa" if v < 1 else f"{v:.1f} MPa"
            elif unit == "mm3":
                val = f"{v:,.0f} mm3"
            else:
                val = f"{v:.3f}"
            out.append(f"| {label} | {val} | {d.notes[key]} |")
        out.append("")

    out.append("## Mass budget")
    out.append("")
    out.append("| Item | Mass |")
    out.append("| --- | --- |")
    for k, v in d["mass_budget"].items():
        out.append(f"| {k} | {v:.1f} g |")
    out.append(f"| **Total, empty** | **{d['mass_total']:.0f} g** |")
    out.append("")

    out.append("## Findings that change the design")
    out.append("")
    net = d["net_buoyancy"]
    out.append(
        f"- **The loaded pouch sinks.** It displaces {d['buoyant_mass']:.0f} g of seawater and weighs "
        f"{d['mass_total'] + DEVICE.mass_g:.0f} g with a device in it, so net buoyancy is "
        f"{net:+.0f} g. The wrist tether is not an accessory, it is the retention system. "
        "A float collar in the D16 pattern is the alternative."
    )
    out.append(
        f"- **The bezel sets the cavity, not the phone.** The weld flange is {d['flange_l']:.0f} mm tall, "
        f"which forces a {d['cavity_depth']:.0f} mm cavity for a {DEVICE.l:.0f} mm device — "
        f"{d['cavity_headroom']:.0f} mm of depth that carries no payload. This is the direct cost of a "
        "display-sized rigid window."
    )
    out.append(
        f"- **Glass dominates the mass budget** at {d['mass_budget']['Tempered glass pane']:.0f} g of "
        f"{d['mass_total']:.0f} g. Dropping the pane to {d['glass_t_min']:.1f} mm, the calculated minimum, "
        "would save about a fifth of the total, at the cost of impact margin on a boat deck."
    )
    out.append(
        f"- **Clamp threshold is derived, not chosen.** {d['clamp_force_per_cell']:.0f} N per cell comes from "
        f"holding {SEAL_PRESSURE_FACTOR:.0f}x internal pressure across the roll contact patch. It still has to "
        "survive a dunk test before it goes in firmware."
    )
    out.append("")
    out.append("## Reconciliation")
    out.append("")
    out.append("| Quantity | Rev B sheet | designs.js Rev A | Rev C | Why it moved |")
    out.append("| --- | --- | --- | --- | --- |")
    out.append(
        f"| Window clear | 100 x 80 | 148 x 70 aperture | {d['aperture_l']:.0f} x {d['aperture_w']:.0f} | "
        "sized to the full display plus registration tolerance |"
    )
    out.append(
        f"| Glass thickness | 3.0 | 1.5 | {d['glass_t']:.1f} | "
        f"3.0 confirmed by plate calculation; minimum was {d['glass_t_min']:.2f} |"
    )
    out.append(
        f"| Body outer | 130 x 150 | 175 x 95 x 40 | {d['loaded_overall_w']:.0f} x {d['sealed_h']:.0f} x "
        f"{d['sealed_t']:.1f} | derived from the bezel flange and the section stack |"
    )
    out.append(
        f"| Depth rating | 5 m / 30 min | 6 m | {RATED_DEPTH_M:.0f} m / {RATED_DURATION_MIN:.0f} min, "
        f"{d['proof_depth_m']:.0f} m proof | directed change |"
    )
    out.append(f"| Mass | 225 g est. | 122 g | {d['mass_total']:.0f} g | itemised budget, not an estimate |")
    out.append(
        f"| Clamp threshold | 100 N/corner | — | {d['clamp_force_per_cell']:.0f} N/corner | "
        "derived from roll contact mechanics |"
    )
    out.append("")
    out.append("## Still open")
    out.append("")
    out.append(
        "- The bezel is PPA GF30 and the body is TPU-faced aramid. Those do not RF-weld to each other, "
        "which is why the bezel carries an overmoulded TPU weld lip. Weld trials are unproven."
    )
    out.append(
        "- Every number above is geometry and hand calculation. Nothing has been submerged. The depth "
        "rating is a design target until the dunk and proof tests are run."
    )
    out.append("- Capacitive touch through a 3.0 mm glass pane with a 1.5 mm air gap does not work. Rev C is")
    out.append("  view-only through the window; all input has to come from elsewhere.")
    out.append("")
    return "\n".join(out)


def main() -> None:
    d = derive()
    (HERE / "derived-dimensions-revC.md").write_text(report(d), encoding="utf-8")
    (HERE / "derived-dimensions-revC.json").write_text(
        json.dumps({k: v for k, v in d.values.items()}, indent=2), encoding="utf-8"
    )
    # Console is not reliably UTF-8 on Windows, so the report goes to file and
    # only the headline numbers get printed.
    print(f"D14 Rev C ({DRAWING_NO})")
    print(f"  window clear      {d['aperture_l']:.0f} x {d['aperture_w']:.0f} mm, {d['glass_t']:.1f} mm glass")
    print(f"  sealed envelope   {d['loaded_overall_w']:.0f} x {d['sealed_h']:.0f} x {d['sealed_t']:.1f} mm")
    print(f"  flat packed       {d['loaded_overall_w']:.0f} x {d['sealed_h']:.0f} x {d['packed_t']:.1f} mm")
    print(f"  mass empty        {d['mass_total']:.0f} g")
    print(f"  clamp threshold   {d['clamp_force_per_cell']:.0f} N per cell, {d['clamp_force_total']:.0f} N total")
    print(f"  net buoyancy      {d['net_buoyancy']:+.0f} g with a {DEVICE.mass_g:.0f} g device")
    print("  wrote derived-dimensions-revC.md / .json")


if __name__ == "__main__":
    main()
