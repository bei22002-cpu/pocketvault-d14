#!/usr/bin/env python3
"""
Nereid — generate demo videos of interfaces working underwater.
Outputs MP4s to blueprints/videos/
"""

from __future__ import annotations

import math
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos"
W, H = 1280, 720
FPS = 30
BG = (7, 17, 22)
PANEL = (12, 28, 36)
INK = (231, 240, 242)
MUTED = (138, 160, 168)
ACCENT = (46, 196, 168)
ACCENT2 = (126, 200, 227)
WATER = (18, 55, 68)
PHONE = (20, 24, 28)
WARN = (226, 179, 106)


def font(size: int, bold: bool = False):
    candidates = [
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
        "C:/Windows/Fonts/calibri.ttf",
    ]
    if bold:
        candidates = [
            "C:/Windows/Fonts/segoeuib.ttf",
            "C:/Windows/Fonts/arialbd.ttf",
        ] + candidates
    for p in candidates:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


F_TITLE = font(42, True)
F_H = font(28, True)
F_BODY = font(20)
F_SMALL = font(15)
F_TINY = font(13)


def lerp(a, b, t):
    return a + (b - a) * t


def ease(t):
    return t * t * (3 - 2 * t)


def clamp01(t):
    return max(0.0, min(1.0, t))


def new_frame():
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)
    # subtle water wash
    for y in range(0, H, 4):
        a = int(8 + 6 * math.sin(y / 40))
        draw.line([(0, y), (W, y)], fill=(BG[0], BG[1] + a, BG[2] + a))
    return img, draw


def chrome(draw, title: str, subtitle: str, frame_i: int, total: int):
    draw.rectangle([0, 0, W, 56], fill=(5, 12, 16))
    draw.text((28, 14), "NEREID", font=F_BODY, fill=ACCENT)
    draw.text((120, 16), title, font=F_BODY, fill=INK)
    draw.text((28, H - 36), subtitle, font=F_TINY, fill=MUTED)
    # progress
    pw = int((frame_i / max(total - 1, 1)) * (W - 56))
    draw.rectangle([28, H - 14, W - 28, H - 10], fill=(30, 45, 52))
    draw.rectangle([28, H - 14, 28 + pw, H - 10], fill=ACCENT)


def draw_case(draw, cx, cy, cw, ch, aperture=True, label=""):
    x0, y0 = cx - cw // 2, cy - ch // 2
    draw.rounded_rectangle([x0, y0, x0 + cw, y0 + ch], radius=28, fill=PANEL, outline=ACCENT2, width=2)
    if aperture:
        m = 22
        draw.rounded_rectangle([x0 + m, y0 + m, x0 + cw - m, y0 + ch - m], radius=18, fill=PHONE, outline=(40, 55, 62), width=1)
        # fake UI
        draw.rounded_rectangle([x0 + m + 16, y0 + m + 20, x0 + cw - m - 16, y0 + m + 70], radius=10, fill=(28, 40, 48))
        draw.text((x0 + m + 28, y0 + m + 34), "MAP · DIVE", font=F_SMALL, fill=ACCENT2)
        # buttons / targets
        for i, name in enumerate(["Mark", "Photo", "Comms"]):
            bx = x0 + m + 24 + i * 90
            by = y0 + ch // 2 + 20
            draw.rounded_rectangle([bx, by, bx + 78, by + 36], radius=8, fill=(32, 48, 56), outline=(55, 75, 85))
            draw.text((bx + 14, by + 8), name, font=F_TINY, fill=INK)
    if label:
        draw.text((x0, y0 - 28), label, font=F_SMALL, fill=MUTED)
    return x0, y0, cw, ch


