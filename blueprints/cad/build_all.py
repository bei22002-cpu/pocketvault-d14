#!/usr/bin/env python3
"""
Nereid Program — build all 18 interface designs as CAD solids.

Exports per design into blueprints/models/<ID>/:
  - shell_front.stl / .step
  - shell_back.stl / .step
  - window_blank.stl / .step  (where applicable)
  - extras (puck, foam collar, cartridge, gauntlet strap mounts, etc.)
  - MANIFEST.json

Units: millimeters. Prototype geometry for FDM/SLA or CNC soft tooling —
production materials (Mg, Ti, CFRP, spinel) still require the BOM process notes.
"""

from __future__ import annotations

import json
import math
from pathlib import Path

import cadquery as cq
from cadquery import exporters

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "models"
TOL = 0.2  # print clearance

# Assumed phone class (mm)
PHONE = {"L": 147.0, "W": 71.0, "H": 8.0}

DESIGNS = [
    dict(id="A1", name="Lightline-Mg", kind="force", L=168, W=88, H=26, apL=148, apW=70, wall=1.8, depth_m=6),
    dict(id="A2", name="Carbonshell", kind="force_cf", L=168, W=88, H=25, apL=148, apW=70, wall=1.2, depth_m=6),
    dict(id="A3", name="Skeleton", kind="skeleton", L=170, W=90, H=28, apL=148, apW=70, wall=2.0, depth_m=10),
    dict(id="A4", name="Titan-20", kind="force_heavy", L=172, W=92, H=32, apL=146, apW=68, wall=2.0, depth_m=20),
    dict(id="B5", name="Hall-Glove", kind="fixed_window", L=168, W=88, H=25, apL=148, apW=70, wall=1.2, depth_m=6),
    dict(id="B6", name="Stylus-EMR", kind="stylus", L=168, W=92, H=28, apL=148, apW=70, wall=1.8, depth_m=6),
    dict(id="B7", name="Lamb-Wave", kind="fixed_window", L=168, W=88, H=25, apL=148, apW=70, wall=1.2, depth_m=6),
    dict(id="B8", name="Resistive-Hard", kind="fixed_window", L=168, W=88, H=26, apL=148, apW=70, wall=1.8, depth_m=6),
    dict(id="B9", name="Gap-Cap", kind="force", L=168, W=88, H=26, apL=148, apW=70, wall=1.8, depth_m=6),
    dict(id="C10", name="Crownpad", kind="controls", L=165, W=86, H=24, apL=140, apW=65, wall=1.5, depth_m=10),
    dict(id="C11", name="Tether-Puck", kind="puck", L=160, W=84, H=22, apL=138, apW=64, wall=1.5, depth_m=20),
    dict(id="C12", name="Tilt-Cursor", kind="controls_thin", L=162, W=84, H=18, apL=136, apW=62, wall=1.0, depth_m=6),
    dict(id="C13", name="Voice-PTT", kind="controls", L=164, W=85, H=22, apL=138, apW=64, wall=1.5, depth_m=20),
    dict(id="D14", name="Rolltop", kind="rolltop", L=175, W=95, H=40, apL=148, apW=70, wall=2.0, depth_m=6),
    dict(id="D15", name="Oilfill-100", kind="oilfill", L=170, W=90, H=35, apL=50, apW=30, wall=1.0, depth_m=100),
    dict(id="D16", name="Floatline", kind="float", L=190, W=110, H=45, apL=148, apW=70, wall=1.8, depth_m=6),
    dict(id="D17", name="Chestboard", kind="chest", L=200, W=120, H=28, apL=155, apW=85, wall=1.8, depth_m=10),
    dict(id="D18", name="Gauntlet", kind="gauntlet", L=95, W=70, H=28, apL=38, apW=38, wall=1.5, depth_m=20),
]


