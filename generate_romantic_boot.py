#!/usr/bin/env python3
"""Romantic Android boot animation — black & gold luxury M❤M."""

from __future__ import annotations

import math
import random
from pathlib import Path

import arabic_reshaper
import numpy as np
from bidi.algorithm import get_display
from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---- Boot animation specs ----
WIDTH = 720
HEIGHT = 1600
FPS = 5
NUM_FRAMES = 40
OUT_DIR = Path(__file__).resolve().parent / "part0"
DESC_PATH = Path(__file__).resolve().parent / "desc.txt"

NAMES = ["محمد", "مزن", "حبي", "حياتي"]

# Luxury gold palette
GOLD = (255, 210, 110)
GOLD_BRIGHT = (255, 235, 170)
GOLD_DEEP = (200, 145, 55)
GOLD_ROSE = (255, 190, 140)
GOLD_SOFT = (230, 190, 120)
CHAMPAGNE = (255, 245, 220)
AMBER = (255, 170, 70)
HEART_RED = (220, 40, 70)
HEART_DEEP = (160, 20, 45)
HEART_GLOW = (255, 80, 90)

NAME_COLORS = [
    GOLD,
    GOLD_BRIGHT,
    GOLD_ROSE,
    GOLD_SOFT,
    CHAMPAGNE,
    AMBER,
    (255, 200, 130),
]

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
rng = random.Random(91)


def ar(text: str) -> str:
    return get_display(arabic_reshaper.reshape(text))