def draw_finger(draw, x, y, press=0.0, glove=False):
    r = 18 + int(4 * press)
    col = (210, 170, 140) if not glove else (35, 55, 48)
    draw.ellipse([x - r, y - r, x + r, y + r], fill=col, outline=(40, 40, 40))
    if glove:
        draw.ellipse([x - 6, y - 6, x + 6, y + 6], fill=(180, 40, 40))  # magnet tip
    # ripple when pressed
    if press > 0.05:
        rr = 28 + int(40 * press)
        alpha_ring = (ACCENT[0], ACCENT[1], ACCENT[2])
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], outline=alpha_ring, width=2)


def draw_stylus(draw, x, y, hover=0.0):
    # tip
    draw.polygon([(x, y), (x - 8, y - 36), (x + 8, y - 36)], fill=INK)
    draw.rounded_rectangle([x - 6, y - 120, x + 6, y - 36], radius=4, fill=ACCENT2)
    if hover > 0:
        rr = 12 + int(20 * hover)
        draw.ellipse([x - rr, y - rr, x + rr, y + rr], outline=WARN, width=2)


def waveform(draw, x, y, w, h, t, active=True):
    draw.rectangle([x, y, x + w, y + h], fill=(8, 18, 24), outline=(40, 60, 70))
    mid = y + h // 2
    pts = []
    for i in range(w):
        amp = (0.35 + 0.65 * abs(math.sin(t * 4 + i * 0.05))) if active else 0.08
        yy = mid + int(math.sin(i * 0.12 + t * 8) * (h * 0.35) * amp)
        pts.append((x + i, yy))
    if len(pts) > 1:
        draw.line(pts, fill=ACCENT if active else MUTED, width=2)


def write_video(path: Path, frames: list[Image.Image], fps: int = FPS):
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = imageio.get_writer(
        str(path),
        fps=fps,
        codec="libx264",
        quality=8,
        pixelformat="yuv420p",
        macro_block_size=1,
    )
    for fr in frames:
        writer.append_data(np.asarray(fr))
    writer.close()
    print(f"Wrote {path.name} ({len(frames)} frames, {len(frames)/fps:.1f}s)")


# ---------- Demo scenes ----------

