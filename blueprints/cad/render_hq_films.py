#!/usr/bin/env python3
"""
Nereid HQ cinematic product films.
Photoreal keyframes + Ken Burns + crossfades + grade. 1280x720.
"""

from __future__ import annotations

import json
import math
import re
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "videos" / "products"
HQ = ROOT / "hq"
PROD = ROOT / "products"
LIFE = ROOT / "lifestyle"
W, H, FPS = 1280, 720, 30

PRODUCTS = [
    ("A1", "Lightline Mg", "Force-sensed full aperture", "Four load cells turn the glass into a strain gauge."),
    ("A2", "Carbonshell", "CFRP stiffness per gram", "Carbon shell, RF window, titanium fasteners."),
    ("A3", "Skeleton", "Field-replaceable cartridge", "Scratch the glass. Swap it with a coin."),
    ("A4", "Titan-20", "Maximum abuse rating", "Titanium and spinel when the drop isn't negotiable."),
    ("B5", "Hall-Glove", "Magnetic through neoprene", "Water is non-magnetic. Thick gloves still work."),
    ("B6", "Stylus-EMR", "Sub-millimeter underwater", "Hover, pressure, and precision chartwork."),
    ("B7", "Lamb-Wave", "Clearest optical path", "Bare glass. Edge piezos listen to every tap."),
    ("B8", "Resistive-Hard", "Ship-first reliability", "Physical contact. Water cannot fake a press."),
    ("B9", "Gap-Cap", "Expedition battery life", "Dry-side capacitance. Weeks of standby."),
    ("C10", "Crownpad", "Controls water can't confuse", "Crown, hat, keys. Viewport only."),
    ("C11", "Tether-Puck", "Phone stays stowed", "Wired puck. Swim free, stay in control."),
    ("C12", "Tilt-Cursor", "Lightest in the catalog", "Wrist tilt drives the cursor. 96 grams."),
    ("C13", "Voice-PTT", "Both hands free", "Bone conduction. Speak while you work."),
    ("D14", "Rolltop", "Packs flat", "Soft body. Rigid window. Dive-bag ready."),
    ("D15", "Oilfill-100", "Real depth", "Oil equalizes pressure. True 100 meters."),
    ("D16", "Floatline", "It comes back", "Syntactic foam. Drop it. It returns."),
    ("D17", "Chestboard", "Torso-mounted", "MOLLE keys. Hands stay free."),
    ("D18", "Gauntlet", "Wrist navigation", "Crown control plus a mechanical compass."),
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


FT, FH, FB, FS = font(48, True), font(28, True), font(22), font(16)


def ease(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def find(folder, pattern):
    hits = list(folder.glob(pattern))
    return hits[0] if hits else None


def load_rgb(path):
    return Image.open(path).convert("RGB")


def fit_cover(img, tw, th):
    s = max(tw / img.width, th / img.height)
    nw, nh = int(img.width * s + 0.5), int(img.height * s + 0.5)
    img = img.resize((nw, nh), Image.Resampling.LANCZOS)
    l, t = (nw - tw) // 2, (nh - th) // 2
    return img.crop((l, t, l + tw, t + th))


# Precompute vignette once
_yy, _xx = np.mgrid[0:H, 0:W]
_cx, _cy = W / 2.0, H / 2.0
_r = np.sqrt(((_xx - _cx) / _cx) ** 2 + ((_yy - _cy) / _cy) ** 2)
_VIGNETTE = (1 - 0.32 * np.clip((_r - 0.35) / 0.9, 0, 1))[..., None].astype(np.float32)


def grade_once(img):
    """Apply cinematic grade + vignette once before Ken Burns."""
    img = ImageEnhance.Contrast(img).enhance(1.08)
    img = ImageEnhance.Color(img).enhance(1.05)
    img = ImageEnhance.Sharpness(img).enhance(1.1)
    arr = np.asarray(img).astype(np.float32)
    lum = arr.mean(axis=2, keepdims=True)
    shadow = np.clip((90 - lum) / 90, 0, 1)
    arr[..., 1] += shadow[..., 0] * 4
    arr[..., 2] += shadow[..., 0] * 6
    # Soft vignette baked at canvas size after fit — applied in ken_burns crop path
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def apply_vignette(frame):
    arr = np.asarray(frame).astype(np.float32) * _VIGNETTE
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def ken_burns(img, n, zoom_from=1.0, zoom_to=1.12, pan=(0, 0)):
    """Slow push-in. Grade once; bilinear crop/resize per frame."""
    graded = grade_once(img)
    base = fit_cover(graded, int(W * 1.18), int(H * 1.18))
    frames = []
    for i in range(n):
        t = ease(i / max(n - 1, 1))
        z = zoom_from + (zoom_to - zoom_from) * t
        cw, ch = int(W / z), int(H / z)
        max_x = max(0, base.width - cw)
        max_y = max(0, base.height - ch)
        ox = int((0.5 + pan[0] * t) * max_x)
        oy = int((0.5 + pan[1] * t) * max_y)
        ox = max(0, min(max_x, ox))
        oy = max(0, min(max_y, oy))
        crop = base.crop((ox, oy, ox + cw, oy + ch)).resize((W, H), Image.Resampling.BILINEAR)
        frames.append(apply_vignette(crop))
    return frames


def solid(color=(6, 12, 16)):
    return Image.new("RGB", (W, H), color)


_TITLE_GRAD = None


def _title_grad():
    global _TITLE_GRAD
    if _TITLE_GRAD is None:
        grad = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        g = ImageDraw.Draw(grad)
        for y in range(H - 280, H):
            a = int(200 * ((y - (H - 280)) / 280))
            g.line([(0, y), (W, y)], fill=(0, 0, 0, a))
        _TITLE_GRAD = grad
    return _TITLE_GRAD


def overlay_title(img, pid, name, line, fade=1.0):
    out = img.convert("RGBA")
    if fade >= 0.99:
        out = Image.alpha_composite(out, _title_grad())
    else:
        g = _title_grad().copy()
        g.putalpha(g.split()[-1].point(lambda a: int(a * fade)))
        out = Image.alpha_composite(out, g)
    out = out.convert("RGB")
    d = ImageDraw.Draw(out)
    a_col = tuple(int(c * fade) for c in (46, 196, 168))
    ink = tuple(int(c * fade + 6 * (1 - fade)) for c in (240, 245, 247))
    muted = tuple(int(c * fade + 6 * (1 - fade)) for c in (170, 185, 190))
    d.text((72, 48), "NEREID", font=FS, fill=a_col)
    d.text((72, H - 200), f"{pid}", font=FS, fill=a_col)
    d.text((72, H - 165), name, font=FT, fill=ink)
    d.text((72, H - 95), line, font=FB, fill=muted)
    return out


def overlay_caption(img, caption, fade=1.0):
    out = img.copy()
    box = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    b = ImageDraw.Draw(box)
    alpha = int(170 * fade)
    b.rounded_rectangle([56, H - 150, min(980, 56 + 18 * len(caption)), H - 48], radius=14, fill=(8, 18, 24, alpha))
    out = Image.alpha_composite(out.convert("RGBA"), box).convert("RGB")
    d = ImageDraw.Draw(out)
    col = tuple(int(c * fade + 6 * (1 - fade)) for c in (230, 238, 240))
    d.text((80, H - 120), caption, font=FH, fill=col)
    return out


def crossfade(a_frames, b_frames, overlap=10):
    if not a_frames:
        return list(b_frames)
    if not b_frames:
        return list(a_frames)
    out = a_frames[:-overlap] if len(a_frames) > overlap else []
    n = min(overlap, len(a_frames), len(b_frames))
    for i in range(n):
        t = ease((i + 1) / n)
        aa = np.asarray(a_frames[-(n - i)]).astype(np.float32)
        bb = np.asarray(b_frames[i]).astype(np.float32)
        mix = (aa * (1 - t) + bb * t).astype(np.uint8)
        out.append(Image.fromarray(mix))
    out.extend(b_frames[n:])
    return out


def fade_in(frames, n=8):
    out = []
    for i, fr in enumerate(frames):
        if i < n:
            t = ease((i + 1) / n)
            arr = (np.asarray(fr).astype(np.float32) * t).astype(np.uint8)
            out.append(Image.fromarray(arr))
        else:
            out.append(fr)
    return out


def fade_out(frames, n=8):
    out = []
    total = len(frames)
    for i, fr in enumerate(frames):
        if i >= total - n:
            t = ease((total - i) / n)
            arr = (np.asarray(fr).astype(np.float32) * t).astype(np.uint8)
            out.append(Image.fromarray(arr))
        else:
            out.append(fr)
    return out


_GLOW = None


def _glow_base():
    global _GLOW
    if _GLOW is None:
        glow = Image.new("RGB", (W, H), (5, 10, 14))
        gd = ImageDraw.Draw(glow)
        r = 240
        gd.ellipse([W // 2 - r, H // 2 - r - 40, W // 2 + r, H // 2 + r - 40], fill=(12, 40, 42))
        _GLOW = glow.filter(ImageFilter.GaussianBlur(36))
    return _GLOW


def title_card(pid, name, tag, seconds=2.0):
    n = int(seconds * FPS)
    glow = _glow_base()
    frames = []
    for i in range(n):
        t = ease(i / max(n - 1, 1))
        img = Image.blend(solid((5, 10, 14)), glow, 0.4 + 0.08 * math.sin(t * math.pi))
        d = ImageDraw.Draw(img)
        ink = tuple(int(240 * t) for _ in range(3))
        d.text((96, 280), "NEREID", font=FS, fill=(46, int(196 * t), int(168 * t)))
        d.text((96, 330), f"{pid}  ·  {name}", font=FT, fill=ink)
        d.text((96, 410), tag, font=FB, fill=tuple(int(170 * t) for _ in range(3)))
        frames.append(img)
    return frames


def end_card(pid, name, seconds=1.6):
    n = int(seconds * FPS)
    frames = []
    for i in range(n):
        t = ease(min(1.0, i / 10))
        img = solid((5, 10, 14))
        d = ImageDraw.Draw(img)
        d.text((96, 320), f"{pid}  ·  {name}", font=FH, fill=tuple(int(235 * t) for _ in range(3)))
        d.text((96, 380), "Designed for water. Built to be used.", font=FB,
               fill=(int(46 * t), int(196 * t), int(168 * t)))
        frames.append(img)
    return frames


def render_one(pid, name, tag, how):
    explode = find(HQ, f"hq-{pid}-explode.png")
    work = find(HQ, f"hq-{pid}-work.png")
    product = find(PROD, f"product-{pid}-*.png")
    lifestyle = find(LIFE, f"life-{pid}-*.png")

    if not explode and product:
        explode = product
    if not work and lifestyle:
        work = lifestyle

    seq = []
    seq = crossfade(seq, title_card(pid, name, tag, 2.0), 8)

    if product and product.exists():
        hero = ken_burns(load_rgb(product), int(2.4 * FPS), 1.02, 1.12, pan=(-0.08, 0.04))
        hero = [overlay_title(f, pid, name, tag, fade=min(1.0, i / 8)) for i, f in enumerate(hero)]
        seq = crossfade(seq, hero, 8)

    if explode and explode.exists():
        ex = ken_burns(load_rgb(explode), int(3.0 * FPS), 1.0, 1.08, pan=(0.05, -0.03))
        mid = []
        for i, f in enumerate(ex):
            fade = 1.0
            if i < 6:
                fade = ease(i / 6)
            elif i > len(ex) - 8:
                fade = ease((len(ex) - i) / 8)
            mid.append(overlay_caption(f, "Piece by piece", fade))
        seq = crossfade(seq, mid, 8)

    if work and work.exists():
        wk = ken_burns(load_rgb(work), int(3.2 * FPS), 1.02, 1.10, pan=(-0.04, 0.04))
        mid = []
        for i, f in enumerate(wk):
            fade = 1.0
            if i < 6:
                fade = ease(i / 6)
            elif i > len(wk) - 8:
                fade = ease((len(wk) - i) / 8)
            mid.append(overlay_caption(f, how, fade))
        seq = crossfade(seq, mid, 8)

    if lifestyle and lifestyle.exists():
        love = ken_burns(load_rgb(lifestyle), int(2.4 * FPS), 1.0, 1.09, pan=(0.03, -0.03))
        love = [overlay_title(f, pid, name, "In the wild", fade=min(1.0, max(0.0, (i - 3) / 8))) for i, f in enumerate(love)]
        seq = crossfade(seq, love, 8)

    if product and product.exists():
        close = ken_burns(load_rgb(product), int(1.8 * FPS), 1.06, 1.0, pan=(0.0, 0.0))
        seq = crossfade(seq, close, 6)

    seq = crossfade(seq, end_card(pid, name, 1.5), 6)
    seq = fade_in(seq, 6)
    seq = fade_out(seq, 8)

    OUT.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    path = OUT / f"{pid}-{slug}.mp4"
    writer = imageio.get_writer(
        str(path),
        fps=FPS,
        codec="libx264",
        quality=7,
        pixelformat="yuv420p",
        macro_block_size=1,
    )
    for fr in seq:
        writer.append_data(np.asarray(fr))
    writer.close()
    sec = len(seq) / FPS
    print(f"  {pid} -> {path.name} ({len(seq)} frames, {sec:.1f}s)", flush=True)
    return {"id": pid, "name": name, "file": f"videos/products/{path.name}", "seconds": round(sec, 1)}


def main():
    print(f"Rendering HQ cinematic films -> {OUT}", flush=True)
    manifest = [render_one(*p) for p in PRODUCTS]
    (OUT / "manifest.json").write_text(json.dumps({"videos": manifest, "quality": "hq-cinematic"}, indent=2), encoding="utf-8")
    print(f"Done - {len(manifest)} films", flush=True)


if __name__ == "__main__":
    main()