def export_pair(solid: cq.Workplane | cq.Shape, dest: Path, name: str) -> dict:
    dest.mkdir(parents=True, exist_ok=True)
    stl = dest / f"{name}.stl"
    step = dest / f"{name}.step"
    shape = solid.val() if hasattr(solid, "val") else solid
    exporters.export(shape, str(stl))
    exporters.export(shape, str(step))
    try:
        vol = float(shape.Volume())
    except Exception:
        vol = 0.0
    return {"stl": stl.name, "step": step.name, "volume_mm3": round(vol, 1)}


def fillet_safe(wp: cq.Workplane, r: float) -> cq.Workplane:
    try:
        return wp.edges("|Z").fillet(r)
    except Exception:
        return wp


def shell_front(L: float, W: float, H: float, wall: float, apL: float, apW: float, lip: float = 2.0) -> cq.Workplane:
    """Front half with window aperture and phone pocket."""
    front_h = H * 0.55
    outer = cq.Workplane("XY").box(L, W, front_h)
    # Inner cavity (phone + air pocket)
    cav_L, cav_W = PHONE["L"] + 2, PHONE["W"] + 2
    cav_H = front_h - wall
    cavity = cq.Workplane("XY").box(cav_L, cav_W, cav_H).translate((0, 0, wall / 2))
    body = outer.cut(cavity)
    # Window aperture through front face
    aperture = (
        cq.Workplane("XY")
        .box(apL, apW, wall + 2)
        .translate((0, 0, -front_h / 2 + wall / 2))
    )
    body = body.cut(aperture)
    # Window recess / glass seat (1 mm larger, 1.2 mm deep)
    seat = (
        cq.Workplane("XY")
        .box(apL + 2, apW + 2, 1.2)
        .translate((0, 0, -front_h / 2 + wall + 0.4))
    )
    body = body.cut(seat)
    # O-ring groove on mating face (inner perimeter)
    try:
        groove = (
            cq.Workplane("XY")
            .rect(L - 2 * wall - 1, W - 2 * wall - 1)
            .rect(L - 2 * wall - 3.5, W - 2 * wall - 3.5)
            .extrude(1.0)
            .translate((0, 0, front_h / 2 - 0.5))
        )
        body = body.cut(groove)
    except Exception:
        pass
    return fillet_safe(body, min(2.0, wall))


def shell_back(L: float, W: float, H: float, wall: float) -> cq.Workplane:
    back_h = H * 0.45
    outer = cq.Workplane("XY").box(L, W, back_h)
    cav_L, cav_W = PHONE["L"] + 2, PHONE["W"] + 2
    cav_H = back_h - wall
    cavity = cq.Workplane("XY").box(cav_L, cav_W, cav_H).translate((0, 0, -wall / 2))
    body = outer.cut(cavity)
    # Latch bosses (4)
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        boss = (
            cq.Workplane("XY")
            .cylinder(3.5, 4)
            .translate((sx * (L / 2 - 8), sy * (W / 2 - 8), back_h / 2 - 1))
        )
        body = body.union(boss)
    # Purge valve boss
    valve = cq.Workplane("XY").cylinder(4, 5).translate((0, W / 2 - 6, 0))
    body = body.union(valve)
    hole = cq.Workplane("XY").cylinder(4.2, 2.2).translate((0, W / 2 - 6, 0))
    body = body.cut(hole)
    return fillet_safe(body, min(2.0, wall))


def window_blank(apL: float, apW: float, t: float = 1.5) -> cq.Workplane:
    return cq.Workplane("XY").box(apL, apW, t)


def load_cell_pockets(front: cq.Workplane, apL: float, apW: float, front_h: float) -> cq.Workplane:
    """Cut 8×8×4 mm pockets at aperture corners for FX29-class cells."""
    body = front
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        pocket = (
            cq.Workplane("XY")
            .box(8, 8, 4)
            .translate((sx * (apL / 2 - 6), sy * (apW / 2 - 6), -front_h * 0.55 / 2 + 4))
        )
        body = body.cut(pocket)
    return body