def demo_force_touch(seconds=6):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "A1 / A3 · Force-Sensed Touch", "Four corner load cells · moment-balance XY · force sum = click", i, n)
        x0, y0, cw, ch = draw_case(d, 520, 360, 280, 520, label="Sealed dry-air pocket")
        # load cell markers
        cells = [(x0 + 40, y0 + 40), (x0 + cw - 40, y0 + 40), (x0 + 40, y0 + ch - 40), (x0 + cw - 40, y0 + ch - 40)]
        for cx, cy in cells:
            d.ellipse([cx - 8, cy - 8, cx + 8, cy + 8], outline=ACCENT, width=2)

        # finger path: approach → press Mark → swipe → release
        path_t = ease(clamp01((t - 0.1) / 0.8))
        fx = lerp(x0 + 70, x0 + 200, path_t)
        fy = lerp(y0 + 180, y0 + ch // 2 + 38, clamp01((t - 0.05) / 0.35))
        press = 0.0
        if 0.35 < t < 0.55:
            press = ease(clamp01((t - 0.35) / 0.08))
        elif 0.55 <= t < 0.7:
            press = 1.0 - ease(clamp01((t - 0.55) / 0.12))
        draw_finger(d, fx, fy, press)

        # HUD
        d.rounded_rectangle([820, 120, 1220, 560], radius=16, fill=PANEL, outline=(40, 60, 70))
        d.text((850, 145), "LOAD CELL READOUT", font=F_SMALL, fill=MUTED)
        forces = []
        for ci, (cx, cy) in enumerate(cells):
            # distance-based force proxy
            dist = math.hypot(fx - cx, fy - cy)
            f = max(0, (180 - dist) / 180) * (0.3 + 0.7 * press)
            forces.append(f)
            bar_w = int(280 * f)
            by = 200 + ci * 55
            d.text((850, by), f"LC{ci+1}", font=F_TINY, fill=MUTED)
            d.rectangle([920, by + 4, 1200, by + 22], fill=(20, 35, 42))
            d.rectangle([920, by + 4, 920 + bar_w, by + 22], fill=ACCENT)
        # solved XY
        sx = sum(f * cells[i][0] for i, f in enumerate(forces)) / (sum(forces) + 1e-6)
        sy = sum(f * cells[i][1] for i, f in enumerate(forces)) / (sum(forces) + 1e-6)
        d.text((850, 430), f"Solve X/Y  →  ({sx-x0:.0f}, {sy-y0:.0f}) px", font=F_SMALL, fill=ACCENT2)
        d.text((850, 465), f"Z-click     →  {'ACTIVE' if press > 0.6 else 'idle'}", font=F_SMALL, fill=WARN if press > 0.6 else MUTED)
        d.text((850, 510), "Works through water — strain, not capacitance", font=F_TINY, fill=MUTED)
        frames.append(img)
    return frames


def demo_hall_glove(seconds=6):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "B5 · Hall-Glove", "8×16 Hall grid reads neodymium fingertip through neoprene", i, n)
        x0, y0, cw, ch = draw_case(d, 480, 360, 260, 500, label="Passive glass cover")
        # hall grid
        cols, rows = 8, 12
        gx0, gy0 = x0 + 40, y0 + 50
        gw, gh = cw - 80, ch - 120
        for r in range(rows):
            for c in range(cols):
                px = gx0 + c * (gw / (cols - 1))
                py = gy0 + r * (gh / (rows - 1))
                d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(40, 70, 80))

        # glove path
        ang = t * math.pi * 2
        fx = gx0 + gw * (0.5 + 0.35 * math.sin(ang))
        fy = gy0 + gh * (0.5 + 0.3 * math.cos(ang * 0.7))
        draw_finger(d, fx, fy, 0.2, glove=True)

        # highlight nearest cells
        for r in range(rows):
            for c in range(cols):
                px = gx0 + c * (gw / (cols - 1))
                py = gy0 + r * (gh / (rows - 1))
                dist = math.hypot(fx - px, fy - py)
                if dist < 55:
                    strength = 1 - dist / 55
                    col = (int(46 * strength + 20), int(196 * strength + 30), int(168 * strength + 40))
                    d.ellipse([px - 4, py - 4, px + 4, py + 4], fill=col)

        d.rounded_rectangle([820, 160, 1220, 520], radius=16, fill=PANEL, outline=(40, 60, 70))
        d.text((850, 190), "FIELD GRADIENT", font=F_SMALL, fill=MUTED)
        d.text((850, 240), "Water is non-magnetic", font=F_H, fill=INK)
        d.text((850, 290), "No hydrostatic compensation.", font=F_BODY, fill=MUTED)
        d.text((850, 330), "No baseline drift from salinity.", font=F_BODY, fill=MUTED)
        d.text((850, 390), "Cursor tracks glove magnet", font=F_SMALL, fill=ACCENT)
        d.ellipse([850, 440, 880, 470], fill=(180, 40, 40))
        d.text((895, 445), "N42 pellet in fingertip", font=F_TINY, fill=MUTED)
        frames.append(img)
    return frames