def ease_out(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 1 - (1 - t) ** 3


def clamp_color(c):
    return tuple(int(max(0, min(255, v))) for v in c)


def heartbeat(t: float, bpm: float = 72.0) -> float:
    cycle = (t * (bpm / 60.0)) % 1.0
    p1 = math.exp(-((cycle - 0.12) ** 2) / 0.0035)
    p2 = 0.65 * math.exp(-((cycle - 0.30) ** 2) / 0.0045)
    return 0.88 + 0.30 * (p1 + p2)


def make_background(frame: int) -> Image.Image:
    """Pure black luxury stage with breathing gold spotlight."""
    sec = frame / FPS
    pulse = 0.5 + 0.5 * math.sin(sec * 1.2)
    hb = heartbeat(sec)

    y = np.linspace(0, 1, HEIGHT, dtype=np.float32)[:, None]
    x = np.linspace(0, 1, WIDTH, dtype=np.float32)[None, :]

    # near-true black base with faintest warm lift
    r = 2.0 + 4.0 * (1.0 - y) * 0.3
    g = 1.5 + 2.0 * (1.0 - y) * 0.2
    b = 1.0 + 1.5 * (1.0 - y) * 0.15

    # main gold spotlight (center, breathes with heartbeat)
    cx, cy = 0.5, 0.34
    dist = np.sqrt((x - cx) ** 2 + ((y - cy) * 0.55) ** 2)
    glow = np.exp(-dist * dist * 7.5) * (0.22 + 0.18 * (hb - 0.88) / 0.30)
    r = r + glow * 90
    g = g + glow * 55
    b = b + glow * 18

    # thin golden aurora haze (very subtle)
    aurora_y = 0.30 + 0.03 * math.sin(sec * 0.6)
    aurora = np.exp(-((y - aurora_y) ** 2) / 0.025) * (0.06 + 0.04 * pulse)
    aurora = aurora * (0.5 + 0.5 * np.sin(x * math.pi * 2.5 + sec * 0.4) ** 2)
    r = r + aurora * 55
    g = g + aurora * 35
    b = b + aurora * 10

    # soft floor gold reflection
    floor = (y ** 3.2) * (0.08 + 0.04 * pulse)
    r = r + floor * 35
    g = g + floor * 22
    b = b + floor * 6

    # deep vignette → pure black edges
    vx = (x - 0.5) * 2.1
    vy = (y - 0.5) * 2.0
    vig = 1.0 - 0.72 * np.clip(vx * vx * 0.9 + vy * vy * 0.7, 0, 1.3)
    r *= vig
    g *= vig
    b *= vig

    arr = np.stack(
        [
            np.clip(r, 0, 255).astype(np.uint8),
            np.clip(g, 0, 255).astype(np.uint8),
            np.clip(b, 0, 255).astype(np.uint8),
        ],
        axis=-1,
    )
    return Image.fromarray(arr, "RGB")


def make_starfield(n: int = 160):
    stars = []
    for _ in range(n):
        stars.append(
            {
                "x": rng.uniform(0, WIDTH),
                "y": rng.uniform(0, HEIGHT),
                "size": rng.choice([1, 1, 1, 2, 2, 3]),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(0.9, 3.0),
                "brightness": rng.uniform(0.35, 1.0),
                "color": rng.choice(
                    [
                        (255, 245, 210),
                        (255, 230, 160),
                        (255, 215, 130),
                        (255, 250, 230),
                        (255, 200, 120),
                        (255, 255, 240),
                    ]
                ),
            }
        )
    return stars


def draw_stars(img: Image.Image, stars, frame: int):
    d = ImageDraw.Draw(img)
    t = frame / FPS
    for s in stars:
        tw = 0.30 + 0.70 * (0.5 + 0.5 * math.sin(t * s["speed"] + s["phase"]))
        if math.sin(t * s["speed"] * 0.5 + s["phase"] * 3) > 0.93:
            tw = min(1.0, tw + 0.5)
        br = s["brightness"] * tw
        col = clamp_color(tuple(c * br for c in s["color"]))
        x, y = s["x"], s["y"]
        sz = s["size"]
        if sz <= 1:
            d.point((x, y), fill=col)
        else:
            d.ellipse((x - sz, y - sz, x + sz, y + sz), fill=col)
            if sz >= 3 and tw > 0.72:
                arm = sz + 2 + int(3 * tw)
                d.line((x - arm, y, x + arm, y), fill=col)
                d.line((x, y - arm, x, y + arm), fill=col)


def make_hearts(n: int = 42):
    hearts = []
    palette = [
        GOLD,
        GOLD_BRIGHT,
        GOLD_DEEP,
        GOLD_ROSE,
        AMBER,
        HEART_RED,
        (255, 180, 90),
        (230, 50, 70),
    ]
    for _ in range(n):
        hearts.append(
            {
                "x": rng.uniform(20, WIDTH - 20),
                "y0": rng.uniform(-HEIGHT * 0.5, HEIGHT),
                "speed": rng.uniform(20, 85),
                "drift": rng.uniform(-26, 26),
                "phase": rng.uniform(0, math.tau),
                "size": rng.uniform(6, 24),
                "alpha": rng.uniform(0.30, 0.92),
                "color": rng.choice(palette),
                "wobble": rng.uniform(0.8, 2.0),
            }
        )
    return hearts


def make_petals(n: int = 36):
    petals = []
    for _ in range(n):
        petals.append(
            {
                "x": rng.uniform(0, WIDTH),
                "y0": rng.uniform(-HEIGHT, HEIGHT),
                "speed": rng.uniform(16, 50),
                "drift": rng.uniform(-38, 38),
                "phase": rng.uniform(0, math.tau),
                "size": rng.uniform(5, 13),
                "alpha": rng.uniform(0.22, 0.65),
                "color": rng.choice(
                    [
                        GOLD,
                        GOLD_SOFT,
                        GOLD_ROSE,
                        (255, 200, 120),
                        (220, 160, 70),
                    ]
                ),
                "spin": rng.uniform(0.5, 2.0),
            }
        )
    return petals


def make_bokeh(n: int = 20):
    balls = []
    for _ in range(n):
        balls.append(
            {
                "x": rng.uniform(0, WIDTH),
                "y": rng.uniform(0, HEIGHT),
                "r": rng.uniform(12, 50),
                "phase": rng.uniform(0, math.tau),
                "speed": rng.uniform(0.35, 1.3),
                "alpha": rng.uniform(0.04, 0.14),
                "color": rng.choice(
                    [
                        (255, 190, 80),
                        (255, 210, 120),
                        (255, 160, 60),
                        (255, 230, 150),
                        (200, 140, 50),
                    ]
                ),
            }
        )
    return balls


def heart_polygon(cx: float, cy: float, size: float, n: int = 72):
    pts = []
    for i in range(n):
        t = math.tau * i / n
        x = 16 * math.sin(t) ** 3
        y = 13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)
        pts.append((cx + (x / 17.0) * size, cy - (y / 17.0) * size))
    return pts


def draw_heart(draw, cx, cy, size, color, outline=None):
    pts = heart_polygon(cx, cy, size)
    draw.polygon(pts, fill=color)
    if outline is not None:
        draw.line(pts + [pts[0]], fill=outline, width=max(1, int(size * 0.06)))


def _stroke_poly(points, width):
    if len(points) < 2:
        return points
    left, right = [], []
    for i in range(len(points)):
        if i == 0:
            dx = points[1][0] - points[0][0]
            dy = points[1][1] - points[0][1]
        elif i == len(points) - 1:
            dx = points[i][0] - points[i - 1][0]
            dy = points[i][1] - points[i - 1][1]
        else:
            dx = points[i + 1][0] - points[i - 1][0]
            dy = points[i + 1][1] - points[i - 1][1]
        length = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / length * width / 2, dx / length * width / 2
        left.append((points[i][0] + nx, points[i][1] + ny))
        right.append((points[i][0] - nx, points[i][1] - ny))
    return left + right[::-1]


def _capsule(draw, p0, p1, thickness, color):
    poly = _stroke_poly([p0, p1], thickness)
    draw.polygon(poly, fill=color)
    r = thickness / 2
    for p in (p0, p1):
        draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=color)