def rf_window_slot(front: cq.Workplane, L: float, W: float, front_h: float) -> cq.Workplane:
    """PPS RF window pocket on long edge (A2)."""
    slot = (
        cq.Workplane("XY")
        .box(40, 3, front_h * 0.4)
        .translate((0, -W / 2 + 2, 0))
    )
    return front.cut(slot)


def skeleton_ribs(L: float, W: float, H: float) -> cq.Workplane:
    """Open lattice rib cage approximating A3."""
    frame = cq.Workplane("XY").box(L, W, H)
    hollow = cq.Workplane("XY").box(L - 8, W - 8, H + 2)
    frame = frame.cut(hollow)
    # Cross ribs
    rib_x = cq.Workplane("XY").box(L - 4, 4, H - 2)
    rib_y = cq.Workplane("XY").box(4, W - 4, H - 2)
    ribs = rib_x.union(rib_y)
    # Corner posts
    for sx, sy in ((1, 1), (1, -1), (-1, 1), (-1, -1)):
        post = cq.Workplane("XY").box(10, 10, H).translate((sx * (L / 2 - 8), sy * (W / 2 - 8), 0))
        ribs = ribs.union(post)
    return fillet_safe(frame.union(ribs), 1.0)


def window_cartridge(apL: float, apW: float) -> cq.Workplane:
    """A3 field-replaceable cartridge carrier."""
    plate = cq.Workplane("XY").box(apL + 12, apW + 12, 6)
    cut = cq.Workplane("XY").box(apL, apW, 8)
    plate = plate.cut(cut)
    # Captive screw ears
    for sx in (-1, 1):
        ear = cq.Workplane("XY").box(10, 8, 6).translate((sx * (apL / 2 + 8), 0, 0))
        plate = plate.union(ear)
        hole = cq.Workplane("XY").cylinder(7, 1.6).translate((sx * (apL / 2 + 8), 0, 0))
        plate = plate.cut(hole)
    return plate


def control_panel(L: float, W: float, H: float, wall: float, apL: float, apW: float, n_keys: int = 4) -> tuple:
    front = shell_front(L, W, H, wall, apL, apW)
    # Side control bay
    bay = cq.Workplane("XY").box(14, 50, H * 0.4).translate((L / 2 - 5, 0, 0))
    front = front.union(bay)
    # Key holes
    span = 36
    for i in range(n_keys):
        y = -span / 2 + i * (span / max(n_keys - 1, 1))
        hole = cq.Workplane("XY").cylinder(6, 3.2).translate((L / 2 - 5, y, H * 0.1))
        front = front.cut(hole)
    # Encoder hole
    enc = cq.Workplane("XY").cylinder(6, 4).translate((L / 2 - 5, span / 2 + 10, H * 0.1))
    front = front.cut(enc)
    back = shell_back(L, W, H, wall)
    return front, back


def stylus_channel(front: cq.Workplane, L: float, W: float, H: float) -> cq.Workplane:
    channel = (
        cq.Workplane("XY")
        .box(8, W - 20, 8)
        .translate((L / 2 - 2, 0, 0))
    )
    return front.union(channel).cut(
        cq.Workplane("XY").cylinder(W - 24, 3.2).rotate((0, 0, 0), (1, 0, 0), 90).translate((L / 2 - 2, 0, 0))
    )


def tether_puck() -> cq.Workplane:
    body = cq.Workplane("XY").ellipse(28, 36).extrude(18)
    # Thumbstick well
    well = cq.Workplane("XY").cylinder(10, 8).translate((0, 6, 9))
    body = body.cut(well)
    # Buttons
    for x in (-10, 10):
        btn = cq.Workplane("XY").cylinder(4, 3).translate((x, -12, 9))
        body = body.cut(btn)
    # Cable exit
    cable = cq.Workplane("XY").cylinder(8, 2.5).rotate((0, 0, 0), (0, 1, 0), 90).translate((-28, 0, 0))
    body = body.cut(cable)
    return body