def demo_stylus_emr(seconds=6):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "B6 · Stylus-EMR", "Passive LC tip · ~0.3 mm · hover + 1024-level pressure", i, n)
        x0, y0, cw, ch = draw_case(d, 500, 370, 300, 480, label="EMR coil grid behind glass")
        # draw path on UI
        pts = []
        for k in range(int(t * 80) + 1):
            u = k / 80
            px = x0 + 60 + u * (cw - 120)
            py = y0 + 160 + math.sin(u * math.pi * 3) * 60
            pts.append((px, py))
        if len(pts) > 1:
            d.line(pts, fill=ACCENT, width=3)
        sx, sy = pts[-1] if pts else (x0 + 60, y0 + 160)
        hover = 0.4 + 0.4 * abs(math.sin(t * 10))
        press = 0.2 + 0.8 * ease(abs(math.sin(t * math.pi * 2)))
        draw_stylus(d, sx, sy - 8, hover)

        d.rounded_rectangle([860, 140, 1230, 560], radius=16, fill=PANEL, outline=(40, 60, 70))
        d.text((890, 170), "EMR CHANNEL", font=F_SMALL, fill=MUTED)
        d.text((890, 220), f"Hover  {hover*5:.1f} mm", font=F_BODY, fill=ACCENT2)
        d.text((890, 265), f"Pressure  {int(press*1024)} / 1024", font=F_BODY, fill=WARN)
        # pressure bar
        d.rectangle([890, 320, 1180, 344], fill=(20, 35, 42))
        d.rectangle([890, 320, 890 + int(290 * press), 344], fill=WARN)
        d.text((890, 380), "Chartwork · annotation · sketch", font=F_SMALL, fill=INK)
        d.text((890, 420), "Seawater = one more dielectric", font=F_TINY, fill=MUTED)
        d.text((890, 450), "to tune — stylus stays passive", font=F_TINY, fill=MUTED)
        frames.append(img)
    return frames


def demo_resistive(seconds=5):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "B8 · Resistive-Hard", "Two layers physically touch — water cannot fake contact", i, n)
        x0, y0, cw, ch = draw_case(d, 480, 360, 270, 500, label="Hard-coated PC + ITO film")
        # cross section inset
        d.rounded_rectangle([820, 130, 1230, 560], radius=16, fill=PANEL, outline=(40, 60, 70))
        d.text((850, 155), "STACK CROSS-SECTION", font=F_SMALL, fill=MUTED)
        layers = [
            ("Hard coat PC", (90, 120, 140)),
            ("ITO top", (60, 90, 110)),
            ("Microdot gap", (20, 35, 42)),
            ("ITO bottom", (60, 90, 110)),
            ("Substrate", (40, 55, 65)),
        ]
        ly = 210
        for name, col in layers:
            hh = 36 if "gap" not in name.lower() else 22
            d.rectangle([850, ly, 1180, ly + hh], fill=col, outline=(30, 40, 48))
            d.text((860, ly + 8), name, font=F_TINY, fill=INK)
            ly += hh + 6

        # press collapses gap
        press = ease(abs(math.sin(t * math.pi * 2)))
        fx, fy = x0 + cw // 2, y0 + ch // 2 + 30
        draw_finger(d, fx, fy, press)
        if press > 0.5:
            d.text((850, 500), "CONTACT  →  voltage divider XY", font=F_SMALL, fill=ACCENT)
        else:
            d.text((850, 500), "OPEN GAP  →  no false touch", font=F_SMALL, fill=MUTED)
        frames.append(img)
    return frames


def demo_crownpad(seconds=5):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "C10 · Crownpad", "Rotary encoder + hat + keys — nothing water can confuse", i, n)
        x0, y0, cw, ch = draw_case(d, 420, 360, 240, 460, label="Viewport only")
        # controls on right of case
        cx, cy = x0 + cw + 70, y0 + 160
        ang = t * math.pi * 4
        d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=ACCENT, width=3)
        d.line([(cx, cy), (cx + 32 * math.cos(ang), cy + 32 * math.sin(ang))], fill=INK, width=3)
        d.text((cx - 30, cy + 55), "CROWN", font=F_TINY, fill=MUTED)
        # hat
        hx, hy = cx, cy + 150
        d.ellipse([hx - 28, hy - 28, hx + 28, hy + 28], outline=ACCENT2, width=2)
        dirs = [(0, -1), (1, 0), (0, 1), (-1, 0)]
        active = int(t * 8) % 4
        for di, (dx, dy) in enumerate(dirs):
            col = WARN if di == active else (50, 70, 80)
            d.ellipse([hx + dx * 18 - 6, hy + dy * 18 - 6, hx + dx * 18 + 6, hy + dy * 18 + 6], fill=col)
        d.text((hx - 18, hy + 45), "HAT", font=F_TINY, fill=MUTED)
        # keys flash
        for k in range(4):
            kx = x0 + 30 + k * 50
            ky = y0 + ch + 20
            on = (int(t * 6) % 4) == k
            d.rounded_rectangle([kx, ky, kx + 40, ky + 28], radius=6, fill=ACCENT if on else (35, 50, 58))
        d.rounded_rectangle([780, 180, 1220, 500], radius=16, fill=PANEL, outline=(40, 60, 70))
        d.text((810, 220), "Discrete HID events", font=F_H, fill=INK)
        d.text((810, 280), "Scroll / select / navigate", font=F_BODY, fill=MUTED)
        d.text((810, 320), "Works with mittens", font=F_BODY, fill=MUTED)
        d.text((810, 380), f"Encoder ticks: {int(t * 24)}", font=F_SMALL, fill=ACCENT)
        frames.append(img)
    return frames


