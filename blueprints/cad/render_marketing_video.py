#!/usr/bin/env python3
"""
Nereid marketing video: each product works + customers love it.
"""

from __future__ import annotations

import math
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos"
PROD = ROOT / "products"
LIFE = ROOT / "lifestyle"
W, H, FPS = 1280, 720, 30

BG = (7, 17, 22)
INK = (231, 240, 242)
MUTED = (170, 190, 198)
ACCENT = (46, 196, 168)
ACCENT2 = (126, 200, 227)

PRODUCTS = [
    ("A1", "Lightline Mg", "Tap the whole screen — even underwater", "lightline-mg", "Customers love the full-screen feel"),
    ("A2", "Carbonshell", "Stiff, light, dive-ready CFRP shell", "carbonshell", "Built for people who hate flex"),
    ("A3", "Skeleton", "Scratch the glass? Swap it in under a minute", "skeleton", "Field repair that feels like magic"),
    ("A4", "Titan-20", "Maximum abuse. Spinel. Titanium.", "titan-20", "When the drop is non-negotiable"),
    ("B5", "Hall-Glove", "Thick gloves. Cold water. Still works.", "hall-glove", "Finally — touch through neoprene"),
    ("B6", "Stylus-EMR", "Sub-mm precision for charts & notes", "stylus-emr", "Precision work, underwater"),
    ("B7", "Lamb-Wave", "Bare glass. Clearest photos & video", "lamb-wave", "Optics first — shooters love it"),
    ("B8", "Resistive-Hard", "Simple. Proven. Ships first.", "resistive-hard", "Reliable enough to trust on vacation"),
    ("B9", "Gap-Cap", "Weeks of standby for expeditions", "gap-cap", "Still alive when you need it"),
    ("C10", "Crownpad", "Physical keys water can’t confuse", "crownpad", "Mittens-friendly control they trust"),
    ("C11", "Tether-Puck", "Phone stays stowed. You keep swimming.", "tether-puck", "Hands free — still in control"),
    ("C12", "Tilt-Cursor", "96 g. Wrist tilt. One-handed swim.", "tilt-cursor", "Light enough to forget you’re wearing it"),
    ("C13", "Voice-PTT", "Both hands busy? Just talk.", "voice-ptt", "Loved by camera and tool operators"),
    ("D14", "Rolltop", "Packs flat into any dive bag", "rolltop", "Disappears until you need it"),
    ("D15", "Oilfill-100", "Real depth — pressure disappears", "oilfill-100", "Trust at depths others can’t go"),
    ("D16", "Floatline", "Drop it. It comes back.", "floatline", "Families stop panicking"),
    ("D17", "Chestboard", "Torso-mounted. Hands free.", "chestboard", "Mission-ready and always reachable"),
    ("D18", "Gauntlet", "Wrist nav + mechanical compass backup", "gauntlet", "Heading even if the phone dies"),
]


def font(size, bold=False):
    paths = (
        ["C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf"]
        if bold
        else ["C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf"]
    )
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


F_TITLE = font(48, True)
F_H = font(32, True)
F_BODY = font(22)
F_SMALL = font(16)
F_QUOTE = font(26, True)


def fit_cover(img: Image.Image, tw: int, th: int) -> Image.Image:
    img = img.convert("RGB")
    scale = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * scale), int(img.height * scale)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    left = (nw - tw) // 2
    top = (nh - th) // 2
    return img.crop((left, top, left + tw, top + th))