def rolltop_bezel(apL: float, apW: float) -> cq.Workplane:
    bezel = cq.Workplane("XY").box(apL + 20, apW + 20, 10)
    cut = cq.Workplane("XY").box(apL, apW, 12)
    bezel = bezel.cut(cut)
    # Fabric clamp flange
    flange = cq.Workplane("XY").box(apL + 28, apW + 28, 2).translate((0, 0, -6))
    bezel = bezel.union(flange)
    return load_cell_pockets(bezel, apL, apW, 10)


def oilfill_housing(L: float, W: float, H: float, wall: float, apL: float, apW: float) -> tuple:
    outer = cq.Workplane("XY").box(L, W, H)
    inner = cq.Workplane("XY").box(L - 2 * wall, W - 2 * wall, H - 2 * wall)
    shell = outer.cut(inner)
    # Small OLED window
    win = cq.Workplane("XY").box(apL, apW, wall + 2).translate((0, W / 4, H / 2 - wall / 2))
    shell = shell.cut(win)
    # Diaphragm port (circular)
    port = cq.Workplane("XY").cylinder(wall + 2, 12).translate((0, -W / 4, H / 2 - wall / 2))
    shell = shell.cut(port)
    # Split into front/back by cutting mid-plane isn't needed — export as single + lid
    lid = cq.Workplane("XY").box(L, W, wall).translate((0, 0, H / 2 + wall / 2))
    return shell, lid


def foam_collar(L: float, W: float, H: float) -> cq.Workplane:
    """Syntactic foam collar around A1 envelope (D16)."""
    outer = cq.Workplane("XY").box(L, W, H)
    # Inner void for A1 core ~168×88×26
    inner = cq.Workplane("XY").box(170, 90, 28)
    collar = outer.cut(inner)
    # Buoyancy scallops (reduce print material, keep volume)
    for i in range(6):
        ang = i * 60
        x = 70 * math.cos(math.radians(ang))
        y = 40 * math.sin(math.radians(ang))
        scoops = cq.Workplane("XY").sphere(12).translate((x, y, 0))
        try:
            collar = collar.cut(scoops)
        except Exception:
            pass
    return collar


def chestboard(L: float, W: float, H: float, wall: float, apL: float, apW: float) -> tuple:
    front, back = control_panel(L, W, H, wall, apL, apW, n_keys=6)
    # MOLLE plate on back
    plate = cq.Workplane("XY").box(L - 20, W - 20, 3).translate((0, 0, -H * 0.45 / 2 - 1.5))
    # Vertical webbing slots
    for x in (-40, 0, 40):
        for y in (-25, 0, 25):
            slot = cq.Workplane("XY").box(4, 12, 5).translate((x, y, -H * 0.45 / 2 - 1.5))
            plate = plate.cut(slot)
    back = back.union(plate)
    return front, back


def gauntlet(L: float, W: float, H: float, wall: float, apL: float, apW: float) -> tuple:
    front = shell_front(L, W, H, wall, apL, apW)
    back = shell_back(L, W, H, wall)
    # Crown on side
    crown_boss = cq.Workplane("XY").cylinder(6, 8).rotate((0, 0, 0), (0, 1, 0), 90).translate((L / 2, 0, 0))
    front = front.union(crown_boss)
    crown_hole = cq.Workplane("XY").cylinder(7, 3).rotate((0, 0, 0), (0, 1, 0), 90).translate((L / 2, 0, 0))
    front = front.cut(crown_hole)
    # Compass repeater well on bezel
    compass = cq.Workplane("XY").cylinder(3, 8).translate((0, W / 2 - 10, H * 0.55 / 2 - 1))
    front = front.cut(compass)
    # Strap lugs
    for sy in (-1, 1):
        lug = cq.Workplane("XY").box(12, 6, 8).translate((0, sy * (W / 2 + 2), 0))
        hole = cq.Workplane("XY").cylinder(8, 2).rotate((0, 0, 0), (1, 0, 0), 90).translate((0, sy * (W / 2 + 2), 0))
        back = back.union(lug).cut(hole)
    return front, back