def demo_tilt_cursor(seconds=5):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "C12 · Tilt-Cursor", "6-axis IMU maps wrist pitch/roll → on-screen cursor", i, n)
        x0, y0, cw, ch = draw_case(d, 520, 370, 220, 400, label="96 g — lightest design")
        pitch = math.sin(t * math.pi * 2) * 0.45
        roll = math.cos(t * math.pi * 2 * 0.7) * 0.35
        cx = x0 + cw // 2 + int(roll * 70)
        cy = y0 + ch // 2 + int(pitch * 90)
        d.ellipse([cx - 10, cy - 10, cx + 10, cy + 10], fill=ACCENT, outline=INK)
        # click pulse
        click = abs(math.sin(t * math.pi * 4)) > 0.92
        if click:
            d.ellipse([cx - 22, cy - 22, cx + 22, cy + 22], outline=WARN, width=2)

        # wrist diagram
        d.rounded_rectangle([860, 150, 1230, 540], radius=16, fill=PANEL, outline=(40, 60, 70))
        d.text((890, 180), "WRIST ORIENTATION", font=F_SMALL, fill=MUTED)
        wx, wy = 1045, 340
        d.ellipse([wx - 70, wy - 40, wx + 70, wy + 40], outline=ACCENT2, width=2)
        d.line([(wx, wy), (wx + 60 * math.sin(roll), wy + 50 * math.sin(pitch))], fill=ACCENT, width=4)
        d.text((890, 430), f"Pitch {pitch:+.2f}   Roll {roll:+.2f}", font=F_SMALL, fill=INK)
        d.text((890, 470), "Trigger = click" + ("  ■" if click else ""), font=F_SMALL, fill=WARN if click else MUTED)
        frames.append(img)
    return frames