def fit_contain(img: Image.Image, tw: int, th: int, bg=BG) -> Image.Image:
    img = img.convert("RGB")
    scale = min(tw / img.width, th / img.height)
    nw, nh = max(1, int(img.width * scale)), max(1, int(img.height * scale))
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", (tw, th), bg)
    canvas.paste(img, ((tw - nw) // 2, (th - nh) // 2))
    return canvas


def darken(img: Image.Image, factor=0.55) -> Image.Image:
    return ImageEnhance.Brightness(img).enhance(factor)


def gradient_overlay(draw, y0=0, y1=220):
    for y in range(y0, y1):
        a = int(180 * (1 - (y - y0) / max(y1 - y0, 1)))
        draw.line([(0, y), (W, y)], fill=(5, 10, 14))


def find_product(slug: str) -> Path | None:
    matches = list(PROD.glob(f"product-*-{slug}.png"))
    return matches[0] if matches else None


def find_life(slug: str) -> Path | None:
    matches = list(LIFE.glob(f"life-*-{slug}.png"))
    return matches[0] if matches else None


def frame_title(t: float) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # soft aqua wash
    for y in range(H):
        c = int(10 + 8 * math.sin(y / 50 + t))
        d.line([(0, y), (W, y)], fill=(7, 17 + c // 2, 22 + c // 3))
    d.text((72, 250), "NEREID", font=F_TITLE, fill=ACCENT)
    d.text((72, 320), "Products people actually use underwater", font=F_H, fill=INK)
    d.text((72, 380), "How each one works — and why customers love them", font=F_BODY, fill=MUTED)
    return img


def frame_product_hero(pid, name, how, prod_path, t):
    base = Image.new("RGB", (W, H), BG)
    if prod_path and prod_path.exists():
        shot = fit_contain(Image.open(prod_path), 620, 620, BG)
        base.paste(shot, (40, 50))
    d = ImageDraw.Draw(base)
    d.text((720, 180), f"{pid}", font=F_SMALL, fill=ACCENT)
    d.text((720, 210), name, font=F_H, fill=INK)
    d.text((720, 280), "HOW IT WORKS", font=F_SMALL, fill=MUTED)
    # wrap how
    words = how.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if len(test) > 28:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    y = 320
    for line in lines:
        d.text((720, y), line, font=F_BODY, fill=ACCENT2)
        y += 34
    # pulse accent bar
    bar = int(200 + 80 * abs(math.sin(t * math.pi * 2)))
    d.rectangle([720, 480, 720 + bar, 486], fill=ACCENT)
    return base


def frame_customer_love(pid, name, love, life_path, t):
    if life_path and life_path.exists():
        img = fit_cover(Image.open(life_path), W, H)
        img = darken(img, 0.62)
    else:
        img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    # bottom gradient via dark rects
    for i in range(220):
        y = H - 220 + i
        d.line([(0, y), (W, y)], fill=(5, 10, 14))
    d.text((56, H - 190), f"{pid} · {name}", font=F_SMALL, fill=ACCENT)
    d.text((56, H - 155), f"“{love}”", font=F_QUOTE, fill=INK)
    d.text((56, H - 100), "Real-world use · customers who keep coming back", font=F_SMALL, fill=MUTED)
    # heart-ish accent
    pulse = 0.7 + 0.3 * abs(math.sin(t * math.pi * 4))
    r = int(10 * pulse)
    d.ellipse([W - 80 - r, 40 - r, W - 80 + r, 40 + r], fill=ACCENT)
    return img


def frame_howto_overlay(pid, name, how, life_path, t):
    """Lifestyle with how-it-works callout card."""
    if life_path and life_path.exists():
        img = fit_cover(Image.open(life_path), W, H)
        img = darken(img, 0.5)
    else:
        img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([48, 48, 620, 250], radius=16, fill=(8, 20, 28))
    d.text((72, 72), f"{pid} · HOW IT WORKS", font=F_SMALL, fill=ACCENT)
    words = how.split()
    lines, cur = [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if len(test) > 32:
            lines.append(cur)
            cur = w
        else:
            cur = test
    if cur:
        lines.append(cur)
    y = 115
    for line in lines[:4]:
        d.text((72, y), line, font=F_BODY, fill=INK)
        y += 36
    d.text((72, 620), name, font=F_H, fill=INK)
    return img


def frame_close(t):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    d.text((72, 250), "Eighteen ways to keep the phone.", font=F_H, fill=INK)
    d.text((72, 310), "One program: Nereid.", font=F_H, fill=ACCENT)
    d.text((72, 390), "Catalog · demos · CAD · product shots", font=F_BODY, fill=MUTED)
    d.text((72, 440), "localhost:4173", font=F_BODY, fill=ACCENT2)
    return img


def append_seconds(frames, maker, seconds):
    n = int(seconds * FPS)
    for i in range(n):
        frames.append(maker(i / max(n - 1, 1)))


def main():
    frames: list[Image.Image] = []
    print("Building marketing video...")

    append_seconds(frames, frame_title, 3.5)

    for pid, name, how, slug, love in PRODUCTS:
        prod = find_product(slug)
        life = find_life(slug)
        print(f"  {pid} prod={bool(prod)} life={bool(life)}")

        append_seconds(frames, lambda t, p=pid, n=name, h=how, pp=prod: frame_product_hero(p, n, h, pp, t), 2.2)
        append_seconds(frames, lambda t, p=pid, n=name, h=how, lp=life: frame_howto_overlay(p, n, h, lp, t), 2.4)
        append_seconds(frames, lambda t, p=pid, n=name, l=love, lp=life: frame_customer_love(p, n, l, lp, t), 2.6)

    append_seconds(frames, frame_close, 4.0)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "nereid-products-loved.mp4"
    writer = imageio.get_writer(
        str(path),
        fps=FPS,
        codec="libx264",
        quality=7,
        pixelformat="yuv420p",
        macro_block_size=1,
    )
    for fr in frames:
        writer.append_data(np.asarray(fr))
    writer.close()
    print(f"Wrote {path} — {len(frames)} frames ({len(frames)/FPS:.1f}s)")


if __name__ == "__main__":
    main()