def draw_custom_M(draw, cx, cy, height, color, weight=0.22):
    h = float(height)
    w = h * 0.92
    th = h * weight
    bl = (cx - w / 2, cy + h / 2)
    tl = (cx - w / 2, cy - h / 2)
    br = (cx + w / 2, cy + h / 2)
    tr = (cx + w / 2, cy - h / 2)
    valley = (cx, cy + h * 0.22)
    _capsule(draw, bl, tl, th, color)
    _capsule(draw, tl, valley, th * 0.92, color)
    _capsule(draw, valley, tr, th * 0.92, color)
    _capsule(draw, tr, br, th, color)
    r = th * 0.42
    for p in (tl, tr, bl, br, valley):
        draw.ellipse((p[0] - r, p[1] - r, p[0] + r, p[1] + r), fill=color)


def draw_custom_M_glow(base, cx, cy, height, fill, glow_color, alpha=1.0, weight=0.22):
    if alpha < 0.02:
        return
    pad = int(height * 1.25)
    layer = Image.new("RGBA", (pad * 2, pad * 2), (0, 0, 0, 0))
    for blur, a in ((height * 0.32, 55), (height * 0.16, 95), (height * 0.07, 150)):
        g = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        draw_custom_M(gd, pad, pad, height, (*glow_color[:3], a), weight=weight)
        g = g.filter(ImageFilter.GaussianBlur(radius=max(1.0, blur)))
        layer = Image.alpha_composite(layer, g)
    # metallic highlight pass (lighter gold on top edge feel)
    ld = ImageDraw.Draw(layer)
    draw_custom_M(ld, pad, pad, height, (*fill[:3], 255), weight=weight)
    # thin bright edge highlight via slightly smaller offset M in champagne
    hi = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    hd = ImageDraw.Draw(hi)
    draw_custom_M(hd, pad - height * 0.02, pad - height * 0.03, height * 0.92, (*CHAMPAGNE, 90), weight=weight * 0.55)
    layer = Image.alpha_composite(layer, hi)
    if alpha < 0.99:
        arr = np.array(layer)
        arr[..., 3] = (arr[..., 3].astype(np.float32) * alpha).astype(np.uint8)
        layer = Image.fromarray(arr, "RGBA")
    base.paste(layer, (int(cx - pad), int(cy - pad)), layer)


def draw_petal(draw, cx, cy, size, angle, color):
    pts = []
    for i in range(20):
        a = math.tau * i / 20
        ox = math.cos(a) * size * 0.55
        oy = math.sin(a) * size
        rx = ox * math.cos(angle) - oy * math.sin(angle)
        ry = ox * math.sin(angle) + oy * math.cos(angle)
        pts.append((cx + rx, cy + ry))
    draw.polygon(pts, fill=color)


def make_falling_names(n: int = 34):
    items = []
    for i in range(n):
        name = NAMES[i % len(NAMES)]
        if rng.random() < 0.6:
            x = rng.choice(
                [rng.uniform(40, WIDTH * 0.26), rng.uniform(WIDTH * 0.74, WIDTH - 40)]
            )
        else:
            x = rng.uniform(50, WIDTH - 50)
        items.append(
            {
                "name": name,
                "x": x,
                "y0": rng.uniform(-HEIGHT * 1.0, HEIGHT * 0.2),
                "speed": rng.uniform(28, 95),
                "drift": rng.uniform(-20, 20),
                "phase": rng.uniform(0, math.tau),
                "size": rng.choice([24, 28, 32, 36, 40, 46, 50]),
                "color": NAME_COLORS[i % len(NAME_COLORS)],
                "alpha": rng.uniform(0.50, 0.95),
                "delay": rng.uniform(0, 1.6),
                "pulse": rng.uniform(0.8, 1.6),
            }
        )
    return items


def make_mm_logos(n: int = 8):
    logos = []
    for _ in range(n):
        logos.append(
            {
                "x": rng.uniform(50, WIDTH - 50),
                "y0": rng.uniform(-HEIGHT * 0.6, HEIGHT * 0.3),
                "speed": rng.uniform(22, 65),
                "drift": rng.uniform(-14, 14),
                "phase": rng.uniform(0, math.tau),
                "scale": rng.uniform(0.45, 0.85),
                "alpha": rng.uniform(0.35, 0.75),
                "delay": rng.uniform(0, 2.0),
            }
        )
    return logos


def make_gold_dust(n: int = 70):
    dust = []
    for _ in range(n):
        dust.append(
            {
                "x": rng.uniform(0, WIDTH),
                "y0": rng.uniform(-HEIGHT * 0.3, HEIGHT),
                "speed": rng.uniform(12, 40),
                "drift": rng.uniform(-20, 20),
                "phase": rng.uniform(0, math.tau),
                "size": rng.choice([1, 1, 2, 2, 3]),
                "alpha": rng.uniform(0.3, 0.9),
            }
        )
    return dust