def demo_oilfill(seconds=6):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "D15 · Oilfill-100", "Pressure compensation — no differential across the shell", i, n)
        # depth meter
        depth = t * 100
        d.rounded_rectangle([80, 100, 200, 620], radius=12, fill=PANEL, outline=(40, 60, 70))
        d.text((100, 120), "DEPTH", font=F_TINY, fill=MUTED)
        fill_h = int(480 * (depth / 100))
        d.rectangle([110, 160, 170, 640], fill=(15, 30, 38))
        d.rectangle([110, 640 - fill_h, 170, 640], fill=WATER)
        d.text((100, 650), f"{depth:.0f} m", font=F_SMALL, fill=ACCENT2)

        # housing with oil
        hx, hy, hw, hh = 420, 160, 320, 440
        d.rounded_rectangle([hx, hy, hx + hw, hy + hh], radius=20, fill=(25, 55, 65), outline=ACCENT2, width=2)
        # oil fill level
        d.rectangle([hx + 20, hy + 40, hx + hw - 20, hy + hh - 40], fill=(40, 90, 100))
        # phone immersed (dark)
        d.rounded_rectangle([hx + 70, hy + 100, hx + hw - 70, hy + hh - 80], radius=12, fill=(15, 20, 24))
        d.text((hx + 95, hy + 200), "PHONE", font=F_TINY, fill=MUTED)
        d.text((hx + 85, hy + 225), "(oil immersed)", font=F_TINY, fill=MUTED)
        # rolling diaphragm
        dy = hy + hh - 30 + int(6 * math.sin(t * 20))
        d.arc([hx + 40, dy - 20, hx + hw - 40, dy + 20], 0, 180, fill=WARN, width=3)
        d.text((hx + 90, hy + hh + 10), "rolling diaphragm", font=F_TINY, fill=WARN)

        # OLED readout separate
        d.rounded_rectangle([860, 200, 1180, 360], radius=12, fill=PHONE, outline=ACCENT)
        d.text((890, 230), "SEALED OLED", font=F_SMALL, fill=ACCENT)
        d.text((890, 275), f"Depth  {depth:.0f} m", font=F_H, fill=INK)
        d.text((890, 320), "P = P_oil  (ΔP ≈ 0)", font=F_SMALL, fill=ACCENT2)
        d.text((860, 400), "Keys still work — screen is companion panel", font=F_TINY, fill=MUTED)
        frames.append(img)
    return frames


def demo_floatline(seconds=5):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "D16 · Floatline", "Syntactic foam collar · +40 N reserve — dropped case returns", i, n)
        # water surface
        water_y = 280
        d.rectangle([0, water_y, W, H], fill=WATER)
        for x in range(0, W, 8):
            yy = water_y + int(4 * math.sin(x / 30 + t * 8))
            d.line([(x, yy), (x + 8, yy)], fill=ACCENT2)

        # case drops then floats up
        if t < 0.35:
            cy = lerp(120, 520, ease(t / 0.35))
        else:
            cy = lerp(520, 250, ease((t - 0.35) / 0.65))
        draw_case(d, 640, int(cy), 160, 260, aperture=True)
        # foam collar hint
        d.ellipse([640 - 110, int(cy) - 40, 640 + 110, int(cy) + 40], outline=WARN, width=3)
        d.text((520, 100), "DROP" if t < 0.35 else "POSITIVE BUOYANCY", font=F_BODY, fill=WARN)
        d.text((500, 640), "+40 N reserve through moderate current", font=F_TINY, fill=INK)
        frames.append(img)
    return frames


def demo_overview_reel(seconds=10):
    """Title + quick cuts of modalities."""
    frames = []
    n = int(seconds * FPS)
    chapters = [
        (0.00, 0.18, "title"),
        (0.18, 0.34, "force"),
        (0.34, 0.50, "hall"),
        (0.50, 0.66, "stylus"),
        (0.66, 0.82, "keys"),
        (0.82, 1.00, "end"),
    ]
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chapter = "title"
        for a, b, name in chapters:
            if a <= t < b:
                chapter = name
                local = (t - a) / (b - a)
                break
        else:
            chapter, local = "end", 1.0

        if chapter == "title":
            d.text((80, 240), "NEREID", font=font(72, True), fill=ACCENT)
            d.text((80, 330), "Interfaces that work underwater", font=F_H, fill=INK)
            d.text((80, 390), "18 designs · sealed phone · water-immune sensing", font=F_BODY, fill=MUTED)
        elif chapter == "force":
            chrome(d, "Force sensing", "Window as strain gauge", i, n)
            draw_case(d, 640, 380, 240, 420)
            draw_finger(d, 640 + int(40 * math.sin(local * 6)), 400, ease(abs(math.sin(local * 8))))
        elif chapter == "hall":
            chrome(d, "Hall-Glove", "Magnetic through neoprene", i, n)
            draw_case(d, 640, 380, 240, 420)
            draw_finger(d, 560 + int(local * 160), 360, 0.2, glove=True)
        elif chapter == "stylus":
            chrome(d, "Stylus-EMR", "Sub-millimeter underwater", i, n)
            draw_case(d, 640, 380, 260, 420)
            draw_stylus(d, 560 + int(local * 160), 380, 0.6)
        elif chapter == "keys":
            chrome(d, "Control surfaces", "When the window is only a viewport", i, n)
            draw_case(d, 520, 380, 220, 400)
            cx, cy = 760, 300
            ang = local * math.pi * 4
            d.ellipse([cx - 36, cy - 36, cx + 36, cy + 36], outline=ACCENT, width=3)
            d.line([(cx, cy), (cx + 28 * math.cos(ang), cy + 28 * math.sin(ang))], fill=INK, width=3)
        else:
            d.text((80, 280), "Open the catalog", font=F_H, fill=INK)
            d.text((80, 340), "localhost:4173  ·  present.html  ·  videos/", font=F_BODY, fill=ACCENT)
            d.text((80, 400), "Prototype CAD · STL/STEP · BOM · assembly", font=F_BODY, fill=MUTED)
        frames.append(img)
    return frames


