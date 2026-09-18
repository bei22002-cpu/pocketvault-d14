#!/usr/bin/env python3
"""Render one animated product film per Nereid design."""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "products"
PROD = ROOT / "products"
LIFE = ROOT / "lifestyle"
W, H, FPS = 1280, 720, 30
BG, PANEL = (6, 14, 18), (12, 26, 34)
INK, MUTED = (232, 240, 242), (150, 170, 178)
ACCENT, ACCENT2, WARN = (46, 196, 168), (126, 200, 227), (226, 179, 106)
COLORS = [
    (46, 196, 168), (126, 200, 227), (226, 179, 106), (180, 140, 220),
    (100, 180, 140), (220, 120, 100), (100, 140, 200), (200, 180, 100),
]

PRODUCTS = [
    ("A1", "Lightline Mg", "Load cell",
     ["Four corner load cells", "Moment balance -> X/Y", "Force sum -> click", "Works through water"],
     [("Mg frame + PEO", "frame"), ("Glass window", "glass"), ("Silicone diaphragm", "diaphragm"),
      ("Load cells ×4", "cells"), ("ADC + MCU PCB", "pcb"), ("Battery + BLE", "battery"),
      ("Latches + O-rings", "seals"), ("Purge valve", "valve")]),
    ("A2", "Carbonshell", "Load cell",
     ["CFRP monocoque shell", "Load cells on GF bosses", "RF window for BLE", "Max stiffness / gram"],
     [("CFRP shell", "frame"), ("Nylon bezel", "bezel"), ("PPS RF window", "rf"),
      ("Glass + diaphragm", "glass"), ("Load cells ×4", "cells"), ("Ti fasteners", "fasteners"),
      ("PCB + BLE", "pcb")]),
    ("A3", "Skeleton", "Load cell",
     ["Rib cage holds phone", "Window is a cartridge", "Two captive screws", "Field swap < 1 minute"],
     [("7075 rib cage", "ribs"), ("PPA overmold", "grip"), ("Window cartridge", "cartridge"),
      ("Load cells in cart.", "cells"), ("Double O-ring", "seals"), ("Captive screws ×2", "fasteners"),
      ("Battery + BLE", "battery")]),
    ("A4", "Titan-20", "Load cell",
     ["Ti-6Al-4V housing", "2.2 mm spinel window", "Hi-preload cells", "Abuse-first rating"],
     [("Ti bezel / back", "frame"), ("Spinel window", "glass"), ("Hi-preload cells", "cells"),
      ("Double O-ring seam", "seals"), ("ADC PCB", "pcb"), ("Battery + BLE", "battery")]),
    ("B5", "Hall-Glove", "Magnetic",
     ["8×16 Hall grid", "Reads fingertip magnet", "Water is non-magnetic", "Gloves required"],
     [("CFRP shell", "frame"), ("Fixed glass", "glass"), ("Hall array flex", "grid"),
      ("Sense PCB", "pcb"), ("Neoprene glove", "glove"), ("N42 fingertip magnet", "magnet")]),
    ("B6", "Stylus-EMR", "Resonant",
     ["EMR coil grid", "Passive LC stylus", "Hover + pressure", "Sub-mm precision"],
     [("Mg shell", "frame"), ("Fixed glass", "glass"), ("EMR coil + ASIC", "grid"),
      ("Passive stylus", "stylus"), ("Coiled tether", "tether"), ("Stow channel", "channel")]),
    ("B7", "Lamb-Wave", "Acoustic",
     ["Bare glass plate", "Edge piezos listen", "Tap -> guided waves", "Clearest aperture"],
     [("CFRP shell", "frame"), ("Bare glass", "glass"), ("Piezos ×4", "piezo"),
      ("DSP board", "pcb"), ("Isolation mounts", "seals")]),
    ("B8", "Resistive-Hard", "Resistive",
     ["ITO layers touch", "Water cannot fake it", "Glove / nail / stylus", "Ship-first reliability"],
     [("Mg shell", "frame"), ("Hard-coat PC lens", "glass"), ("Resistive film", "film"),
      ("Sense IC", "pcb"), ("Battery + BLE", "battery"), ("Seals + latches", "seals")]),
    ("B9", "Gap-Cap", "Cap. gap",
     ["Dry-side electrode gap", "Micron glass deflection", "µA standby draw", "Weeks of expedition life"],
     [("Mg shell", "frame"), ("Glass + short diaphragm", "glass"), ("Electrode backplate", "plate"),
      ("Cap-sense IC", "pcb"), ("Small LiPo", "battery")]),
    ("C10", "Crownpad", "Keys only",
     ["Rotary encoder", "5-way hat + keys", "Window is viewport only", "Fewest failure modes"],
     [("PPA shell", "frame"), ("PC viewport", "glass"), ("Rotary crown", "crown"),
      ("Hat switch", "hat"), ("Programmable keys", "keys"), ("NVIS LEDs", "leds")]),
    ("C11", "Tether-Puck", "Wired puck",
     ["Phone stays sealed", "Thumbstick on tether", "Wired = no BLE loss", "One-handed swim control"],
     [("Dry case shell", "frame"), ("PC window", "glass"), ("Bulkhead gland", "valve"),
      ("Puck body", "puck"), ("Thumbstick + buttons", "stick"), ("Coiled marine cable", "tether")]),
    ("C12", "Tilt-Cursor", "IMU",
     ["6-axis IMU", "Wrist pitch/roll -> cursor", "Trigger = click", "Lightest in catalog"],
     [("Thin PPA shell", "frame"), ("Thin PC window", "glass"), ("IMU board", "pcb"),
      ("Index trigger", "keys"), ("Battery + BLE", "battery")]),
    ("C13", "Voice-PTT", "Voice",
     ["Bone-conduction PTT", "Screen is display-only", "Both hands free", "Works wet or dry"],
     [("PPA shell", "frame"), ("PC window", "glass"), ("PTT switch", "keys"),
      ("Audio codec", "pcb"), ("Bone transducer", "bone"), ("Mask-strap clip", "clip")]),
    ("D14", "Rolltop", "Load cell",
     ["Fabric body packs flat", "Only window is rigid", "Load-cell bezel", "Dive-bag friendly"],
     [("Aramid / TPU body", "fabric"), ("Rigid bezel", "bezel"), ("Glass + load cells", "glass"),
      ("Roll clamp + buckles", "buckle"), ("Battery + BLE", "battery")]),
    ("D15", "Oilfill-100", "Keys",
     ["Oil equalizes pressure", "Phone immersed", "Separate OLED readout", "True 100 m depth"],
     [("Thin PPA shell", "frame"), ("Rolling diaphragm", "diaphragm"), ("Silicone oil fill", "oil"),
      ("Sealed OLED + MCU", "oled"), ("Encoder + keys", "keys"), ("Bleed / fill valve", "valve")]),
    ("D16", "Floatline", "Load cell",
     ["A1 core unchanged", "Syntactic foam collar", "+40 N buoyancy", "Drop it — it returns"],
     [("A1 Mg core", "frame"), ("Glass + cells", "glass"), ("Foam collar", "foam"), ("Electronics", "pcb")]),
    ("D17", "Chestboard", "Keys",
     ["Landscape torso mount", "Six sealed dome keys", "MOLLE plate carrier", "Hands stay free"],
     [("Landscape PPA shell", "frame"), ("Large PC window", "glass"), ("Dome keys ×6", "keys"),
      ("MOLLE plate", "molle"), ("Battery + BLE", "battery")]),
    ("D18", "Gauntlet", "Crown",
     ["Forearm mount", "Cropped 38 mm window", "Side crown + keys", "Mechanical compass backup"],
     [("PPA shell + lugs", "frame"), ("38×38 PC window", "glass"), ("Side crown", "crown"),
      ("Keys ×2", "keys"), ("Liquid compass", "compass"), ("Forearm strap", "strap")]),
]