def text_size(font, text):
    bbox = font.getbbox(text)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def draw_glow_text(base, xy, text, font, fill, glow_color=None, glow_radius=8):
    if glow_color is None:
        glow_color = fill
    tw, th = text_size(font, text)
    pad = glow_radius * 3 + 10
    layer = Image.new("RGBA", (tw + pad * 2, th + pad * 2), (0, 0, 0, 0))
    pos = (pad, pad)
    for r, a in ((glow_radius * 2.4, 40), (glow_radius * 1.3, 80), (max(2, glow_radius // 2), 140)):
        glow = Image.new("RGBA", layer.size, (0, 0, 0, 0))
        gd = ImageDraw.Draw(glow)
        gd.text(pos, text, font=font, fill=(*glow_color[:3], a))
        glow = glow.filter(ImageFilter.GaussianBlur(radius=r))
        layer = Image.alpha_composite(layer, glow)
    ld = ImageDraw.Draw(layer)
    ld.text(pos, text, font=font, fill=(*fill[:3], 255))
    base.paste(layer, (int(xy[0] - pad), int(xy[1] - pad)), layer)


def draw_mm_logo(base, cx, cy, scale, alpha, t, fonts=None):
    """Hero monogram: golden M ❤ M on black."""
    if alpha < 0.02:
        return

    hb = heartbeat(t)
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))

    # expanding gold heartbeat rings
    ring_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    rd = ImageDraw.Draw(ring_layer)
    for k in range(3):
        cycle = (t * (72 / 60.0) + k * 0.33) % 1.0
        expand = ease_out(cycle)
        rad = (48 + 175 * expand) * scale
        a = int(160 * (1.0 - expand) * alpha * (0.7 + 0.3 * hb))
        if a > 4:
            bbox = (cx - rad, cy - rad * 0.82, cx + rad, cy + rad * 0.82)
            rd.ellipse(bbox, outline=(255, 200, 100, a), width=max(2, int(5 * (1 - expand) + 1)))
    ring_layer = ring_layer.filter(ImageFilter.GaussianBlur(radius=1.2))
    layer = Image.alpha_composite(layer, ring_layer)

    # gold radial bloom
    bloom = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bloom)
    for i, rad in enumerate([250, 180, 125, 80, 48]):
        a = int((42 - i * 7) * alpha * (0.85 + 0.25 * (hb - 0.88) / 0.3))
        rr = rad * scale * (0.95 + 0.08 * hb)
        bd.ellipse(
            (cx - rr, cy - rr * 0.88, cx + rr, cy + rr * 0.88),
            fill=(255, 175, 60, max(0, a)),
        )
    bloom = bloom.filter(ImageFilter.GaussianBlur(radius=36))
    layer = Image.alpha_composite(layer, bloom)

    # golden light rays
    rays = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    ryd = ImageDraw.Draw(rays)
    for i in range(12):
        ang = t * 0.20 + i * (math.tau / 12)
        length = 210 * scale * (0.88 + 0.14 * math.sin(t * 2 + i))
        width_a = 0.05 + 0.015 * math.sin(t + i)
        x1 = cx + math.cos(ang - width_a) * 26 * scale
        y1 = cy + math.sin(ang - width_a) * 26 * scale
        x2 = cx + math.cos(ang + width_a) * 26 * scale
        y2 = cy + math.sin(ang + width_a) * 26 * scale
        x3 = cx + math.cos(ang) * length
        y3 = cy + math.sin(ang) * length * 0.82
        aa = int(26 * alpha * (0.5 + 0.5 * math.sin(t * 1.4 + i)))
        ryd.polygon([(x1, y1), (x2, y2), (x3, y3)], fill=(255, 200, 110, max(0, aa)))
    rays = rays.filter(ImageFilter.GaussianBlur(radius=9))
    layer = Image.alpha_composite(layer, rays)

    # orbiting gold hearts & sparkles
    sd = ImageDraw.Draw(layer)
    for i in range(12):
        ang = t * 0.48 + i * (math.tau / 12)
        rr = (128 + 12 * math.sin(t * 2.3 + i)) * scale * (0.96 + 0.06 * hb)
        px = cx + math.cos(ang) * rr
        py = cy + math.sin(ang) * rr * 0.78
        aa = int((150 + 90 * math.sin(t * 3 + i)) * alpha)
        if i % 2 == 0:
            draw_heart(sd, px, py, 5.5 * scale * (0.9 + 0.12 * hb), (*GOLD, max(0, aa)))
        else:
            spark = 2.0 + 1.5 * (0.5 + 0.5 * math.sin(t * 4 + i))
            sd.ellipse(
                (px - spark, py - spark, px + spark, py + spark),
                fill=(*GOLD_BRIGHT, max(0, aa)),
            )
            if aa > 170:
                sd.line((px - spark * 2.4, py, px + spark * 2.4, py), fill=(*CHAMPAGNE, aa // 2))
                sd.line((px, py - spark * 2.4, px, py + spark * 2.4), fill=(*CHAMPAGNE, aa // 2))

    # central heart — ruby red with gold rim glow
    heart_size = 56 * scale * hb
    hbloom = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    hbd = ImageDraw.Draw(hbloom)
    draw_heart(hbd, cx, cy, heart_size * 1.55, (255, 160, 50, int(100 * alpha)))
    draw_heart(hbd, cx, cy, heart_size * 1.35, (*HEART_GLOW, int(120 * alpha)))
    hbloom = hbloom.filter(ImageFilter.GaussianBlur(radius=16))
    layer = Image.alpha_composite(layer, hbloom)

    hd = ImageDraw.Draw(layer)
    # gold outer rim heart
    draw_heart(hd, cx, cy, heart_size * 1.12, (*GOLD_DEEP, int(220 * alpha)))
    # ruby body
    draw_heart(hd, cx, cy, heart_size, (*HEART_RED, int(250 * alpha)))
    draw_heart(hd, cx, cy + 2 * scale, heart_size * 0.68, (255, 90, 110, int(230 * alpha)))
    # glossy highlight
    draw_heart(
        hd,
        cx - heart_size * 0.20,
        cy - heart_size * 0.26,
        heart_size * 0.26,
        (255, 230, 220, int(200 * alpha)),
    )
    sp = 3.2 * scale
    sx, sy = cx - heart_size * 0.10, cy - heart_size * 0.30
    hd.ellipse((sx - sp, sy - sp, sx + sp, sy + sp), fill=(255, 255, 250, int(230 * alpha)))

    # golden M  ❤  M
    m_h = 100 * scale
    m_w = m_h * 0.92
    gap = heart_size * 1.05 + m_w * 0.55 + 18 * scale
    left_cx = cx - gap
    right_cx = cx + gap

    plate = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pld = ImageDraw.Draw(plate)
    for mx in (left_cx, right_cx):
        pld.ellipse(
            (mx - m_w * 0.75, cy - m_h * 0.65, mx + m_w * 0.75, cy + m_h * 0.65),
            fill=(255, 180, 60, int(28 * alpha)),
        )
    plate = plate.filter(ImageFilter.GaussianBlur(radius=14))
    layer = Image.alpha_composite(layer, plate)

    draw_custom_M_glow(layer, left_cx, cy, m_h, GOLD_BRIGHT, GOLD, alpha=1.0, weight=0.24)
    draw_custom_M_glow(layer, right_cx, cy, m_h, GOLD_BRIGHT, GOLD, alpha=1.0, weight=0.24)

    sd = ImageDraw.Draw(layer)
    for mx in (left_cx, right_cx):
        for ox in (-14, 0, 14):
            draw_heart(
                sd,
                mx + ox,
                cy + m_h * 0.58,
                5.2 * scale,
                (*GOLD, int(210 * alpha)),
            )

    if alpha < 0.99:
        arr = np.array(layer)
        arr[..., 3] = (arr[..., 3].astype(np.float32) * alpha).astype(np.uint8)
        layer = Image.fromarray(arr, "RGBA")
    base.alpha_composite(layer)


def draw_small_mm(base, cx, cy, scale, alpha, fonts=None):
    if alpha < 0.05:
        return
    layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    m_h = 26 * scale
    m_w = m_h * 0.92
    hs = 9 * scale
    gap = 6 * scale
    total = m_w + gap + hs * 2.0 + gap + m_w
    left_cx = cx - total / 2 + m_w / 2
    right_cx = cx + total / 2 - m_w / 2
    draw_custom_M_glow(layer, left_cx, cy, m_h, GOLD_BRIGHT, GOLD, alpha=1.0, weight=0.26)
    sd = ImageDraw.Draw(layer)
    draw_heart(sd, cx, cy, hs, (*HEART_RED, int(245 * alpha)))
    draw_heart(sd, cx - hs * 0.12, cy - hs * 0.22, hs * 0.28, (255, 220, 200, int(180 * alpha)))
    draw_custom_M_glow(layer, right_cx, cy, m_h, GOLD_BRIGHT, GOLD, alpha=1.0, weight=0.26)
    if alpha < 0.99:
        arr = np.array(layer)
        arr[..., 3] = (arr[..., 3].astype(np.float32) * alpha).astype(np.uint8)
        layer = Image.fromarray(arr, "RGBA")
    base.alpha_composite(layer)


def render_frame(frame, stars, hearts, petals, bokeh, names, mm_logos, dust, fonts):
    t = frame / FPS
    progress = frame / max(1, NUM_FRAMES - 1)
    hb = heartbeat(t)

    img = make_background(frame).convert("RGBA")

    # gold bokeh
    bok = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    bd = ImageDraw.Draw(bok)
    for b in bokeh:
        pulse = 0.7 + 0.3 * math.sin(t * b["speed"] + b["phase"])
        a = int(255 * b["alpha"] * pulse)
        r = b["r"] * (0.9 + 0.15 * pulse)
        x = b["x"] + math.sin(t * 0.3 + b["phase"]) * 12
        y = b["y"] + math.cos(t * 0.25 + b["phase"]) * 10
        bd.ellipse((x - r, y - r, x + r, y + r), fill=(*b["color"], a))
    bok = bok.filter(ImageFilter.GaussianBlur(radius=11))
    img = Image.alpha_composite(img, bok)

    draw_stars(img, stars, frame)

    # gold dust
    dd = ImageDraw.Draw(img)
    for p in dust:
        y = (p["y0"] + t * p["speed"]) % (HEIGHT + 40) - 20
        x = p["x"] + math.sin(t * 0.6 + p["phase"]) * p["drift"]
        tw = 0.5 + 0.5 * math.sin(t * 2 + p["phase"])
        a = int(255 * p["alpha"] * tw)
        s = p["size"]
        col = (*GOLD_BRIGHT, a) if s > 1 else (*GOLD, a)
        if s <= 1:
            dd.point((x, y), fill=col[:3])
        else:
            dd.ellipse((x - s, y - s, x + s, y + s), fill=col[:3])

    # gold petals
    petal_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    pd = ImageDraw.Draw(petal_layer)
    for p in petals:
        y = (p["y0"] + t * p["speed"]) % (HEIGHT + 60) - 30
        x = p["x"] + math.sin(t * 0.7 + p["phase"]) * p["drift"]
        edge = 1.0
        if y < 30:
            edge = y / 30
        elif y > HEIGHT - 40:
            edge = (HEIGHT - y) / 40
        edge = max(0.0, min(1.0, edge))
        a = int(255 * p["alpha"] * edge)
        ang = t * p["spin"] + p["phase"]
        draw_petal(pd, x, y, p["size"], ang, (*p["color"], a))
    img = Image.alpha_composite(img, petal_layer)

    # falling hearts (gold + ruby)
    heart_layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
    hd = ImageDraw.Draw(heart_layer)
    for h in hearts:
        y = (h["y0"] + t * h["speed"]) % (HEIGHT + 90) - 45
        x = h["x"] + math.sin(t * h["wobble"] + h["phase"]) * h["drift"]
        edge = 1.0
        if y < 40:
            edge = y / 40
        elif y > HEIGHT - 60:
            edge = (HEIGHT - y) / 60
        edge = max(0.0, min(1.0, edge))
        a = int(
            255
            * h["alpha"]
            * edge
            * (0.65 + 0.35 * math.sin(t * 1.4 + h["phase"]))
            * (0.9 + 0.1 * hb)
        )
        sz = h["size"] * (0.88 + 0.18 * math.sin(t * 2.2 + h["phase"])) * (0.95 + 0.08 * hb)
        draw_heart(hd, x, y, sz, (*h["color"], max(0, a)))
    img = Image.alpha_composite(img, heart_layer)

    # falling golden names
    for item in names:
        local_t = t - item["delay"]
        if local_t < 0:
            continue
        y = (item["y0"] + local_t * item["speed"]) % (HEIGHT + 130) - 65
        x = item["x"] + math.sin(local_t * 0.95 + item["phase"]) * item["drift"]

        edge = 1.0
        if y < 50:
            edge = y / 50
        elif y > HEIGHT - 80:
            edge = (HEIGHT - y) / 80
        edge = max(0.0, min(1.0, edge))

        dx = (x - WIDTH * 0.5) / (WIDTH * 0.28)
        dy = (y - HEIGHT * 0.34) / (HEIGHT * 0.14)
        center_dist = math.sqrt(dx * dx + dy * dy)
        center_fade = 0.12 + 0.88 * min(1.0, max(0.0, (center_dist - 0.5) / 0.75))

        fade_in = min(1.0, local_t / 0.5)
        twinkle = 0.85 + 0.15 * math.sin(t * item["pulse"] + item["phase"])
        alpha = item["alpha"] * edge * fade_in * center_fade * twinkle
        if alpha < 0.05:
            continue

        font = fonts[item["size"]]
        text = ar(item["name"])
        tw, th = text_size(font, text)
        fill = clamp_color(item["color"])
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        glow_r = max(5, item["size"] // 5)
        draw_glow_text(
            layer,
            (x - tw / 2, y - th / 2),
            text,
            font,
            fill,
            glow_color=GOLD_DEEP,
            glow_radius=glow_r,
        )
        if alpha < 0.99:
            arr = np.array(layer)
            arr[..., 3] = (arr[..., 3].astype(np.float32) * alpha).astype(np.uint8)
            layer = Image.fromarray(arr, "RGBA")
        img = Image.alpha_composite(img, layer)

    # small floating gold M❤M
    for logo in mm_logos:
        local_t = t - logo["delay"]
        if local_t < 0:
            continue
        y = (logo["y0"] + local_t * logo["speed"]) % (HEIGHT + 80) - 40
        x = logo["x"] + math.sin(local_t * 0.8 + logo["phase"]) * logo["drift"]
        edge = 1.0
        if y < 40:
            edge = y / 40
        elif y > HEIGHT - 50:
            edge = (HEIGHT - y) / 50
        edge = max(0.0, min(1.0, edge))
        dx = (x - WIDTH * 0.5) / (WIDTH * 0.25)
        dy = (y - HEIGHT * 0.34) / (HEIGHT * 0.12)
        if dx * dx + dy * dy < 1.0:
            continue
        a = logo["alpha"] * edge * min(1.0, local_t / 0.5)
        draw_small_mm(img, x, y, logo["scale"], a, fonts)

    # HERO emblem
    enter = ease_out(min(1.0, t / 0.85))
    end_a = 1.0
    if progress > 0.92:
        end_a = 1.0 - (progress - 0.92) / 0.08 * 0.08
    emblem_alpha = enter * end_a
    pop = (0.78 + 0.22 * ease_out(min(1.0, t / 0.85))) * (0.97 + 0.03 * hb)
    cx, cy = WIDTH / 2, HEIGHT * 0.34
    cy = cy + math.sin(t * 1.3) * 7
    draw_mm_logo(img, cx, cy, pop, emblem_alpha, t, fonts)

    # Arabic names under logo — champagne gold
    name_a = ease_out(max(0.0, min(1.0, (t - 0.7) / 1.0))) * end_a
    if name_a > 0.02:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        font_lg = fonts[48]
        font_md = fonts[32]
        name_m = ar("محمد")
        name_z = ar("مزن")
        cream = CHAMPAGNE
        tw, th = text_size(font_lg, name_m)
        y_names = cy + 118 * pop
        draw_glow_text(layer, (cx - tw / 2, y_names), name_m, font_lg, cream, GOLD, 12)
        sd = ImageDraw.Draw(layer)
        for i, ox in enumerate((-36, -12, 12, 36)):
            col = HEART_RED if i in (1, 2) else GOLD
            draw_heart(
                sd,
                cx + ox,
                y_names + th + 16,
                5.5 + (i in (1, 2)) * 2,
                (*col, int(220 * name_a)),
            )
        tw2, _ = text_size(font_lg, name_z)
        draw_glow_text(
            layer, (cx - tw2 / 2, y_names + th + 30), name_z, font_lg, cream, GOLD, 12
        )
        bob = math.sin(t * 1.7) * 10
        s1, s2 = ar("حبي"), ar("حياتي")
        tws, _ = text_size(font_md, s1)
        tws2, _ = text_size(font_md, s2)
        draw_glow_text(
            layer, (cx - 240 - tws / 2, cy + bob), s1, font_md, GOLD_ROSE, GOLD_DEEP, 8
        )
        draw_glow_text(
            layer, (cx + 240 - tws2 / 2, cy - bob), s2, font_md, GOLD_SOFT, GOLD_DEEP, 8
        )
        arr = np.array(layer)
        arr[..., 3] = (arr[..., 3].astype(np.float32) * name_a).astype(np.uint8)
        layer = Image.fromarray(arr, "RGBA")
        img = Image.alpha_composite(img, layer)

    # bottom gold brand strip
    tag_t = ease_out(max(0.0, min(1.0, (t - 1.3) / 1.3))) * end_a
    if tag_t > 0.02:
        layer = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        by = HEIGHT * 0.80
        gg = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        gd = ImageDraw.Draw(gg)
        gd.ellipse(
            (WIDTH * 0.18, by - 40, WIDTH * 0.82, by + 70),
            fill=(255, 180, 60, int(40 * tag_t)),
        )
        gg = gg.filter(ImageFilter.GaussianBlur(radius=28))
        layer = Image.alpha_composite(layer, gg)

        m_h = 58 * (0.97 + 0.04 * hb)
        m_w = m_h * 0.92
        hs = 20 * (0.95 + 0.08 * hb)
        gap = 16
        total = m_w + gap + hs * 2.1 + gap + m_w
        left_cx = WIDTH / 2 - total / 2 + m_w / 2
        right_cx = WIDTH / 2 + total / 2 - m_w / 2
        hcx = WIDTH / 2
        draw_custom_M_glow(layer, left_cx, by, m_h, GOLD_BRIGHT, GOLD, 1.0, 0.24)
        sd = ImageDraw.Draw(layer)
        draw_heart(sd, hcx, by, hs * 1.35, (*GOLD_DEEP, int(110 * tag_t)))
        draw_heart(sd, hcx, by, hs, (*HEART_RED, int(245 * tag_t)))
        draw_heart(
            sd, hcx - hs * 0.15, by - hs * 0.22, hs * 0.28, (255, 230, 210, int(180 * tag_t))
        )
        draw_custom_M_glow(layer, right_cx, by, m_h, GOLD_BRIGHT, GOLD, 1.0, 0.24)

        font = fonts[28]
        left = ar("محمد")
        right = ar("مزن")
        tw_l, th_l = text_size(font, left)
        gap2 = 14
        hs2 = 9
        total2 = tw_l + gap2 + hs2 * 2 + gap2 + text_size(font, right)[0]
        x1 = (WIDTH - total2) / 2
        y = by + 48
        draw_glow_text(layer, (x1, y), left, font, CHAMPAGNE, GOLD, 8)
        draw_heart(
            sd, x1 + tw_l + gap2 + hs2, y + th_l * 0.55, hs2, (*HEART_RED, int(240 * tag_t))
        )
        draw_glow_text(
            layer, (x1 + tw_l + gap2 + hs2 * 2 + gap2, y), right, font, CHAMPAGNE, GOLD, 8
        )
        arr = np.array(layer)
        arr[..., 3] = (arr[..., 3].astype(np.float32) * tag_t).astype(np.uint8)
        layer = Image.fromarray(arr, "RGBA")
        img = Image.alpha_composite(img, layer)

    # sparkle burst on heartbeat peaks
    if hb > 1.08:
        burst = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 0))
        bd = ImageDraw.Draw(burst)
        strength = (hb - 1.08) / 0.10
        for i in range(12):
            ang = i * (math.tau / 12) + t * 3
            dist = 70 + 45 * strength
            px = cx + math.cos(ang) * dist
            py = cy + math.sin(ang) * dist * 0.8
            a = int(210 * strength * emblem_alpha)
            s = 2 + 3 * strength
            bd.ellipse((px - s, py - s, px + s, py + s), fill=(*GOLD_BRIGHT, a))
            bd.line((px - s * 2.5, py, px + s * 2.5, py), fill=(*CHAMPAGNE, a // 2))
            bd.line((px, py - s * 2.5, px, py + s * 2.5), fill=(*CHAMPAGNE, a // 2))
        img = Image.alpha_composite(img, burst)

    # subtle film grain
    grain = np.random.randint(0, 8, size=(HEIGHT, WIDTH, 1), dtype=np.int16)
    g_img = np.array(img)
    g_img[..., :3] = np.clip(g_img[..., :3].astype(np.int16) + (grain - 4), 0, 255).astype(
        np.uint8
    )
    img = Image.fromarray(g_img, "RGBA")

    return img.convert("RGB")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    sizes = sorted(
        set(
            [
                18, 20, 22, 24, 26, 28, 30, 32, 34, 36, 38, 40,
                44, 46, 48, 50, 52, 56, 60, 64, 72, 78, 84,
            ]
        )
    )
    fonts = {s: ImageFont.truetype(FONT_PATH, s) for s in sizes}

    stars = make_starfield(160)
    hearts = make_hearts(44)
    petals = make_petals(36)
    bokeh = make_bokeh(20)
    names = make_falling_names(32)
    mm_logos = make_mm_logos(8)
    dust = make_gold_dust(80)

    print(f"Generating {NUM_FRAMES} frames at {WIDTH}x{HEIGHT} @ {FPS}fps ...")
    preview_frames = []
    for i in range(NUM_FRAMES):
        frame = render_frame(i, stars, hearts, petals, bokeh, names, mm_logos, dust, fonts)
        path = OUT_DIR / f"frame_{i + 1:04d}.png"
        frame.save(path, format="PNG", optimize=True)
        if i in (0, 5, 10, 15, 20, 25, 30, 35, 39):
            preview_frames.append((i, frame.copy()))
        print(f"  frame {i + 1:02d}/{NUM_FRAMES}")

    DESC_PATH.write_bytes(f"{WIDTH} {HEIGHT} {FPS}\r\np 0 0 part0\r\n\r\n\r\n".encode("ascii"))

    prev_dir = Path(__file__).resolve().parent / "preview"
    prev_dir.mkdir(exist_ok=True)
    for i, fr in preview_frames:
        fr.save(prev_dir / f"frame_{i + 1:04d}.png")
    keys = [preview_frames[j][1].resize((180, 400)) for j in range(len(preview_frames))]
    strip = Image.new("RGB", (180 * len(keys), 400), (0, 0, 0))
    for idx, k in enumerate(keys):
        strip.paste(k, (idx * 180, 0))
    strip.save(prev_dir / "strip.png")

    gif_frames = [
        Image.open(OUT_DIR / f"frame_{i:04d}.png").resize((216, 480), Image.LANCZOS)
        for i in range(1, NUM_FRAMES + 1)
    ]
    gif_frames[0].save(
        prev_dir / "boot_preview.gif",
        save_all=True,
        append_images=gif_frames[1:],
        duration=200,
        loop=0,
        optimize=True,
    )
    print("Done.")


if __name__ == "__main__":
    main()