def demo_lamb_wave(seconds=5):
    frames = []
    n = int(seconds * FPS)
    for i in range(n):
        t = i / n
        img, d = new_frame()
        chrome(d, "B7 · Lamb-Wave", "Edge piezos listen to guided waves in bare glass", i, n)
        x0, y0, cw, ch = draw_case(d, 500, 360, 280, 500, label="Nothing in the optical path")
        # piezos at edges
        piezos = [(x0 + cw // 2, y0 + 30), (x0 + cw - 30, y0 + ch // 2), (x0 + cw // 2, y0 + ch - 30), (x0 + 30, y0 + ch // 2)]
        for px, py in piezos:
            d.rectangle([px - 10, py - 10, px + 10, py + 10], fill=WARN, outline=INK)

        tap_t = (t * 2) % 1.0
        tx, ty = x0 + cw // 2 + int(40 * math.sin(t * 3)), y0 + ch // 2
        if tap_t < 0.15:
            draw_finger(d, tx, ty, 1.0)
        # ripples
        for k in range(4):
            age = tap_t - k * 0.08
            if 0 < age < 0.6:
                rr = int(20 + age * 180)
                d.ellipse([tx - rr, ty - rr, tx + rr, ty + rr], outline=ACCENT, width=2)
        waveform(d, 860, 220, 320, 120, t * 10, active=tap_t < 0.5)
        d.text((860, 380), "Time-of-arrival → XY", font=F_BODY, fill=INK)
        d.text((860, 430), "Wet plate model recalibrates each dive", font=F_TINY, fill=MUTED)
        frames.append(img)
    return frames


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [
        ("01-overview-reel.mp4", demo_overview_reel),
        ("02-A-force-touch.mp4", demo_force_touch),
        ("03-B5-hall-glove.mp4", demo_hall_glove),
        ("04-B6-stylus-emr.mp4", demo_stylus_emr),
        ("05-B7-lamb-wave.mp4", demo_lamb_wave),
        ("06-B8-resistive.mp4", demo_resistive),
        ("07-C10-crownpad.mp4", demo_crownpad),
        ("08-C12-tilt-cursor.mp4", demo_tilt_cursor),
        ("09-D15-oilfill-100.mp4", demo_oilfill),
        ("10-D16-floatline.mp4", demo_floatline),
    ]
    manifest = []
    for name, fn in jobs:
        print(f"Rendering {name} ...")
        frames = fn()
        path = OUT / name
        write_video(path, frames)
        manifest.append({"file": name, "seconds": round(len(frames) / FPS, 1), "frames": len(frames)})
    (OUT / "manifest.json").write_text(
        __import__("json").dumps({"fps": FPS, "size": [W, H], "videos": manifest}, indent=2),
        encoding="utf-8",
    )
    print(f"Done — {len(manifest)} videos in {OUT}")


if __name__ == "__main__":
    main()