def font(size, bold=False):
    for p in (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
        if bold else
        ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    ):
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


FT, FH, FB, FS, FTINY = font(44, True), font(28, True), font(20), font(15), font(13)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def lerp(a, b, t):
    return a + (b - a) * t


def find_img(folder, pid, prefix):
    hits = list(folder.glob(f"{prefix}-{pid}-*.png"))
    return hits[0] if hits else None


def fit_cover(img, tw, th):
    img = img.convert("RGB")
    s = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * s), int(img.height * s)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    l, t = (nw - tw) // 2, (nh - th) // 2
    return img.crop((l, t, l + tw, t + th))


def fit_contain(img, tw, th, bg=BG):
    img = img.convert("RGB")
    s = min(tw / img.width, th / img.height)
    nw, nh = max(1, int(img.width * s)), max(1, int(img.height * s))
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    c = Image.new("RGB", (tw, th), bg)
    c.paste(img, ((tw - nw) // 2, (th - nh) // 2))
    return c


def darken(img, f=0.55):
    return ImageEnhance.Brightness(img).enhance(f)


def canvas():
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    for y in range(0, H, 3):
        a = int(6 + 5 * math.sin(y / 45.0))
        d.line([(0, y), (W, y)], fill=(BG[0], BG[1] + a, BG[2] + a))
    return img, d


def chrome(d, pid, name, stage):
    d.rectangle([0, 0, W, 52], fill=(4, 10, 14))
    d.text((24, 14), "NEREID", font=FB, fill=ACCENT)
    d.text((120, 16), f"{pid}  ·  {name}", font=FB, fill=INK)
    d.text((W - 300, 16), stage, font=FS, fill=MUTED)
    d.rectangle([0, H - 6, W, H], fill=(20, 35, 42))


def draw_part(d, kind, cx, cy, scale, color):
    s, c = scale, color
    if kind in ("frame", "fabric", "ribs", "grip", "cartridge"):
        d.rounded_rectangle([cx - 70 * s, cy - 120 * s, cx + 70 * s, cy + 120 * s],
                            radius=int(14 * s), outline=c, width=3)
        if kind == "ribs":
            d.line([(cx - 50 * s, cy), (cx + 50 * s, cy)], fill=c, width=2)
            d.line([(cx, cy - 90 * s), (cx, cy + 90 * s)], fill=c, width=2)
    elif kind == "glass":
        d.rounded_rectangle([cx - 55 * s, cy - 95 * s, cx + 55 * s, cy + 95 * s],
                            radius=int(10 * s), fill=(30, 50, 60), outline=c, width=2)
    elif kind == "diaphragm":
        d.ellipse([cx - 50 * s, cy - 20 * s, cx + 50 * s, cy + 20 * s], outline=c, width=2)
    elif kind == "cells":
        for dx, dy in [(-40, -70), (40, -70), (-40, 70), (40, 70)]:
            d.rectangle([cx + dx * s - 8, cy + dy * s - 8, cx + dx * s + 8, cy + dy * s + 8], fill=c)
    elif kind == "pcb":
        d.rounded_rectangle([cx - 40 * s, cy - 25 * s, cx + 40 * s, cy + 25 * s], radius=4, fill=c)
    elif kind == "battery":
        d.rounded_rectangle([cx - 35 * s, cy - 18 * s, cx + 35 * s, cy + 18 * s], radius=6, outline=c, width=2)
    elif kind == "seals":
        d.ellipse([cx - 45 * s, cy - 70 * s, cx + 45 * s, cy + 70 * s], outline=c, width=2)
    elif kind == "valve":
        d.ellipse([cx - 14 * s, cy - 14 * s, cx + 14 * s, cy + 14 * s], fill=c)
    elif kind == "bezel":
        d.rounded_rectangle([cx - 65 * s, cy - 105 * s, cx + 65 * s, cy + 105 * s], radius=12, outline=c, width=4)
    elif kind == "rf":
        d.rectangle([cx - 30 * s, cy - 8 * s, cx + 30 * s, cy + 8 * s], fill=c)
    elif kind == "fasteners":
        for i in range(4):
            ang = i * math.pi / 2
            x, y = cx + 50 * s * math.cos(ang), cy + 50 * s * math.sin(ang)
            d.ellipse([x - 5, y - 5, x + 5, y + 5], fill=c)
    elif kind == "grid":
        for r in range(-2, 3):
            for col in range(-2, 3):
                d.ellipse([cx + col * 16 * s - 3, cy + r * 20 * s - 3,
                           cx + col * 16 * s + 3, cy + r * 20 * s + 3], fill=c)
    elif kind == "glove":
        d.ellipse([cx - 25 * s, cy - 40 * s, cx + 35 * s, cy + 50 * s], outline=c, width=3)
        d.ellipse([cx + 20 * s, cy - 50 * s, cx + 40 * s, cy - 25 * s], fill=(200, 40, 40))
    elif kind == "magnet":
        d.ellipse([cx - 10 * s, cy - 10 * s, cx + 10 * s, cy + 10 * s], fill=(200, 40, 40))
    elif kind == "stylus":
        d.polygon([(cx, cy + 40 * s), (cx - 8 * s, cy - 50 * s), (cx + 8 * s, cy - 50 * s)], fill=c)
    elif kind == "tether":
        pts = [(cx + int(30 * math.sin(i / 3) * s), cy - 60 * s + i * 8 * s) for i in range(16)]
        d.line(pts, fill=c, width=2)
    elif kind == "channel":
        d.rounded_rectangle([cx - 12 * s, cy - 80 * s, cx + 12 * s, cy + 80 * s], radius=6, outline=c, width=2)
    elif kind == "piezo":
        for dx, dy in [(0, -90), (55, 0), (0, 90), (-55, 0)]:
            d.rectangle([cx + dx * s - 8, cy + dy * s - 8, cx + dx * s + 8, cy + dy * s + 8], fill=WARN)
    elif kind == "film":
        d.rounded_rectangle([cx - 50 * s, cy - 85 * s, cx + 50 * s, cy + 85 * s], radius=8, outline=c, width=1)
        d.rounded_rectangle([cx - 45 * s, cy - 80 * s, cx + 45 * s, cy + 80 * s], radius=6, outline=ACCENT2, width=1)
    elif kind == "plate":
        d.rectangle([cx - 50 * s, cy - 80 * s, cx + 50 * s, cy + 80 * s], outline=c, width=2)
    elif kind == "crown":
        d.ellipse([cx - 22 * s, cy - 22 * s, cx + 22 * s, cy + 22 * s], outline=c, width=3)
        d.line([(cx, cy), (cx + 18 * s, cy)], fill=INK, width=2)
    elif kind == "hat":
        d.ellipse([cx - 18 * s, cy - 18 * s, cx + 18 * s, cy + 18 * s], outline=c, width=2)
    elif kind == "keys":
        for i in range(4):
            d.rounded_rectangle([cx - 40 * s + i * 22 * s, cy - 10 * s,
                                 cx - 28 * s + i * 22 * s, cy + 10 * s], radius=3, fill=c)
    elif kind == "leds":
        for i in range(3):
            d.ellipse([cx - 20 + i * 20 - 4, cy - 4, cx - 20 + i * 20 + 4, cy + 4], fill=ACCENT)
    elif kind == "puck":
        d.ellipse([cx - 40 * s, cy - 50 * s, cx + 40 * s, cy + 50 * s], outline=c, width=3)
    elif kind == "stick":
        d.ellipse([cx - 12 * s, cy - 12 * s, cx + 12 * s, cy + 12 * s], fill=c)
    elif kind == "bone":
        d.rounded_rectangle([cx - 30 * s, cy - 12 * s, cx + 30 * s, cy + 12 * s], radius=8, fill=c)
    elif kind == "clip":
        d.arc([cx - 20 * s, cy - 20 * s, cx + 20 * s, cy + 20 * s], 200, 340, fill=c, width=3)
    elif kind == "buckle":
        d.rounded_rectangle([cx - 25 * s, cy - 12 * s, cx + 25 * s, cy + 12 * s], radius=4, outline=c, width=2)
    elif kind == "oil":
        d.ellipse([cx - 40 * s, cy - 50 * s, cx + 40 * s, cy + 50 * s], fill=(40, 90, 100), outline=c)
    elif kind == "oled":
        d.rounded_rectangle([cx - 35 * s, cy - 22 * s, cx + 35 * s, cy + 22 * s], radius=4, fill=c)
    elif kind == "foam":
        d.ellipse([cx - 90 * s, cy - 50 * s, cx + 90 * s, cy + 50 * s], outline=WARN, width=4)
    elif kind == "molle":
        d.rectangle([cx - 50 * s, cy - 70 * s, cx + 50 * s, cy + 70 * s], outline=c, width=2)
        for yy in range(-2, 3):
            d.line([(cx - 40 * s, cy + yy * 20 * s), (cx + 40 * s, cy + yy * 20 * s)], fill=c, width=1)
    elif kind == "compass":
        d.ellipse([cx - 20 * s, cy - 20 * s, cx + 20 * s, cy + 20 * s], outline=WARN, width=2)
        d.line([(cx, cy), (cx, cy - 14 * s)], fill=(200, 40, 40), width=2)
    elif kind == "strap":
        d.arc([cx - 60 * s, cy - 30 * s, cx + 60 * s, cy + 30 * s], 20, 160, fill=c, width=4)
    else:
        d.ellipse([cx - 20 * s, cy - 20 * s, cx + 20 * s, cy + 20 * s], outline=c, width=2)


def title_frames(pid, name, sensing, n=40):
    out = []
    for i in range(n):
        t = ease(i / max(n - 1, 1))
        img, d = canvas()
        chrome(d, pid, name, "PRODUCT FILM")
        d.text((72, 250), pid, font=FS, fill=ACCENT)
        col = tuple(int(INK[j] * t + BG[j] * (1 - t)) for j in range(3))
        d.text((72, 290), name, font=FT, fill=col)
        d.text((72, 370), f"Sensing · {sensing}", font=FB, fill=MUTED)
        d.text((72, 420), "Piece-by-piece build  ->  how it works", font=FS, fill=ACCENT2)
        out.append(img)
    return out


def explode_frames(pid, name, parts, n_per=20, hold=12):
    out = []
    n = len(parts)
    home = [(640, 340 - (n / 2 - i) * 8) for i in range(n)]
    exploded = []
    for i in range(n):
        ang = -0.9 + 1.8 * (i / max(n - 1, 1))
        exploded.append((640 + int(math.sin(ang) * 280), 340 + int((i - n / 2) * 55)))

    for _ in range(15):
        img, d = canvas()
        chrome(d, pid, name, "EXPLODED BUILD")
        d.text((72, 100), "Parts assemble one by one", font=FS, fill=MUTED)
        out.append(img)

    placed = []
    for pi, (label, kind) in enumerate(parts):
        color = COLORS[pi % len(COLORS)]
        for i in range(n_per):
            t = ease(i / max(n_per - 1, 1))
            img, d = canvas()
            chrome(d, pid, name, f"PART {pi + 1}/{n}")
            for j, (_lab, knd) in enumerate(placed):
                hx, hy = home[j]
                draw_part(d, knd, hx, hy, 0.85, COLORS[j % len(COLORS)])
            sx, sy = exploded[pi]
            hx, hy = home[pi]
            draw_part(d, kind, lerp(sx, hx, t), lerp(sy, hy, t), lerp(1.15, 0.85, t), color)
            d.rounded_rectangle([40, H - 120, 540, H - 36], radius=10, fill=PANEL)
            d.text((60, H - 100), f"{pi + 1}. {label}", font=FH, fill=INK)
            d.text((60, H - 65), kind.upper(), font=FTINY, fill=ACCENT)
            d.rounded_rectangle([W - 360, 80, W - 40, 80 + min(n, 8) * 28 + 24], radius=10, fill=PANEL)
            for j, (lab, _) in enumerate(parts[:8]):
                mark = "●" if j <= pi else "○"
                d.text((W - 340, 95 + j * 28), f"{mark}  {lab[:28]}", font=FTINY,
                       fill=ACCENT if j <= pi else MUTED)
            out.append(img)
        placed.append((label, kind))
        for _ in range(max(1, hold // 3)):
            out.append(out[-1].copy())

    for _ in range(hold):
        img, d = canvas()
        chrome(d, pid, name, "ASSEMBLED")
        for j, (_lab, knd) in enumerate(parts):
            hx, hy = home[j]
            draw_part(d, knd, hx, hy, 0.9, COLORS[j % len(COLORS)])
        d.text((72, 100), "Full stack locked", font=FH, fill=ACCENT)
        out.append(img)
    return out


def how_frames(pid, name, sensing, lines, n=85):
    out = []
    for i in range(n):
        t = i / max(n - 1, 1)
        img, d = canvas()
        chrome(d, pid, name, "HOW IT WORKS")
        d.text((72, 100), sensing.upper(), font=FS, fill=ACCENT)
        d.text((72, 140), "Signal path", font=FH, fill=INK)
        reveal = t * len(lines)
        for li, line in enumerate(lines):
            if li <= reveal:
                local = ease(min(1.0, reveal - li))
                col = tuple(int(INK[j] * local + BG[j] * (1 - local)) for j in range(3))
                y = 210 + li * 55
                d.ellipse([72, y + 8, 86, y + 22], fill=ACCENT)
                d.text((100, y), line, font=FB, fill=col)

        cx, cy = 980, 360
        d.rounded_rectangle([820, 160, 1220, 560], radius=16, fill=PANEL)
        s = sensing.lower()
        if "load" in s:
            press = abs(math.sin(t * math.pi * 3))
            for dx, dy in [(-60, -80), (60, -80), (-40, 80), (40, 80)]:
                d.rectangle([cx + dx - 8, cy + dy - 8, cx + dx + 8, cy + dy + 8], fill=ACCENT)
            d.ellipse([cx - 16, cy - 16 + int(10 * press), cx + 16, cy + 16 + int(10 * press)], fill=(210, 170, 140))
            d.text((880, 500), "CLICK" if press > 0.7 else "PRESS", font=FS, fill=WARN)
        elif "magnet" in s:
            ang = t * math.pi * 4
            d.ellipse([cx - 70, cy - 90, cx + 70, cy + 90], outline=ACCENT2, width=2)
            mx, my = cx + int(50 * math.cos(ang)), cy + int(60 * math.sin(ang))
            d.ellipse([mx - 10, my - 10, mx + 10, my + 10], fill=(200, 40, 40))
            d.text((880, 500), "HALL FIELD", font=FS, fill=ACCENT)
        elif "reson" in s:
            d.line([(880, 280), (1160, 280 + int(40 * math.sin(t * 20)))], fill=ACCENT, width=3)
            d.polygon([(1100, 400), (1090, 300), (1110, 300)], fill=INK)
            d.text((880, 500), "EMR TRACK", font=FS, fill=ACCENT2)
        elif "acoustic" in s:
            for k in range(4):
                rr = int(20 + ((t * 4 + k * 0.2) % 1) * 100)
                d.ellipse([cx - rr, cy - rr, cx + rr, cy + rr], outline=ACCENT, width=2)
            d.text((880, 500), "LAMB WAVE", font=FS, fill=WARN)
        elif "resist" in s:
            gap = 20 - int(14 * abs(math.sin(t * math.pi * 2)))
            d.rectangle([900, 300, 1140, 320], fill=ACCENT2)
            d.rectangle([900, 320 + gap, 1140, 340 + gap], fill=ACCENT)
            d.text((880, 500), "CONTACT" if gap < 10 else "OPEN", font=FS, fill=WARN)
        elif "cap" in s:
            defl = int(8 * abs(math.sin(t * math.pi * 2)))
            d.rectangle([920, 280, 1120, 300], fill=ACCENT2)
            d.arc([920, 300 - defl, 1120, 340 - defl], 0, 180, fill=ACCENT, width=3)
            d.text((880, 500), "GAP CHANGE", font=FS, fill=ACCENT)
        elif "imu" in s:
            pitch = math.sin(t * math.pi * 2) * 40
            d.ellipse([cx - 10, cy - 10 + int(pitch), cx + 10, cy + 10 + int(pitch)], fill=ACCENT)
            d.text((880, 500), "TILT -> CURSOR", font=FS, fill=ACCENT)
        elif "voice" in s:
            for k in range(5):
                hgt = int(20 + 30 * abs(math.sin(t * 10 + k)))
                d.rectangle([920 + k * 30, 400 - hgt, 935 + k * 30, 400], fill=ACCENT)
            d.text((880, 500), "PTT AUDIO", font=FS, fill=ACCENT)
        elif "puck" in s or "wired" in s:
            d.ellipse([cx - 50, cy - 60, cx + 50, cy + 60], outline=ACCENT, width=3)
            d.ellipse([cx - 12, cy - 20, cx + 12, cy + 4], fill=ACCENT2)
            d.text((880, 500), "WIRED CURSOR", font=FS, fill=ACCENT2)
        elif "key" in s or "crown" in s:
            ang = t * math.pi * 4
            d.ellipse([cx - 40, cy - 40, cx + 40, cy + 40], outline=ACCENT, width=3)
            d.line([(cx, cy), (cx + 32 * math.cos(ang), cy + 32 * math.sin(ang))], fill=INK, width=3)
            d.text((880, 500), "DISCRETE HID", font=FS, fill=ACCENT)
        else:
            d.text((900, 340), sensing, font=FB, fill=INK)
        out.append(img)
    return out


def product_frames(pid, name, path, n=45):
    out = []
    for i in range(n):
        t = ease(i / max(n - 1, 1))
        img, d = canvas()
        chrome(d, pid, name, "COMPLETE PRODUCT")
        if path and path.exists():
            shot = fit_contain(Image.open(path), int(lerp(520, 640, t)), int(lerp(520, 640, t)))
            img.paste(shot, ((W - shot.width) // 2, 70))
        d.text((72, H - 70), "Design complete — print, assemble, pressure-test", font=FS, fill=MUTED)
        out.append(img)
    return out


def in_use_frames(pid, name, path, n=50):
    out = []
    for i in range(n):
        t = ease(i / max(n - 1, 1))
        if path and path.exists():
            base = darken(fit_cover(Image.open(path), W, H), 0.58 + 0.1 * t)
        else:
            base = Image.new("RGB", (W, H), BG)
        d = ImageDraw.Draw(base)
        chrome(d, pid, name, "IN USE")
        for j in range(150):
            d.line([(0, H - 150 + j), (W, H - 150 + j)], fill=(5, 10, 14))
        d.text((56, H - 110), f"{pid} · {name}", font=FH, fill=INK)
        d.text((56, H - 70), "Working the way it was designed to", font=FS, fill=ACCENT)
        out.append(base)
    return out


def end_frames(pid, name, n=30):
    out = []
    for _ in range(n):
        img, d = canvas()
        chrome(d, pid, name, "END")
        d.text((72, 280), f"{pid} film complete", font=FH, fill=INK)
        d.text((72, 340), "Catalog · CAD · Print guide · Demos", font=FB, fill=MUTED)
        out.append(img)
    return out


def render_one(pid, name, sensing, how, parts):
    prod = find_img(PROD, pid, "product")
    life = find_img(LIFE, pid, "life")
    frames = []
    frames += title_frames(pid, name, sensing)
    frames += explode_frames(pid, name, parts)
    frames += how_frames(pid, name, sensing, how)
    frames += product_frames(pid, name, prod)
    frames += in_use_frames(pid, name, life)
    frames += end_frames(pid, name)

    OUT.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    path = OUT / f"{pid}-{slug}.mp4"
    writer = imageio.get_writer(
        str(path), fps=FPS, codec="libx264", quality=7,
        pixelformat="yuv420p", macro_block_size=1,
    )
    for fr in frames:
        writer.append_data(np.asarray(fr))
    writer.close()
    sec = len(frames) / FPS
    print(f"  {pid} -> {path.name} ({len(frames)} frames, {sec:.1f}s)")
    return {"id": pid, "name": name, "file": f"videos/products/{path.name}", "seconds": round(sec, 1)}


def main():
    print(f"Rendering {len(PRODUCTS)} product films -> {OUT}")
    manifest = [render_one(*p) for p in PRODUCTS]
    (OUT / "manifest.json").write_text(json.dumps({"videos": manifest}, indent=2), encoding="utf-8")
    print(f"Done — {len(manifest)} videos")


if __name__ == "__main__":
    main()
