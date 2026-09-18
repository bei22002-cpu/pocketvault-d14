#!/usr/bin/env python3
"""D14 Rolltop Rev C — drawing sheet D14-RT-003.

Every dimension on the sheet is pulled from rev_c_dimensions.derive(), so the
drawing cannot disagree with the spec. A3 landscape, dark house style.

Run: python blueprints/rolltop/rev_c_sheet.py
Writes: renders/D14-RT-003-revC.png and .svg
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.patches as mp
from matplotlib.figure import Figure

from rev_c_dimensions import (
    BEZEL_FLANGE_REACH,
    BEZEL_FRAME_FACE,
    BEZEL_TO_BOTTOM,
    BEZEL_TOP_RAIL,
    DEVICE,
    DRAWING_DATE,
    DRAWING_NO,
    GLASS_RECESS,
    GLASS_SEAT_LAND,
    RATED_DEPTH_M,
    RATED_DURATION_MIN,
    REVISION,
    derive,
)

HERE = Path(__file__).resolve().parent
OUT = HERE / "renders"

# --- sheet geometry, mm --------------------------------------------------
SHEET_W, SHEET_H = 420.0, 297.0
MARGIN = 10.0
HEADER_Y = 259.0  # rule under the header block
BAND_TOP = 256.0
BAND_BOT = 34.0
TITLE_H = 22.0

MAIN_SCALE = 1.0 / 1.5  # front elevation and flat-pack side view
STACK_SCALE = 2.6  # section A-A
DETAIL_SCALE = 3.4  # detail B
PACK_SCALE = 1.0 / 3.0

# Column origins.
COL_A = 14.0
COL_B = 188.0
COL_C = 298.0
COL_C_W = 108.0

# Front elevation placement: sheet position of the body bottom-left corner.
FE_X, FE_Y = 68.0, 76.0

WEB_W = 15.0

# --- palette ------------------------------------------------------------
BG = "#08090b"
INK = "#e9edf1"
INK2 = "#8d9aa8"
INK3 = "#5a6672"
GRID = "#1b2129"
DIM = "#63d3c4"
ACC = "#35d07f"
ACC2 = "#ff6b5e"
GLASS = "#3d8f9c"

MONO = "DejaVu Sans Mono"

LW_OUTLINE = 1.5
LW_MAIN = 0.9
LW_THIN = 0.55
LW_DIM = 0.45


# --- primitives ---------------------------------------------------------


def rect(ax, x, y, w, h, ec=INK, lw=LW_MAIN, fc="none", ls="-", z=3):
    ax.add_patch(mp.Rectangle((x, y), w, h, edgecolor=ec, facecolor=fc, linewidth=lw, linestyle=ls, zorder=z))


def rrect(ax, x, y, w, h, r, ec=INK, lw=LW_MAIN, fc="none", ls="-", z=3):
    r = min(r, w / 2.0, h / 2.0)
    ax.add_patch(
        mp.FancyBboxPatch(
            (x + r, y + r),
            max(w - 2 * r, 1e-6),
            max(h - 2 * r, 1e-6),
            boxstyle=mp.BoxStyle("Round", pad=r),
            edgecolor=ec,
            facecolor=fc,
            linewidth=lw,
            linestyle=ls,
            zorder=z,
        )
    )


def line(ax, x1, y1, x2, y2, c=INK, lw=LW_MAIN, ls="-", z=3):
    ax.plot([x1, x2], [y1, y2], color=c, linewidth=lw, linestyle=ls, zorder=z, solid_capstyle="butt")


def txt(ax, x, y, s, size=5.0, c=INK2, ha="left", va="center", weight="normal", z=6, style="normal", rot=0):
    ax.text(
        x,
        y,
        s,
        fontsize=size,
        color=c,
        ha=ha,
        va=va,
        family=MONO,
        fontweight=weight,
        zorder=z,
        fontstyle=style,
        rotation=rot,
        rotation_mode="anchor",
    )


def centerline(ax, x1, y1, x2, y2):
    line(ax, x1, y1, x2, y2, c=INK3, lw=0.35, ls=(0, (7, 2, 1, 2)), z=2)


def _arrow(ax, x, y, dx, dy, c=DIM):
    ax.add_patch(
        mp.FancyArrow(
            x, y, dx, dy, width=0, head_width=1.0, head_length=1.7, length_includes_head=True, color=c, zorder=5
        )
    )


def dim_h(ax, x1, x2, y, label, ext_from=None, size=4.8):
    """Horizontal dimension. Label sits above the line."""
    if ext_from is not None:
        for x in (x1, x2):
            line(ax, x, ext_from, x, y - 1.2 if y < ext_from else y + 1.2, c=DIM, lw=LW_DIM, z=4)
    line(ax, x1, y, x2, y, c=DIM, lw=LW_DIM, z=4)
    reach = min(4.2, (x2 - x1) / 2.5)
    _arrow(ax, x1, y, reach, 0)
    _arrow(ax, x2, y, -reach, 0)
    txt(ax, (x1 + x2) / 2, y + 2.2, label, size=size, c=DIM, ha="center")


def dim_v(ax, y1, y2, x, label, ext_from=None, size=4.8):
    """Vertical dimension. Label is rotated so nested dimensions do not collide."""
    if ext_from is not None:
        for y in (y1, y2):
            line(ax, ext_from, y, x + 1.2 if x < ext_from else x - 1.2, y, c=DIM, lw=LW_DIM, z=4)
    line(ax, x, y1, x, y2, c=DIM, lw=LW_DIM, z=4)
    reach = min(4.2, (y2 - y1) / 2.5)
    _arrow(ax, x, y1, 0, reach)
    _arrow(ax, x, y2, 0, -reach)
    txt(ax, x - 1.6, (y1 + y2) / 2, label, size=size, c=DIM, ha="center", va="bottom", rot=90)


def leader(ax, px, py, knee_x, tx, ty, label, size=4.8, c=INK2, ha="left"):
    ax.plot([px, knee_x, tx], [py, ty, ty], color=INK3, linewidth=LW_DIM, zorder=4)
    ax.add_patch(mp.Circle((px, py), 0.45, color=INK3, zorder=5))
    txt(ax, tx + (1.2 if ha == "left" else -1.2), ty, label, size=size, c=c, ha=ha)


def view_title(ax, x, y, name, sub=""):
    txt(ax, x, y, name, size=6.8, c=INK, weight="bold")
    line(ax, x, y - 2.8, x + max(28.0, len(name) * 1.5), y - 2.8, c=INK, lw=0.7, z=4)
    if sub:
        txt(ax, x, y - 6.4, sub, size=4.6, c=INK3)


# --- front elevation ----------------------------------------------------


def front_elevation(ax, d):
    s = MAIN_SCALE
    W = d["loaded_overall_w"]
    Hc = d["cavity_depth"]
    roll_d = d["roll_clamped_depth"]
    H = d["sealed_h"]

    def X(v):
        return FE_X + v * s

    def Y(v):
        return FE_Y + v * s

    view_title(ax, COL_A + 4, 248.0, "FRONT ELEVATION", "SEALED AND LOADED  ·  SCALE 1:1.5")

    # Body and roll.
    rrect(ax, X(0), Y(0), W * s, Hc * s, 5.0 * s, ec=INK, lw=LW_OUTLINE)
    line(ax, X(0), Y(Hc), X(W), Y(Hc), c=INK3, lw=LW_THIN, ls=(0, (3, 2)), z=4)
    rrect(ax, X(0), Y(Hc), W * s, roll_d * s, roll_d * s / 2, ec=INK, lw=LW_OUTLINE, fc="#101318")
    for i in range(1, 4):
        fx = X(W * (0.30 + 0.13 * i))
        line(ax, fx, Y(Hc) + 0.5, fx, Y(Hc + roll_d) - 0.5, c=INK3, lw=LW_DIM, z=5)

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
    txt(
        ax,
        X(W / 2),
        Y(ay0 + al * 0.52) - 8.4,
        f"CLEAR {al:.0f} x {aw:.0f}",
        size=4.6,
        c=INK3,
        ha="center",
    )

    # Electronics rail.
    rail_y = by0 + bl - BEZEL_TOP_RAIL
    line(ax, X(bx0), Y(rail_y), X(bx0 + bw), Y(rail_y), c=INK3, lw=LW_THIN, ls=(0, (2, 2)), z=4)

    # Load cells, two under each strap anchor.
    anchors = [W * 0.235, W * 0.765]
    cell_y = rail_y + BEZEL_TOP_RAIL * 0.32
    for a in anchors:
        for dx in (-6.5, 6.5):
            ax.add_patch(
                mp.Circle((X(a + dx), Y(cell_y)), 3.2 * s, edgecolor=DIM, facecolor="#0f2a2c", lw=LW_THIN, zorder=5)
            )
            ax.add_patch(
                mp.Circle((X(a + dx), Y(cell_y)), 1.0 * s, edgecolor=INK2, facecolor="none", lw=LW_DIM, zorder=6)
            )

    # Status LED.
    led_w, led_h = 26.0, 3.0
    led_x, led_y = (W - led_w) / 2.0, by0 + bl - 4.5
    rrect(ax, X(led_x), Y(led_y), led_w * s, led_h * s, led_h * s / 2, ec=ACC, lw=LW_MAIN, fc="#123a24")

    # Clamp straps and buckles.
    for a in anchors:
        sx = X(a)
        rect(ax, sx - WEB_W * s / 2, Y(rail_y - 3), WEB_W * s, (Hc + roll_d - rail_y + 3) * s, ec=INK2, lw=LW_THIN)
        rrect(
            ax,
            sx - 11.0 * s,
            Y(Hc + roll_d * 0.12),
            22.0 * s,
            roll_d * 0.76 * s,
            1.2 * s,
            ec=INK,
            lw=LW_MAIN,
            fc="#151a21",
            z=6,
        )

    # Tether anchor.
    ax.add_patch(mp.Circle((X(W - 10), Y(8)), 2.6 * s, edgecolor=INK2, facecolor="none", lw=LW_THIN, zorder=5))

    centerline(ax, X(W / 2), Y(-16), X(W / 2), Y(H + 10))

    # Section arrows A-A.
    say = Y(ay0 + al * 0.62)
    _arrow(ax, X(-14), say, 5.0, 0)
    _arrow(ax, X(W + 14), say, -5.0, 0)
    txt(ax, X(-16), say, "A", size=6.2, c=DIM, ha="right", weight="bold")
    txt(ax, X(W + 16), say, "A", size=6.2, c=DIM, ha="left", weight="bold")

    # Dimensions: horizontal below, vertical nested on the left.
    dim_h(ax, X(0), X(W), Y(-14), f"{W:.0f} OVERALL", ext_from=Y(0))
    dim_h(ax, X(ax0), X(ax0 + aw), Y(-25), f"{aw:.0f} CLEAR", ext_from=Y(ay0))
    dim_h(ax, X(fx0), X(fx0 + fw), Y(-36), f"{fw:.0f} WELD FLANGE", ext_from=Y(fy0))
    dim_h(ax, X(bx0), X(bx0 + bw), Y(H) + 12.0, f"{bw:.0f} BEZEL", ext_from=Y(by0 + bl))

    dim_v(ax, Y(ay0), Y(ay0 + al), X(0) - 8.0, f"{al:.0f} CLEAR", ext_from=X(ax0))
    dim_v(ax, Y(0), Y(Hc), X(0) - 18.0, f"{Hc:.0f} CAVITY", ext_from=X(0))
    dim_v(ax, Y(0), Y(H), X(0) - 28.0, f"{H:.0f} SEALED", ext_from=X(0))

    # Callouts, all stacked on the right.
    kx, tx = X(W) + 6.0, X(W) + 8.0
    callouts = [
        (W * 0.50, Hc + roll_d * 0.5, 238.0, "ROLL-TOP CLOSURE, 3 FOLDS", INK2),
        (anchors[1], Hc + roll_d * 0.5, 231.0, "SIDE-RELEASE BUCKLE x2", INK2),
        (led_x + led_w, led_y + led_h / 2, 219.0, "SEAL-STATUS LED", ACC),
        (anchors[1] + 6.5, cell_y, 212.0, f"LOAD CELL x4, {d['clamp_force_per_cell']:.0f} N MIN EACH", DIM),
        (bx0 + bw, rail_y + 2.0, 205.0, f"{BEZEL_TOP_RAIL:.0f} ELECTRONICS RAIL", INK2),
        (gx0 + gw, gy0 + gl * 0.72, 192.0, f"{GLASS_SEAT_LAND:.0f} BONDED GLASS SEAT", INK2),
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
        ("REAR CLEARANCE", 1.5, "#0b0d11", INK3),
        ("REAR PLY, WELDED", 0.5, "#1d232c", INK2),
    ]
    total = sum(t for _, t, _, _ in layers) * s
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

    txt(ax, COL_B, bottom - 6.0, f"CAVITY {d['cavity_t']:.1f}  ·  PANE DEFLECTION {d['glass_defl_rated']:.2f}", size=4.5, c=INK3)
    txt(ax, COL_B, bottom - 10.5, f"AT RATED, {d['glass_defl_proof']:.2f} AT PROOF - AIR GAP CLEARS BOTH", size=4.5, c=INK3)


# --- detail B -----------------------------------------------------------


def detail_roll(ax, d):
    s = DETAIL_SCALE
    cx, cy = COL_B + 48.0, 136.0
    view_title(ax, COL_B, 172.0, "DETAIL B", f"ROLL CLAMP, SECTION  ·  SCALE {s:.1f}:1")

    t = d["roll_clamped_t"] * s
    dp = d["roll_clamped_depth"] * s

    ax.add_patch(mp.Ellipse((cx, cy), dp, t, edgecolor=INK, facecolor="#0f1319", lw=LW_MAIN, zorder=3))
    for i in range(3):
        f = 1.0 - i * 0.27
        ax.add_patch(
            mp.Arc((cx, cy), dp * f, t * f, theta1=-166 + i * 10, theta2=166 - i * 10, edgecolor=INK2, lw=LW_THIN, zorder=4)
        )
    rect(ax, cx - 4.0 * s / 2, cy - 3.0 * s / 2, 4.0 * s, 3.0 * s, ec=INK, lw=LW_THIN, fc="#1d232c", z=5)
    leader(ax, cx, cy + 1.5 * s, cx + dp / 2 + 4, cx + dp / 2 + 6, cy + t / 2 + 4.0, "MOUTH BATTEN 4.0 x 3.0")

    # Webbing over the bundle.
    line(ax, cx - dp / 2 - 12, cy + t / 2 + 1.4, cx + dp / 2 + 12, cy + t / 2 + 1.4, c=INK2, lw=1.3)
    line(ax, cx - dp / 2 - 12, cy + t / 2 + 3.2, cx + dp / 2 + 12, cy + t / 2 + 3.2, c=INK2, lw=LW_DIM)
    txt(ax, cx - dp / 2 - 13, cy + t / 2 + 2.3, f"{WEB_W:.0f} WEBBING", size=4.5, c=INK2, ha="right")

    # Bezel top rail with two cells in section.
    rail_h = 11.0
    rail_y = cy - t / 2 - 4.0 - rail_h
    rect(ax, cx - dp / 2 - 12, rail_y, dp + 24, rail_h, ec=INK, lw=LW_MAIN, fc="#12161d")
    for dx in (-13.0, 13.0):
        rect(ax, cx + dx - 4.5, rail_y + 3.0, 9.0, 5.0, ec=DIM, lw=LW_THIN, fc="#0f2a2c", z=5)
    txt(ax, cx, rail_y - 3.6, "BEZEL TOP RAIL, LOAD CELLS IN SECTION", size=4.5, c=INK3, ha="center")

    _arrow(ax, cx, cy + t / 2 + 10.5, 0, -4.5)
    txt(
        ax,
        cx,
        cy + t / 2 + 12.5,
        f"CLAMP {d['clamp_force_total']:.0f} N TOTAL  ·  {d['clamp_force_per_cell']:.0f}-"
        f"{d['clamp_force_per_cell_max']:.0f} N PER CELL",
        size=4.6,
        c=DIM,
        ha="center",
    )

    dim_h(ax, cx - dp / 2, cx + dp / 2, rail_y - 9.0, f"{d['roll_clamped_depth']:.1f}", ext_from=cy - t / 2)
    dim_v(ax, cy - t / 2, cy + t / 2, cx - dp / 2 - 20.0, f"{d['roll_clamped_t']:.1f}")
    txt(ax, COL_B, 95.0, f"FREE BUNDLE dia {d['roll_dia']:.1f}, 3 FOLDS x 2.0 PER FOLD", size=4.5, c=INK3)
    txt(ax, COL_B, 90.5, f"CONSUMES {d['roll_consumed']:.0f} OF PANEL LENGTH", size=4.5, c=INK3)


# --- flat packed --------------------------------------------------------


def flat_packed(ax, d):
    s = PACK_SCALE
    ox, oy = COL_B + 4.0, 50.0
    view_title(ax, COL_B, 80.0, "FLAT PACKED", f"EMPTY, EDGE VIEW  ·  SCALE 1:{1 / s:.0f}")

    L = d["sealed_h"] * s
    t = d["packed_t"] * s
    tr = d["packed_t_at_roll"] * s
    roll_len = d["roll_clamped_depth"] * s * 2.2

    rrect(ax, ox, oy, L - roll_len, t, t / 2, ec=INK, lw=LW_MAIN, fc="#101318")
    rrect(ax, ox + L - roll_len, oy, roll_len, tr, tr / 2, ec=INK, lw=LW_MAIN, fc="#161c24")
    bez = d["bezel_l"] * s
    rect(ax, ox + 6.0, oy + 0.4, bez, t - 0.8, ec=INK3, lw=LW_THIN, ls=(0, (3, 2)))

    dim_h(ax, ox, ox + L, oy - 9.0, f"{d['sealed_h']:.0f}", ext_from=oy)
    dim_v(ax, oy, oy + t, ox - 6.0, f"{d['packed_t']:.1f}")
    leader(
        ax,
        ox + L - roll_len / 2,
        oy + tr,
        ox + L + 4,
        ox + L + 6,
        oy + 18.0,
        f"{d['packed_t_at_roll']:.1f} AT ROLL",
    )
    leader(ax, ox + 6.0 + bez / 2, oy + t, ox + 24, ox + 26, oy + 11.0, "RIGID BEZEL DOES NOT COLLAPSE")


# --- right column -------------------------------------------------------


def spec_table(ax, d, y_title):
    x, w = COL_C, COL_C_W
    view_title(ax, x, y_title, "SPECIFICATION")
    rows = [
        ("BODY", "500D ARAMID, TPU BOTH FACES, 0.50 PLY"),
        ("BEZEL", "PPA GF30 + TPU OVERMOULD WELD LIP"),
        ("WINDOW", f"{d['glass_l']:.0f} x {d['glass_w']:.0f} x {d['glass_t']:.1f} CHEM-STRENGTHENED"),
        ("CLEAR APERTURE", f"{d['aperture_l']:.0f} x {d['aperture_w']:.0f} — FULL DISPLAY"),
        ("CLOSURE", "ROLL-TOP, 3 FOLDS, 2 CLAMP STRAPS"),
        ("SEALING", "RF-WELDED 10 LAP, NO STITCH BELOW FOLD"),
        ("RATING", f"{RATED_DEPTH_M:.0f} m / {RATED_DURATION_MIN:.0f} min, PROOF {d['proof_depth_m']:.0f} m"),
        ("PANE STRESS", f"{d['glass_stress_rated']:.0f} MPa RATED, {d['glass_stress_proof']:.0f} MPa PROOF"),
        ("SENSING", f"4x LOAD CELL, >={d['clamp_force_per_cell']:.0f} N EACH TO VERIFY"),
        ("SEAL INDICATOR", "GREEN = SEALED   RED = CHECK CLAMP"),
        ("DEVICE MAX", f"{DEVICE.l:.0f} x {DEVICE.w:.0f} x {DEVICE.t:.0f}"),
        ("SEALED", f"{d['loaded_overall_w']:.0f} x {d['sealed_h']:.0f} x {d['sealed_t']:.1f}"),
        ("PACKED", f"{d['loaded_overall_w']:.0f} x {d['sealed_h']:.0f} x {d['packed_t']:.1f}"),
        ("MASS", f"{d['mass_total']:.0f} g EMPTY, {d['mass_total'] + DEVICE.mass_g:.0f} g LOADED"),
        ("BUOYANCY", f"{d['net_buoyancy']:+.0f} g — SINKS, TETHER REQUIRED"),
    ]
    rh, split = 4.9, 30.0
    top = y_title - 6.0
    bot = top - rh * len(rows)
    rect(ax, x, bot, w, rh * len(rows), ec=INK3, lw=LW_THIN)
    line(ax, x + split, bot, x + split, top, c=GRID, lw=0.4, z=2)
    for i, (k, v) in enumerate(rows):
        ry = top - rh * (i + 1)
        if i:
            line(ax, x, ry + rh, x + w, ry + rh, c=GRID, lw=0.35, z=2)
        txt(ax, x + 1.8, ry + rh / 2, k, size=4.4, c=INK3)
        txt(ax, x + split + 1.8, ry + rh / 2, v, size=4.4, c=ACC2 if "SINKS" in v else INK2)
    return bot


def notes_block(ax, d, y_title):
    x = COL_C
    view_title(ax, x, y_title, "NOTES")
    notes = [
        ("1. ALL DIMENSIONS IN MILLIMETRES. TOL +/-1.0 UNLESS NOTED.", INK2),
        (f"2. WINDOW EXPOSES THE FULL {DEVICE.display_l:.0f} x {DEVICE.display_w:.0f} DISPLAY PLUS", INK2),
        ("   2.0 REGISTRATION TOLERANCE PER SIDE. (CHANGED FROM REV B)", INK2),
        (f"3. PANE THICKNESS FROM FLAT-PLATE BENDING AT {d['proof_depth_m']:.0f} m PROOF.", INK2),
        (f"   MINIMUM {d['glass_t_min']:.2f}, SPECIFIED {d['glass_t']:.1f} FOR IMPACT MARGIN.", INK2),
        ("4. DEVICE SITS IN A WELDED TPU RETENTION SLEEVE SO THE DISPLAY", INK2),
        ("   REGISTERS TO THE APERTURE. WITHOUT IT THE WINDOW GROWS. (NEW)", INK2),
        (f"5. THE {BEZEL_TOP_RAIL:.0f} ELECTRONICS RAIL SETS THE BODY LENGTH. CELL IS", INK2),
        ("   FLAT, 40 x 10 x 4 / 120 mAh; A SQUARE CELL COSTS 8. (CHANGED)", INK2),
        (f"6. CLAMP THRESHOLD IS 3x INTERNAL PRESSURE OVER THE", INK2),
        (f"   {d['roll_contact_area']:.0f} mm2 ROLL CONTACT PATCH. (CHANGED)", INK2),
        ("7. NO STITCH PENETRATIONS BELOW THE FOLD LINE.", INK2),
        (f"8. VIEW-ONLY. CAPACITIVE TOUCH WILL NOT WORK THROUGH", ACC2),
        (f"   {d['glass_t']:.1f} GLASS AND A {d['air_gap']:.1f} AIR GAP. (NEW)", ACC2),
        (f"9. LOADED ASSEMBLY IS {abs(d['net_buoyancy']):.0f} g NEGATIVE. THE TETHER IS", ACC2),
        ("   RETENTION, NOT AN ACCESSORY. (NEW)", ACC2),
        ("10. RATING IS A DESIGN TARGET. NOTHING HAS BEEN SUBMERGED.", ACC2),
        ("11. SURFACE WATERSPORTS AND SNORKELLING. NOT FOR SCUBA.", ACC2),
    ]
    top = y_title - 7.0
    for i, (n, c) in enumerate(notes):
        txt(ax, x, top - i * 4.1, n, size=4.4, c=c)
    return top - len(notes) * 4.1


def revision_block(ax, d, y_title):
    x, w = COL_C, COL_C_W
    view_title(ax, x, y_title, f"REV {REVISION} — CHANGES FROM B")
    rows = [
        ("WINDOW CLEAR", "100 x 80", f"{d['aperture_l']:.0f} x {d['aperture_w']:.0f}"),
        ("RATING", "5 m / 30 min", f"{RATED_DEPTH_M:.0f} m / {RATED_DURATION_MIN:.0f} min"),
        ("BODY OUTER", "130 x 150", f"{d['loaded_overall_w']:.0f} x {d['sealed_h']:.0f}"),
        ("CLAMP / CORNER", "100 N", f"{d['clamp_force_per_cell']:.0f} N"),
        ("MASS", "225 g EST.", f"{d['mass_total']:.0f} g BUDGETED"),
        ("TOP RAIL", "UNDEFINED", f"{BEZEL_TOP_RAIL:.0f} ELECTRONICS"),
    ]
    rh = 5.0
    top = y_title - 6.0
    bot = top - rh * (len(rows) + 1)
    rect(ax, x, bot, w, rh * (len(rows) + 1), ec=INK3, lw=LW_THIN)
    hdr = top - rh
    for cx, label in ((1.8, "ITEM"), (32.0, "REV B"), (68.0, f"REV {REVISION}")):
        txt(ax, x + cx, hdr + rh / 2, label, size=4.4, c=INK3)
    line(ax, x, hdr, x + w, hdr, c=GRID, lw=0.5, z=2)
    for i, (k, a, b) in enumerate(rows):
        ry = hdr - rh * (i + 1)
        txt(ax, x + 1.8, ry + rh / 2, k, size=4.4, c=INK2)
        txt(ax, x + 32.0, ry + rh / 2, a, size=4.4, c=INK3)
        txt(ax, x + 68.0, ry + rh / 2, b, size=4.4, c=DIM)
    for cx in (30.0, 66.0):
        line(ax, x + cx, bot, x + cx, top, c=GRID, lw=0.4, z=2)
    return bot


def title_block(ax, d):
    x0, y0 = MARGIN, MARGIN
    w = SHEET_W - 2 * MARGIN
    rect(ax, x0, y0, w, TITLE_H, ec=INK, lw=LW_MAIN)
    cols = [
        ("TITLE / DESIGNATION", "D14 ROLLTOP - DIVE-READY PHONE POUCH", 100.0, 7.6),
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


# --- assembly -----------------------------------------------------------


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

    txt(ax, MARGIN + 4, SHEET_H - MARGIN - 10, "D14 ROLLTOP", size=19, c=INK, weight="bold")
    txt(ax, MARGIN + 88, SHEET_H - MARGIN - 10, f"REV {REVISION}", size=12, c=DIM, weight="bold")
    txt(
        ax,
        MARGIN + 4,
        SHEET_H - MARGIN - 19,
        "SOFT ARAMID BODY  ·  RF-WELDED RIGID WINDOW BEZEL  ·  FULL-DISPLAY TEMPERED GLASS  ·  "
        "CLAMP-VERIFICATION SENSING",
        size=5.4,
        c=INK2,
    )
    txt(
        ax,
        MARGIN + 4,
        SHEET_H - MARGIN - 25,
        "EVERY DIMENSION IS COMPUTED BY rev_c_dimensions.py FROM THE DEVICE DATUM  ·  DERIVATIONS IN "
        "derived-dimensions-revC.md",
        size=4.6,
        c=INK3,
        style="italic",
    )
    line(ax, MARGIN, HEADER_Y, SHEET_W - MARGIN, HEADER_Y, c=INK, lw=LW_THIN, z=2)

    # Column rules.
    for cx in (COL_B - 6.0, COL_C - 6.0):
        line(ax, cx, BAND_BOT - 2.0, cx, HEADER_Y, c=GRID, lw=0.5, z=2)

    front_elevation(ax, d)
    section_aa(ax, d)
    detail_roll(ax, d)
    flat_packed(ax, d)

    y = spec_table(ax, d, 250.0)
    y = notes_block(ax, d, y - 7.0)
    revision_block(ax, d, y - 4.0)

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