def build_design(d: dict) -> dict:
    dest = OUT / d["id"]
    if dest.exists():
        for p in dest.iterdir():
            if p.is_file():
                p.unlink()
    dest.mkdir(parents=True, exist_ok=True)

    L, W, H, wall = d["L"], d["W"], d["H"], d["wall"]
    apL, apW = d["apL"], d["apW"]
    kind = d["kind"]
    parts: dict[str, dict] = {}
    notes: list[str] = []

    if kind in ("force", "force_cf", "force_heavy", "fixed_window", "stylus"):
        front = shell_front(L, W, H, wall, apL, apW)
        if kind in ("force", "force_cf", "force_heavy"):
            front = load_cell_pockets(front, apL, apW, H)
            notes.append("Four corner load-cell pockets for FX29-class sensors")
        if kind == "force_cf":
            front = rf_window_slot(front, L, W, H * 0.55)
            notes.append("RF window slot on long edge — backfill with RF-transparent filament for prototype")
        if kind == "stylus":
            front = stylus_channel(front, L, W, H)
            notes.append("Side stylus stow channel — print with dissolvable support")
        back = shell_back(L, W, H, wall)
        win_t = 2.2 if kind == "force_heavy" else 1.5
        parts["shell_front"] = export_pair(front, dest, "shell_front")
        parts["shell_back"] = export_pair(back, dest, "shell_back")
        parts["window_blank"] = export_pair(window_blank(apL, apW, win_t), dest, "window_blank")

    elif kind == "skeleton":
        ribs = skeleton_ribs(L, W, H)
        cart = window_cartridge(apL, apW)
        back = shell_back(L, W, H, wall)
        parts["rib_cage"] = export_pair(ribs, dest, "rib_cage")
        parts["window_cartridge"] = export_pair(cart, dest, "window_cartridge")
        parts["shell_back"] = export_pair(back, dest, "shell_back")
        parts["window_blank"] = export_pair(window_blank(apL, apW, 1.5), dest, "window_blank")
        notes.append("Field-swap cartridge: two M3 clearance ears")

    elif kind in ("controls", "controls_thin"):
        n = 4 if kind == "controls" else 1
        front, back = control_panel(L, W, H, wall, apL, apW, n_keys=n)
        parts["shell_front"] = export_pair(front, dest, "shell_front")
        parts["shell_back"] = export_pair(back, dest, "shell_back")
        parts["window_blank"] = export_pair(window_blank(apL, apW, 1.0), dest, "window_blank")
        notes.append("Control bay on +X edge; silicone boots not modeled — buy COTS")

    elif kind == "puck":
        front = shell_front(L, W, H, wall, apL, apW)
        back = shell_back(L, W, H, wall)
        # Bulkhead boss
        bh = cq.Workplane("XY").cylinder(6, 8).rotate((0, 0, 0), (0, 1, 0), 90).translate((L / 2, 0, 0))
        front = front.union(bh)
        puck = tether_puck()
        parts["shell_front"] = export_pair(front, dest, "shell_front")
        parts["shell_back"] = export_pair(back, dest, "shell_back")
        parts["tether_puck"] = export_pair(puck, dest, "tether_puck")
        parts["window_blank"] = export_pair(window_blank(apL, apW, 1.0), dest, "window_blank")
        notes.append("Bulkhead connector is COTS marine — do not print the seal gland")

    elif kind == "rolltop":
        bezel = rolltop_bezel(apL, apW)
        parts["rigid_bezel"] = export_pair(bezel, dest, "rigid_bezel")
        parts["window_blank"] = export_pair(window_blank(apL, apW, 1.5), dest, "window_blank")
        # Fabric pattern as flat DXF-like plate for cutting
        pattern = cq.Workplane("XY").box(220, 160, 0.4)
        parts["fabric_cut_pattern"] = export_pair(pattern, dest, "fabric_cut_pattern")
        notes.append("Print bezel only; sew/RF-weld aramid/TPU body to flange per BOM")

    elif kind == "oilfill":
        shell, lid = oilfill_housing(L, W, H, wall, apL, apW)
        parts["oil_shell"] = export_pair(shell, dest, "oil_shell")
        parts["oil_lid"] = export_pair(lid, dest, "oil_lid")
        notes.append("Prototype only — 100 m requires PE-rated oil-comp housing, not FDM alone")

    elif kind == "float":
        # A1 core parts + collar
        front = load_cell_pockets(shell_front(168, 88, 26, 1.8, 148, 70), 148, 70, 26)
        back = shell_back(168, 88, 26, 1.8)
        collar = foam_collar(L, W, H)
        parts["shell_front"] = export_pair(front, dest, "shell_front")
        parts["shell_back"] = export_pair(back, dest, "shell_back")
        parts["foam_collar"] = export_pair(collar, dest, "foam_collar")
        parts["window_blank"] = export_pair(window_blank(148, 70, 1.5), dest, "window_blank")
        notes.append("Print collar in lightweight filament or cast syntactic foam into printed mold")

    elif kind == "chest":
        front, back = chestboard(L, W, H, wall, apL, apW)
        parts["shell_front"] = export_pair(front, dest, "shell_front")
        parts["shell_back"] = export_pair(back, dest, "shell_back")
        parts["window_blank"] = export_pair(window_blank(apL, apW, 1.2), dest, "window_blank")
        notes.append("MOLLE slots on back plate — verify strap width before print")

    elif kind == "gauntlet":
        front, back = gauntlet(L, W, H, wall, apL, apW)
        parts["shell_front"] = export_pair(front, dest, "shell_front")
        parts["shell_back"] = export_pair(back, dest, "shell_back")
        parts["window_blank"] = export_pair(window_blank(apL, apW, 1.0), dest, "window_blank")
        notes.append("Compass repeater is COTS liquid-filled — seat in bezel well")

    else:
        raise ValueError(f"Unknown kind {kind}")

    manifest = {
        "id": d["id"],
        "name": d["name"],
        "kind": kind,
        "units": "mm",
        "outer_mm": {"L": L, "W": W, "H": H},
        "aperture_mm": {"L": apL, "W": apW},
        "wall_mm": wall,
        "depth_rating_m_design": d["depth_m"],
        "phone_cavity_mm": PHONE,
        "parts": parts,
        "print_notes": [
            "Material for waterproof prototype: PETG or ASA, 100% infill walls, 4+ perimeters",
            "Coat seam with marine epoxy or silicone after fit-check; O-rings are COTS",
            "Window blank is dimensional stand-in — use real glass/PC/spinel from BOM",
            *notes,
        ],
        "disclaimer": "Digital prototype geometry. Not certified for immersion. Pressure-test before any water use.",
    }
    (dest / "MANIFEST.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    return manifest


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    results = []
    errors = []
    for d in DESIGNS:
        print(f"Building {d['id']} {d['name']} ...", flush=True)
        try:
            m = build_design(d)
            nparts = len(m["parts"])
            print(f"  OK - {nparts} parts -> {OUT / d['id']}")
            results.append(m)
        except Exception as e:
            print(f"  FAIL - {e}")
            errors.append({"id": d["id"], "error": str(e)})

    index = {
        "program": "Nereid Interface Catalog",
        "rev": "A",
        "designs_built": len(results),
        "designs_failed": errors,
        "models": [{k: r[k] for k in ("id", "name", "parts", "outer_mm")} for r in results],
    }
    (OUT / "INDEX.json").write_text(json.dumps(index, indent=2), encoding="utf-8")
    print(f"\nDone: {len(results)}/{len(DESIGNS)} designs -> {OUT}")
    if errors:
        print("Failures:", errors)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
