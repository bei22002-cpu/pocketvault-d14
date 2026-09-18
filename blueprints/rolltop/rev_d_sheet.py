#!/usr/bin/env python3
"""D14 Rev D — drawing sheet D14-RT-004, clamp-bar closure.

Dimensions come from rev_d_dimensions.derive(); drawing primitives and the
house palette are shared with the Rev C sheet.

The sheet carries a bow diagram in place of Rev C's flat-pack view, because bow
is the calculation that sizes the closure and it is worth showing rather than
just tabulating.

Run: python blueprints/rolltop/rev_d_sheet.py
Writes: renders/D14-RT-004-revD.png and .svg
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mp
from matplotlib.figure import Figure

from rev_c_sheet import (
    ACC,
    ACC2,
    BAND_BOT,
    BG,
    DIM,
    GLASS,
    GRID,
    HEADER_Y,
    INK,
    INK2,
    INK3,
    LW_DIM,
    LW_MAIN,
    LW_OUTLINE,
    LW_THIN,
    MARGIN,
    SHEET_H,
    SHEET_W,
    TITLE_H,
    _arrow,
    centerline,
    dim_h,
    dim_v,
    leader,
    line,
    rect,
    rrect,
    txt,
    view_title,
)
from rev_c_dimensions import (
    BEZEL_FLANGE_REACH,
    BEZEL_FRAME_FACE,
    BEZEL_TO_BOTTOM,
    DEVICE,
    GLASS_RECESS,
    GLASS_SEAT_LAND,
    RATED_DEPTH_M,
    RATED_DURATION_MIN,
    REAR_CLEARANCE,
)
from rev_d_dimensions import (
    DRAWING_DATE,
    DRAWING_NO,
    GASKET_SECTION,
    LAND_END_CAP,
    LATCH_COUNT,
    LATCH_INSET,
    MOUTH_FOLD,
    PRODUCT_NAME,
    REVISION,
    SEAL_FACE_W,
    derive,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "renders"

MAIN_SCALE = 1.0 / 1.5
STACK_SCALE = 2.6
DETAIL_SCALE = 3.2
LAND_SHOWN = 8.0  # depth of land drawn in detail B before the break, mm
BOW_EXAG = 50.0  # vertical exaggeration on the bow diagram, x the drawing scale

COL_A = 14.0
COL_B = 188.0
COL_C = 298.0
COL_C_W = 108.0

FE_X, FE_Y = 68.0, 74.0


# --- front elevation ----------------------------------------------------


def front_elevation(ax, d):
    s = MAIN_SCALE
    W = d["loaded_overall_w"]
    Hc = d["cavity_depth"]
    H = d["sealed_h"]
    mouth = d["mouth_w"]
    land_h = d["land_h"]
    bar_t = d["bar_t"]
    fold = 2 * 0.5

    def X(v):
        return FE_X + v * s

    def Y(v):
        return FE_Y + v * s

    view_title(ax, COL_A + 4, 248.0, "FRONT ELEVATION", "SEALED AND LOADED  ·  SCALE 1:1.5")

    # Body.
    rrect(ax, X(0), Y(0), W * s, Hc * s, 5.0 * s, ec=INK, lw=LW_OUTLINE)
    line(ax, X(0), Y(Hc), X(W), Y(Hc), c=INK3, lw=LW_THIN, ls=(0, (3, 2)), z=4)

    # Closure: land, folded mouth, bar. The mouth clamps flat so it is wider
    # than the loaded body; the land end caps make it the widest point.
    m0 = (W - mouth) / 2.0
    cap0 = m0 - LAND_END_CAP
    cap_w = mouth + 2 * LAND_END_CAP
    rect(ax, X(cap0), Y(Hc), cap_w * s, land_h * s, ec=INK, lw=LW_MAIN, fc="#1a212b")
    line(ax, X(m0), Y(Hc + land_h), X(m0 + mouth), Y(Hc + land_h), c=INK2, lw=LW_THIN, z=5)
    rect(ax, X(m0), Y(Hc + land_h), mouth * s, fold * s, ec=INK2, lw=LW_DIM, fc="#1d232c")
    rrect(ax, X(m0), Y(Hc + land_h + fold), mouth * s, bar_t * s, 1.2 * s, ec=INK, lw=LW_OUTLINE, fc="#151a21")

    # Weld flange, bezel, glass, aperture.
    fw, fl = d["flange_w"], d["flange_l"]
    fx0, fy0 = (W - fw) / 2.0, BEZEL_TO_BOTTOM
    rect(ax, X(fx0), Y(fy0), fw * s, fl * s, ec=INK3, lw=LW_THIN, ls=(0, (4, 2)))

    bw, bl = d["bezel_w"], d["bezel_l"]
    bx0, by0 = (W - bw) / 2.0, fy0 + BEZEL_FLANGE_REACH
    rrect(ax, X(bx0), Y(by0), bw * s, bl * s, 3.0 * s, ec=INK, lw=LW_MAIN)

    gw, gl = d["glass_w"], d["glass_l"]
    gx0, gy0 = (W - gw) / 2.0, by0 + BEZEL_FRAME_FACE
    rect(ax, X(gx0), Y(gy0), gw * s, gl * s, ec=INK3, lw=LW_THIN, ls=(0, (2, 2)))

    aw, al = d["aperture_w"], d["aperture_l"]
    ax0, ay0 = (W - aw) / 2.0, gy0 + GLASS_SEAT_LAND
    rect(ax, X(ax0), Y(ay0), aw * s, al * s, ec=GLASS, lw=LW_MAIN, fc="#0d1a1f")
    txt(ax, X(W / 2), Y(ay0 + al * 0.52), "TEMPERED GLASS", size=5.0, c=GLASS, ha="center")
    txt(ax, X(W / 2), Y(ay0 + al * 0.52) - 3.6, f"{d['glass_t']:.1f} THICK", size=4.8, c=GLASS, ha="center")
    txt(ax, X(W / 2), Y(ay0 + al * 0.52) - 8.4, f"CLEAR {al:.0f} x {aw:.0f}", size=4.6, c=INK3, ha="center")

    # Latches with a load cell under each, and the LED, all in the land.
    latches = [m0 + LATCH_INSET + i * d["latch_span"] for i in range(LATCH_COUNT)]
    cell_y = Hc + land_h * 0.52
    for lx in latches:
        # over-centre latch straddling the bar
        rect(ax, X(lx - 5.0), Y(Hc + land_h * 0.35), 10.0 * s, (land_h * 0.65 + fold + bar_t) * s,
             ec=INK, lw=LW_THIN, fc="#1b222c", z=7)
        ax.add_patch(
            mp.Circle((X(lx), Y(cell_y)), 3.0 * s, edgecolor=DIM, facecolor="#0f2a2c", lw=LW_THIN, zorder=8)
        )
        ax.add_patch(
            mp.Circle((X(lx), Y(cell_y)), 1.0 * s, edgecolor=INK2, facecolor="none", lw=LW_DIM, zorder=9)
        )

    led_w, led_h = 26.0, 2.6
    led_x, led_y = (W - led_w) / 2.0, Hc + 1.6
    rrect(ax, X(led_x), Y(led_y), led_w * s, led_h * s, led_h * s / 2, ec=ACC, lw=LW_MAIN, fc="#123a24", z=7)

    # Tether anchor.
    ax.add_patch(mp.Circle((X(W - 10), Y(8)), 2.6 * s, edgecolor=INK2, facecolor="none", lw=LW_THIN, zorder=5))

    centerline(ax, X(W / 2), Y(-16), X(W / 2), Y(H + 10))

    say = Y(ay0 + al * 0.62)
    _arrow(ax, X(-14), say, 5.0, 0)
    _arrow(ax, X(W + 14), say, -5.0, 0)
    txt(ax, X(-16), say, "A", size=6.2, c=DIM, ha="right", weight="bold")
    txt(ax, X(W + 16), say, "A", size=6.2, c=DIM, ha="left", weight="bold")

    # Dimensions.
    dim_h(ax, X(0), X(W), Y(-14), f"{W:.0f} BODY", ext_from=Y(0))
    dim_h(ax, X(ax0), X(ax0 + aw), Y(-25), f"{aw:.0f} CLEAR", ext_from=Y(ay0))
    dim_h(ax, X(fx0), X(fx0 + fw), Y(-36), f"{fw:.0f} WELD FLANGE", ext_from=Y(fy0))
    dim_h(ax, X(cap0), X(cap0 + cap_w), Y(H) + 11.0, f"{cap_w:.0f} AT CLOSURE", ext_from=Y(Hc + land_h))

    dim_v(ax, Y(ay0), Y(ay0 + al), X(0) - 8.0, f"{al:.0f} CLEAR", ext_from=X(ax0))
    dim_v(ax, Y(0), Y(Hc), X(0) - 18.0, f"{Hc:.0f} CAVITY", ext_from=X(0))
    dim_v(ax, Y(0), Y(H), X(0) - 28.0, f"{H:.0f} SEALED", ext_from=X(0))

    # Callouts.
    kx, tx = X(W) + 6.0, X(W) + 8.0
    callouts = [
        (W / 2, Hc + land_h + fold + bar_t / 2, 238.0, f"CLAMP BAR {bar_t:.0f} x {d['bar_face_z']:.0f}", INK2),
        (latches[-1], Hc + land_h * 0.7, 231.0, f"OVER-CENTRE LATCH x{LATCH_COUNT}", INK2),
        (latches[-1], cell_y, 224.0, f"LOAD CELL x{LATCH_COUNT}, {d['clamp_force_per_latch']:.0f} N MIN", DIM),
        (cap0 + cap_w, Hc + land_h * 0.3, 217.0, f"GASKET LAND, {land_h:.0f} DEEP", INK2),
        (led_x + led_w, led_y + led_h / 2, 210.0, "SEAL-STATUS LED", ACC),
        (gx0 + gw, gy0 + gl * 0.74, 196.0, f"{GLASS_SEAT_LAND:.0f} BONDED GLASS SEAT", INK2),
        (fx0 + fw, fl * 0.45, 150.0, "RF WELD LAP, BEZEL TO BODY", INK2),
        (W - 2, Hc * 0.16, 112.0, "500D ARAMID / TPU BODY", INK2),
        (W - 10, 8, 84.0, "WRIST TETHER ANCHOR", ACC2),
    ]
    for px, py, ty, label, c in callouts:
        leader(ax, X(px), Y(py), kx, tx, ty, label, c=c)


# --- section A-A --------------------------------------------------------


def section_aa(ax, d):
    s = STACK_SCALE
    x, w = COL_B + 4.0, 32.0
    view_title(ax, COL_B, 250.0, "SECTION A-A", f"THICKNESS STACK  ·  SCALE {s:.1f}:1")

    layers = [
        ("PANE RECESS", GLASS_RECESS, "#171c24", INK3),
        ("TEMPERED GLASS", d["glass_t"], "#123138", GLASS),
        ("AIR GAP", d["air_gap"], "#0b0d11", INK3),
        ("DEVICE, MAX", DEVICE.t, "#1a212b", INK2),
        ("REAR CLEARANCE", REAR_CLEARANCE, "#0b0d11", INK3),
        ("REAR PLY, WELDED", 0.5, "#1d232c", INK2),
    ]
    top = 238.0
    y = top
    for name, t, fc, ec in layers:
        h = t * s
        y -= h
        rect(ax, x, y, w, h, ec=ec, lw=LW_THIN, fc=fc)
        line(ax, x + w, y + h / 2, x + w + 3.0, y + h / 2, c=INK3, lw=LW_DIM, z=4)
        txt(ax, x + w + 4.2, y + h / 2, f"{name}  {t:.1f}", size=4.6, c=ec)
    bottom = y

    dim_v(ax, bottom, top, x - 7.0, f"{d['sealed_t']:.1f} OVERALL", ext_from=x)
    txt(ax, COL_B, bottom - 4.5, f"CAVITY {d['cavity_t']:.1f}  ·  UNCHANGED FROM REV C", size=4.5, c=INK3)
    txt(ax, COL_B, bottom - 9.0, f"PANE DEFLECTS {d['glass_defl_proof']:.2f} AT PROOF", size=4.5, c=INK3)


# --- detail B: clamp bar section ---------------------------------------


def detail_clamp(ax, d):
    s = DETAIL_SCALE
    cx, cy = COL_B + 48.0, 128.0
    view_title(ax, COL_B, 176.0, "DETAIL B", f"CLAMP BAR, SECTION  ·  SCALE {s:.1f}:1")

    land_t = d["land_t"] * s
    land_h = LAND_SHOWN * s
    bar_t = d["bar_t"] * s
    bar_z = d["bar_face_z"] * s
    ply = 0.5 * s
    gask = GASKET_SECTION * s

    # Land, broken off below the sealing face: it runs on down to hold the
    # electronics and none of that matters to the seal.
    rect(ax, cx - land_t / 2, cy - land_h, land_t, land_h, ec=INK, lw=LW_MAIN, fc="#161c24")
    bx0, by = cx - land_t / 2, cy - land_h
    zig = [(bx0 + i * land_t / 6, by + (1.6 if i % 2 else -1.6)) for i in range(7)]
    ax.plot([p[0] for p in zig], [p[1] for p in zig], color=INK, linewidth=LW_THIN, zorder=6)
    leader(ax, bx0, cy - land_h * 0.55, cx - 22, cx - 24, cy - 14.0,
           f"LAND, {d['land_h']:.0f} DEEP, CELL INSIDE", ha="right", c=DIM)

    # Gasket bead on the land's sealing face.
    ax.add_patch(mp.Circle((cx, cy + gask / 2), gask / 2, edgecolor=ACC, facecolor="#12301f", lw=LW_THIN, zorder=7))
    leader(ax, cx + gask / 2, cy + gask / 2, cx + 18, cx + 20, cy - 5.0,
           f"{GASKET_SECTION:.1f} BEAD, {SEAL_FACE_W:.0f} FACE", c=ACC)

    # Folded mouth: two plies pinched over the bead.
    fold_y = cy + gask
    for i in range(2):
        rect(ax, cx - bar_z / 2 - 5, fold_y + i * ply, bar_z + 10, ply, ec=INK2, lw=LW_DIM, fc="#1d232c", z=6)
    leader(ax, cx - bar_z / 2 - 5, fold_y + ply, cx - 22, cx - 24, cy + 9.0, "MOUTH, FOLDED", ha="right")

    # Bar on top.
    bar_y = fold_y + 2 * ply
    rect(ax, cx - bar_z / 2, bar_y, bar_z, bar_t, ec=INK, lw=LW_OUTLINE, fc="#151a21", z=6)
    dim_v(ax, bar_y, bar_y + bar_t, cx + bar_z / 2 + 13.0, f"{d['bar_t']:.1f}")
    dim_h(ax, cx - bar_z / 2, cx + bar_z / 2, bar_y + bar_t + 7.0, f"{d['bar_face_z']:.0f}")

    for i in range(3):
        ax.plot([cx - bar_z / 4 + i * bar_z / 4] * 2, [bar_y + bar_t + 4.5, bar_y + bar_t + 0.6],
                color=DIM, lw=LW_DIM, zorder=5)
        _arrow(ax, cx - bar_z / 4 + i * bar_z / 4, bar_y + bar_t + 1.6, 0, -1.0)
    fx = cx + bar_z / 2 + 20.0
    txt(ax, fx, bar_y + bar_t * 0.7, f"{d['seal_line_load']:.2f} N/mm", size=4.6, c=DIM)
    txt(ax, fx, bar_y + bar_t * 0.7 - 4.4, f"{d['clamp_force_total']:.0f} N TOTAL", size=4.6, c=DIM)

    txt(ax, COL_B, 96.0, f"CLOSURE STANDS {d['closure_stack_h']:.0f} ABOVE THE SEAL LINE", size=4.4, c=INK3)
    txt(ax, COL_B, 91.5, f"MOUTH CONSUMES {MOUTH_FOLD:.0f} OF PANEL, WAS 78 ON THE ROLL", size=4.4, c=INK3)


# --- detail C: bow diagram ---------------------------------------------


def detail_bow(ax, d):
    view_title(ax, COL_B, 84.0, "DETAIL C", f"BAR BOW  ·  SPAN 1:1.5, BOW EXAGGERATED {BOW_EXAG:.0f}x")

    s = MAIN_SCALE
    vs = MAIN_SCALE * BOW_EXAG
    mouth = d["mouth_w"]
    span = d["latch_span"]
    bow = d["bar_bow_actual"]
    budget = d["bow_budget"]

    ox, oy = COL_B + 6.0, 52.0

    # Gasket datum.
    line(ax, ox, oy, ox + mouth * s, oy, c=ACC, lw=LW_MAIN)
    txt(ax, ox + mouth * s + 2.0, oy, "SEAL FACE", size=4.4, c=ACC)

    # Budget limit.
    line(ax, ox, oy + budget * vs, ox + mouth * s, oy + budget * vs, c=ACC2, lw=LW_DIM, ls=(0, (3, 2)))
    txt(ax, ox + mouth * s + 2.0, oy + budget * vs, f"{budget:.3f} LIMIT", size=4.4, c=ACC2)

    # Latch supports.
    latch_x = [LATCH_INSET + i * span for i in range(LATCH_COUNT)]
    for lx in latch_x:
        px = ox + lx * s
        ax.add_patch(
            mp.Polygon([[px, oy], [px - 2.2, oy - 4.0], [px + 2.2, oy - 4.0]], closed=True,
                       edgecolor=INK, facecolor="#1b222c", lw=LW_THIN, zorder=5)
        )

    # Deflected underside of the bar. Uniform load, simply supported:
    # y/ymax = (16/5)(s - 2s^3 + s^4).
    pts = []
    n = 24
    for i in range(len(latch_x) - 1):
        x0, x1 = latch_x[i], latch_x[i + 1]
        for j in range(n + 1):
            u = j / n
            shape = (16.0 / 5.0) * (u - 2 * u**3 + u**4)
            pts.append((ox + (x0 + u * (x1 - x0)) * s, oy + bow * shape * vs))
    # Overhangs stay effectively flat, which is the point.
    pts = [(ox, oy)] + pts + [(ox + mouth * s, oy)]
    ax.plot([p[0] for p in pts], [p[1] for p in pts], color=INK, linewidth=LW_MAIN, zorder=6)

    mid = ox + (latch_x[0] + span / 2) * s
    _arrow(ax, mid, oy + bow * vs + 7.0, 0, -5.0)
    txt(ax, mid, oy + bow * vs + 9.0, f"{bow:.3f}", size=4.6, c=DIM, ha="center")

    dim_h(ax, ox + latch_x[0] * s, ox + latch_x[1] * s, oy - 10.0, f"{span:.1f} SPAN")
    txt(ax, COL_B, 38.0,
        f"OVERHANG BOWS {d['bar_overhang_bow']:.5f}. SPAN ENTERS AS THE 4th POWER, SO "
        f"{LATCH_COUNT} INBOARD LATCHES BEAT 2 END LATCHES BY 14 mm OF BAR.",
        size=4.3, c=INK3)


# --- right column -------------------------------------------------------


def spec_table(ax, d, y_title):
    x, w = COL_C, COL_C_W
    view_title(ax, x, y_title, "SPECIFICATION")
    rows = [
        ("BODY", "500D ARAMID, TPU BOTH FACES, 0.50 PLY"),
        ("BEZEL", "PPA GF30 + TPU OVERMOULD WELD LIP"),
        ("WINDOW", f"{d['glass_l']:.0f} x {d['glass_w']:.0f} x {d['glass_t']:.1f} CHEM-STRENGTHENED"),
        ("CLEAR APERTURE", f"{d['aperture_l']:.0f} x {d['aperture_w']:.0f} — FULL DISPLAY"),
        ("CLOSURE", f"CLAMP BAR, {LATCH_COUNT} OVER-CENTRE LATCHES"),
        ("BAR", f"PPA GF30 {d['bar_t']:.1f} x {d['bar_face_z']:.0f} x {d['bar_l']:.0f}"),
        ("GASKET", f"{GASKET_SECTION:.1f} SILICONE BEAD, {SEAL_FACE_W:.0f} FACE"),
        ("SEALING", "RF-WELDED 10 LAP, NO STITCH BELOW FOLD"),
        ("RATING", f"{RATED_DEPTH_M:.0f} m / {RATED_DURATION_MIN:.0f} min, PROOF {d['proof_depth_m']:.0f} m"),
        ("PANE STRESS", f"{d['glass_stress_rated']:.0f} MPa RATED, {d['glass_stress_proof']:.0f} MPa PROOF"),
        ("CLAMP", f"{d['clamp_force_total']:.0f} N TOTAL, {d['clamp_force_per_latch']:.0f} N PER LATCH"),
        ("SENSING", f"{LATCH_COUNT}x LOAD CELL, ONE UNDER EACH LATCH"),
        ("SEAL INDICATOR", "GREEN = SEALED   RED = CHECK CLAMP"),
        ("DEVICE MAX", f"{DEVICE.l:.0f} x {DEVICE.w:.0f} x {DEVICE.t:.0f}"),
        ("SEALED", f"{d['overall_w_max']:.0f} x {d['sealed_h']:.0f} x {d['sealed_t']:.1f}"),
        ("MASS", f"{d['mass_total']:.0f} g EMPTY, {d['mass_total'] + DEVICE.mass_g:.0f} g LOADED"),
        ("BUOYANCY", f"{d['net_buoyancy']:+.0f} g — SINKS, TETHER REQUIRED"),
    ]
    rh, split = 4.6, 30.0
    top = y_title - 6.0
    bot = top - rh * len(rows)
    rect(ax, x, bot, w, rh * len(rows), ec=INK3, lw=LW_THIN)
    line(ax, x + split, bot, x + split, top, c=GRID, lw=0.4, z=2)
    for i, (k, v) in enumerate(rows):
        ry = top - rh * (i + 1)
        if i:
            line(ax, x, ry + rh, x + w, ry + rh, c=GRID, lw=0.35, z=2)
        txt(ax, x + 1.8, ry + rh / 2, k, size=4.3, c=INK3)
        txt(ax, x + split + 1.8, ry + rh / 2, v, size=4.3, c=ACC2 if "SINKS" in v else INK2)
    return bot


def notes_block(ax, d, y_title):
    x = COL_C
    view_title(ax, x, y_title, "NOTES")
    notes = [
        ("1. ALL DIMENSIONS IN MILLIMETRES. TOL +/-1.0 UNLESS NOTED.", INK2),
        ("2. THE ROLL-TOP IS SUPERSEDED. A BAR CLAMPING A GASKET LINE", DIM),
        ("   REPLACES A SPIRAL FRICTION SEAL. (CHANGED)", DIM),
        (f"3. BAR SECTION SET BY BOW, NOT STRENGTH: {d['bar_bow_actual']:.3f} MID-SPAN", INK2),
        (f"   AGAINST A {d['bow_budget']:.3f} BUDGET. STRESS ONLY {d['bar_stress']:.0f} MPa.", INK2),
        (f"4. LATCHES INSET {LATCH_INSET:.0f} FROM EACH END. THE OUTBOARD OVERHANG", INK2),
        (f"   BOWS {d['bar_overhang_bow']:.5f}, WHICH IS NEGLIGIBLE. (NEW)", INK2),
        ("5. ELECTRONICS MOVED FROM THE BEZEL INTO THE CLOSURE LAND,", INK2),
        ("   SHORTENING THE BEZEL BY 9.5. (CHANGED)", INK2),
        (f"6. WINDOW EXPOSES THE FULL {DEVICE.display_l:.0f} x {DEVICE.display_w:.0f} DISPLAY. VIEW-ONLY;", INK2),
        (f"   TOUCH WILL NOT WORK THROUGH {d['glass_t']:.1f} GLASS.", INK2),
        ("7. DEVICE SITS IN A WELDED TPU RETENTION SLEEVE.", INK2),
        ("8. CELLS UNDER LATCHES READ LATCH DELIVERY, NOT MID-SPAN", ACC2),
        ("   PRESSURE. BOW IS GUARANTEED BY DESIGN, NOT SENSED. (NEW)", ACC2),
        ("9. GRIT TOLERANCE IS WORSE THAN THE ROLL. THE SEALING FACE", ACC2),
        ("   MUST BE WIPEABLE AND EXPOSED, NOT A TRAPPED GROOVE. (NEW)", ACC2),
        (f"10. LOADED ASSEMBLY IS {abs(d['net_buoyancy']):.0f} g NEGATIVE. THE TETHER IS", ACC2),
        ("    RETENTION, NOT AN ACCESSORY.", ACC2),
        ("11. BEZEL WELD AND GLASS BOND REMAIN UNVALIDATED. THE CLOSURE", ACC2),
        ("    WAS ONE OF THREE SEAL PATHS, NOT ALL OF THEM. THE RATING", ACC2),
        ("    IS A TARGET; NOTHING HAS BEEN SUBMERGED.", ACC2),
    ]
    pitch = 3.75
    top = y_title - 7.0
    for i, (n, c) in enumerate(notes):
        txt(ax, x, top - i * pitch, n, size=4.3, c=c)
    return top - len(notes) * pitch


def revision_block(ax, d, y_title):
    x, w = COL_C, COL_C_W
    view_title(ax, x, y_title, f"REV {REVISION} — CHANGES FROM C")
    rows = [
        ("CLOSURE", "ROLL, 3 FOLDS", f"BAR + {LATCH_COUNT} LATCH"),
        ("CLAMP TOTAL", "287 N", f"{d['clamp_force_total']:.0f} N"),
        ("SENSORS", "4 CELLS", f"{LATCH_COUNT} CELLS"),
        ("OVERALL W", "111", f"{d['overall_w_max']:.0f}"),
        ("MASS", "225 g", f"{d['mass_total']:.0f} g"),
    ]
    rh = 4.7
    top = y_title - 6.0
    bot = top - rh * (len(rows) + 1)
    rect(ax, x, bot, w, rh * (len(rows) + 1), ec=INK3, lw=LW_THIN)
    hdr = top - rh
    for cxo, label in ((1.8, "ITEM"), (32.0, "REV C"), (68.0, f"REV {REVISION}")):
        txt(ax, x + cxo, hdr + rh / 2, label, size=4.3, c=INK3)
    line(ax, x, hdr, x + w, hdr, c=GRID, lw=0.5, z=2)
    for i, (k, a, b) in enumerate(rows):
        ry = hdr - rh * (i + 1)
        txt(ax, x + 1.8, ry + rh / 2, k, size=4.3, c=INK2)
        txt(ax, x + 32.0, ry + rh / 2, a, size=4.3, c=INK3)
        txt(ax, x + 68.0, ry + rh / 2, b, size=4.3, c=DIM)
    for cxo in (30.0, 66.0):
        line(ax, x + cxo, bot, x + cxo, top, c=GRID, lw=0.4, z=2)
    return bot


def title_block(ax, d):
    x0, y0 = MARGIN, MARGIN
    w = SHEET_W - 2 * MARGIN
    rect(ax, x0, y0, w, TITLE_H, ec=INK, lw=LW_MAIN)
    cols = [
        ("TITLE / DESIGNATION", f"D14 {PRODUCT_NAME} - DIVE-READY PHONE POUCH", 100.0, 7.2),
        ("DRAWING No.", DRAWING_NO, 40.0, 7.2),
        ("REV.", REVISION, 18.0, 7.2),
        ("SCALE", "1:1.5", 24.0, 5.8),
        ("UNITS", "mm", 20.0, 5.8),
        ("DATE", DRAWING_DATE, 40.0, 5.8),
        ("MASS", f"{d['mass_total']:.0f} g", 28.0, 5.8),
        ("RATING", f"{RATED_DEPTH_M:.0f} m / {RATED_DURATION_MIN:.0f} min", 46.0, 5.8),
        ("SHEET", "1 OF 1", 0.0, 5.8),
    ]
    cx = x0
    for i, (label, value, cw, vs) in enumerate(cols):
        if i:
            line(ax, cx, y0, cx, y0 + TITLE_H, c=INK, lw=LW_THIN)
        txt(ax, cx + 2.4, y0 + TITLE_H - 4.6, label, size=4.4, c=INK3)
        txt(ax, cx + 2.4, y0 + 7.0, value, size=vs, c=INK, weight="bold")
        cx += cw


def build() -> Figure:
    d = derive()
    fig = Figure(figsize=(SHEET_W / 25.4, SHEET_H / 25.4), dpi=200)
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, SHEET_W)
    ax.set_ylim(0, SHEET_H)
    ax.set_facecolor(BG)
    ax.set_axis_off()

    rect(ax, MARGIN, MARGIN, SHEET_W - 2 * MARGIN, SHEET_H - 2 * MARGIN, ec=INK, lw=LW_MAIN, z=2)

    txt(ax, MARGIN + 4, SHEET_H - MARGIN - 10, f"D14 {PRODUCT_NAME}", size=19, c=INK, weight="bold")
    txt(ax, MARGIN + 112, SHEET_H - MARGIN - 10, f"REV {REVISION}", size=12, c=DIM, weight="bold")
    txt(
        ax,
        MARGIN + 4,
        SHEET_H - MARGIN - 19,
        "SOFT ARAMID BODY  ·  RF-WELDED RIGID WINDOW BEZEL  ·  FULL-DISPLAY TEMPERED GLASS  ·  "
        "BAR-CLAMPED GASKET CLOSURE WITH PER-LATCH SENSING",
        size=5.4,
        c=INK2,
    )
    txt(
        ax,
        MARGIN + 4,
        SHEET_H - MARGIN - 25,
        "SUPERSEDES THE ROLL-TOP OF REV C PER closure-trade-study.md  ·  DIMENSIONS COMPUTED BY "
        "rev_d_dimensions.py  ·  NOTE: designs.js STILL NAMES THIS PART 'ROLLTOP'",
        size=4.6,
        c=ACC2,
        style="italic",
    )
    line(ax, MARGIN, HEADER_Y, SHEET_W - MARGIN, HEADER_Y, c=INK, lw=LW_THIN, z=2)

    for cx in (COL_B - 6.0, COL_C - 6.0):
        line(ax, cx, BAND_BOT - 8.0, cx, HEADER_Y, c=GRID, lw=0.5, z=2)

    front_elevation(ax, d)
    section_aa(ax, d)
    detail_clamp(ax, d)
    detail_bow(ax, d)

    y = spec_table(ax, d, 250.0)
    y = notes_block(ax, d, y - 6.0)
    revision_block(ax, d, y - 3.0)

    title_block(ax, d)
    return fig


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    fig = build()
    png = OUT / f"{DRAWING_NO}-rev{REVISION}.png"
    svg = OUT / f"{DRAWING_NO}-rev{REVISION}.svg"
    fig.savefig(png, facecolor=BG)
    fig.savefig(svg, facecolor=BG)
    print(f"wrote {png.name} and {svg.name}")


if __name__ == "__main__":
    main()
