"""
iso_kit.py — the show-tell drawing kit. PASTE this block at the top of a reel's scenes.py;
do not import it (Gate A copies only scenes.py into its sandbox).

Drawn isometric objects in the Claude palette: cardboard boxes (closed, open, taped), dark
MCP blocks with ports, flat skill pages, server stacks with lights, checks, a cursor, pills,
and a WRITING KIT (quill, inkwell, paper, scribble lines, branching outline + the write_lines /
grow_tree animations that make the quill write). A PERSON IS NEVER AN ICON: `professor_bear(ratio, …)`
places a random Professor Bear portrait of the right aspect ratio (PROFESSOR BEAR LAW).
Pacing helpers read the reel's beat_sheet.json so scenes wait for their spoken phrase.

Every rule in ../SKILL.md "DRAWING LAWS" is already obeyed by these primitives; keep it that
way when you add one (label beside, never inside; terracotta never under text; dim greys
with gaps for chart blocks; type floor 32).
"""
from manim import *
import numpy as np
import json as _json, os as _os

# ═════════════════════════════ ISO KIT (show-tell) ═════════════════════════════
STAGE = "#F2F0E9"; INK = "#3D3929"; TERRA = "#D97757"; DIM = "#8B8F96"; GHOST = "#D9D4C7"; CARD = "#FAF9F5"
BOX_TOP, BOX_L, BOX_R = "#F3E9D8", "#DCC9AA", "#C7AE86"          # kraft cardboard: top, left face, right face (deep enough for Gate V contrast)
BOX_IN1, BOX_IN2, BOX_FLOOR = "#CDB894", "#BFA67E", "#B39A72"     # inside walls + floor
DARK_TOP, DARK_L, DARK_R = "#3A3530", "#26221F", "#1E1B18"        # MCP / server blocks
PAGE_TOP, PAGE_L, PAGE_R = "#FFFFFF", "#ECE7DF", "#E2DCD2"         # skill pages
BAR1, BAR2, BAR3 = "#8B8F96", "#B4AFA6", "#D9D4C7"                # chart segments, dim to ghost
SERIF = "EB Garamond"
C30 = 0.8660254
config.background_color = STAGE


def T(s, size=36, color=INK, bold=False):
    return Text(s, font=SERIF, color=color, font_size=size, weight="BOLD" if bold else "NORMAL")


class Iso:
    """Isometric projection: x runs right-up, y runs left-up, z runs up. (ox, oy) is where (0,0,0) lands."""
    def __init__(self, ox=0.0, oy=0.0, s=1.0):
        self.ox, self.oy, self.s = ox, oy, s

    def p(self, x, y, z=0.0):
        return np.array([self.ox + (x - y) * C30 * self.s, self.oy + (x + y) * 0.5 * self.s + z * self.s, 0.0])

    def v(self, dx, dy, dz=0.0):
        return self.p(dx, dy, dz) - self.p(0, 0, 0)

    def quad(self, pts, fill, stroke=INK, sw=4):
        return Polygon(*[self.p(*q) for q in pts], fill_color=fill, fill_opacity=1, stroke_color=stroke, stroke_width=sw)

    def box(self, x0, y0, z0, w, d, h, top=BOX_TOP, left=BOX_L, right=BOX_R, sw=4):
        """Closed box: the two front faces (x = x0 and y = y0) plus the top."""
        x1, y1, z1 = x0 + w, y0 + d, z0 + h
        return VGroup(
            self.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], left, sw=sw),
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], right, sw=sw),
            self.quad([(x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)], top, sw=sw))

    def open_box(self, x0, y0, z0, w, d, h):
        """(back, front): floor + inner back walls, then the front walls. Put contents between them."""
        x1, y1, z1 = x0 + w, y0 + d, z0 + h
        back = VGroup(
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0)], BOX_FLOOR),
            self.quad([(x1, y0, z0), (x1, y1, z0), (x1, y1, z1), (x1, y0, z1)], BOX_IN1),
            self.quad([(x0, y1, z0), (x1, y1, z0), (x1, y1, z1), (x0, y1, z1)], BOX_IN2))
        front = VGroup(
            self.quad([(x0, y0, z0), (x0, y1, z0), (x0, y1, z1), (x0, y0, z1)], BOX_L),
            self.quad([(x0, y0, z0), (x1, y0, z0), (x1, y0, z1), (x0, y0, z1)], BOX_R))
        back.set_z_index(0); front.set_z_index(2)
        return back, front

    def tape(self, x0, y0, z1, w, d, drop=0.35, t=0.22):
        """Terracotta tape across the top (along x) and down the left front face."""
        ym = y0 + d / 2
        return VGroup(
            self.quad([(x0, ym - t, z1), (x0 + w, ym - t, z1), (x0 + w, ym + t, z1), (x0, ym + t, z1)], TERRA, sw=0),
            self.quad([(x0, ym - t, z1), (x0, ym + t, z1), (x0, ym + t, z1 - drop), (x0, ym - t, z1 - drop)], TERRA, sw=0))

    def mcp(self, x0, y0, z0, w=1.3, d=1.3, h=0.7):
        """Dark MCP block with two light ports on its right front face."""
        body = self.box(x0, y0, z0, w, d, h, DARK_TOP, DARK_L, DARK_R)
        ports = VGroup(*[self.box(x0 + w * f, y0 - 0.18, z0 + h * 0.3, w * 0.16, 0.18, h * 0.3, GHOST, BOX_IN1, BOX_IN2, sw=1)
                         for f in (0.22, 0.58)])
        return VGroup(body, ports)

    def page(self, x0, y0, z0, w=1.1, d=1.4):
        """A skill page lying flat: white slab, three ghost text lines, one terracotta dot."""
        slab = self.box(x0, y0, z0, w, d, 0.06, PAGE_TOP, PAGE_L, PAGE_R, sw=1.5)
        zt = z0 + 0.06
        lines = VGroup(*[Line(self.p(x0 + 0.2, y0 + d * f, zt), self.p(x0 + w - 0.2, y0 + d * f, zt), color=GHOST, stroke_width=4)
                         for f in (0.3, 0.5, 0.7)])
        dot = Dot(self.p(x0 + 0.2, y0 + d * 0.86, zt), radius=0.06, color=TERRA)
        return VGroup(slab, lines, dot)

    def server(self, x0, y0, z0, w=1.4, d=1.4, slab=0.42, n=3):
        """A stack of dark server slabs; returns (stack, lights) — lights start ghost, turn terracotta."""
        stack = VGroup(*[self.box(x0, y0, z0 + i * (slab + 0.04), w, d, slab, DARK_TOP, DARK_L, DARK_R) for i in range(n)])
        lights = VGroup(*[Dot(self.p(x0 + 0.25, y0, z0 + i * (slab + 0.04) + slab / 2), radius=0.06, color=GHOST) for i in range(n)])
        return stack, lights


def ease_in(t):
    """Quadratic ease-in (things dropping into a box). Local: Gate A's stub has no ease_in_quad."""
    return t * t


def check(x, y, s=0.2, color=INK, w=7):
    return VGroup(Line([x - s, y, 0], [x - s * 0.3, y - s * 0.75, 0], color=color, stroke_width=w),
                  Line([x - s * 0.3, y - s * 0.75, 0], [x + s * 1.1, y + s * 0.85, 0], color=color, stroke_width=w))


def cursor(x, y, s=0.45):
    return Polygon([x, y, 0], [x, y - s, 0], [x + s * 0.28, y - s * 0.72, 0], [x + s * 0.62, y - s * 0.66, 0],
                   fill_color=INK, fill_opacity=1, stroke_color=CARD, stroke_width=2)


def pill(x, y, w, h=0.62, fill="#FFFFFF"):
    return RoundedRectangle(width=w, height=h, corner_radius=h / 2, fill_color=fill, fill_opacity=1, stroke_width=0).move_to([x, y, 0])


# ═════════════════════════════ WRITING KIT (quill, ink, paper, scribble) ═════════════════════════════
# Added 2026-10-07 from Bear's two reference drawings: a quill drawing a branching outline on a
# scroll, and three scattered pages of scribbled handwriting with a quill. Use when a beat is
# about writing, drafting, authorship, notes, a manuscript, a log, a letter, a signature.
# Terracotta here is only the ink drop and the outline's nodes (dots) — never the lines.


def quill(x, y, s=1.0, angle=0.0, color=INK, fill=BOX_TOP):
    """A drawn quill with its NIB at (x, y); the feather points up-right. `g.nib` is the nib point.
    Kraft-filled feather, ink outline, a shaft line and one barb. Rotate with `angle` (radians)."""
    o = np.array([x, y, 0.0])
    def P(u, v):  # icon units (0..1) → scene, nib at origin, tip at (1, 1.1)·s
        return o + np.array([u * s, v * s, 0.0])
    body = VMobject(fill_color=fill, fill_opacity=1, stroke_color=color, stroke_width=4)
    body.set_points_smoothly([P(0.00, 0.00), P(0.12, 0.62), P(0.55, 1.02), P(1.00, 1.10),
                              P(0.95, 0.68), P(0.62, 0.22), P(0.00, 0.00)])
    shaft = Line(P(0.02, 0.02), P(0.98, 1.06), color=color, stroke_width=3)
    barb = Line(P(0.46, 0.50), P(0.40, 0.72), color=color, stroke_width=2.5)
    g = VGroup(body, shaft, barb)
    if angle:
        g.rotate(angle, about_point=o)
    g.nib = o.copy()
    return g


def inkwell(iso, x0=0.0, y0=0.0, z0=0.0, s=0.7):
    """A dark ink bottle (iso box + narrow neck) with one terracotta ink dot on the lid."""
    body = iso.box(x0, y0, z0, s, s, s * 0.9, DARK_TOP, DARK_L, DARK_R)
    neck = iso.box(x0 + s * 0.3, y0 + s * 0.3, z0 + s * 0.9, s * 0.4, s * 0.4, s * 0.25, DARK_TOP, DARK_L, DARK_R)
    drop = Dot(iso.p(x0 + s * 0.5, y0 + s * 0.5, z0 + s * 1.15), radius=0.07, color=TERRA)
    return VGroup(body, neck, drop)


def paper(x, y, w=2.4, h=3.0, tilt=0.0, fill=PAGE_TOP):
    """A flat 2-D sheet (the scattered-pages drawing): white page, ink outline, kraft drop shadow.
    `tilt` in radians. Returns a VGroup; `.sheet` is the page rectangle for placing lines on it."""
    shadow = Rectangle(width=w, height=h, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.12, y - 0.12, 0])
    sheet = Rectangle(width=w, height=h, fill_color=fill, fill_opacity=1, stroke_color=INK, stroke_width=4).move_to([x, y, 0])
    g = VGroup(shadow, sheet)
    if tilt:
        g.rotate(tilt, about_point=[x, y, 0])
    g.sheet = sheet
    g.cx, g.cy, g.w, g.h, g.tilt = float(x), float(y), float(w), float(h), float(tilt)   # read these; never ask the stub for vertices
    return g


def scribble(x, y, w, amp=0.07, waves=None, color=INK, sw=4):
    """One wavy handwriting line from (x, y) rightwards for `w` units. Reads as script, never as type."""
    n = waves or max(3, int(round(w * 3)))
    pts = []
    for i in range(n * 4 + 1):
        t = i / (n * 4)
        pts.append([x + w * t, y + amp * np.sin(t * n * 2 * np.pi) * (0.6 + 0.4 * np.cos(t * 5.3)), 0])
    m = VMobject(stroke_color=color, stroke_width=sw)
    m.set_points_smoothly(pts)
    return m


def scribble_block(x, y, w, n=3, gap=0.34, last=0.62, color=INK, sw=4):
    """`n` scribble lines stacked downward from (x, y); the last one is `last`× as long (a paragraph end)."""
    return VGroup(*[scribble(x, y - i * gap, w * (last if i == n - 1 else 1.0), color=color, sw=sw) for i in range(n)])


def scribbles_on(page, n=3, inset=0.3, gap=0.34, color=INK, sw=4):
    """Scribble lines laid on a `paper()` group, following its tilt (uses the page's stored geometry)."""
    w = page.w - 2 * inset
    g = scribble_block(page.cx - w / 2, page.cy + page.h / 2 - inset - 0.1, w, n=n, gap=gap, color=color, sw=sw)
    if abs(page.tilt) > 1e-3:
        g.rotate(page.tilt, about_point=[page.cx, page.cy, 0])
    return g


def outline_tree(x, y, h=1.6, levels=2, spread=0.55, color=INK, node=TERRA):
    """A branching outline (the scroll drawing): a trunk rising from (x, y), forking `levels` times,
    a terracotta dot at every tip. Returns VGroup(lines, dots) — draw lines first, dots last."""
    lines, dots = VGroup(), VGroup()
    def grow(px, py, length, lvl, dx):
        qx, qy = px + dx, py + length
        lines.add(Line([px, py, 0], [qx, qy, 0], color=color, stroke_width=4))
        if lvl == 0:
            dots.add(Dot([qx, qy, 0], radius=0.075, color=node))
            return
        for d in (-spread, spread):
            grow(qx, qy, length * 0.62, lvl - 1, d * (0.75 ** (levels - lvl)))
    grow(x, y, h * 0.42, levels, 0.0)
    g = VGroup(lines, dots)
    g.lines, g.dots = lines, dots
    return g


def write_lines(self, q, lines, speed=1.6, hop=0.22, dip=0.06):
    """Animate the quill `q` WRITING each line in `lines`: the nib hops to the line's start, then the
    line draws while the nib rides its tip (the writing motion). `speed` is scene units per second.
    Call between `until()` phrases so each line lands on its words. Works with the midpoint guard."""
    for ln in lines:
        start = np.array(ln.get_start(), dtype=float)
        self.play(q.animate.shift(start - q.nib), run_time=hop, rate_func=smooth)
        q.nib = start.copy()
        off = np.array(q.get_center(), dtype=float) - q.nib
        def ride(m, a, ln=ln, off=off):
            m.move_to(np.array(ln.point_from_proportion(min(1.0, a)), dtype=float) + off)
        try:
            length = float(ln.get_arc_length())
        except Exception:          # Gate A's stub has no arc length; any positive number keeps the check moving
            length = 2.0
        rt = max(0.35, length / speed)
        self.play(Create(ln), UpdateFromAlphaFunc(q, ride), run_time=rt, rate_func=linear)
        q.nib = np.array(ln.get_end(), dtype=float)
        # the small lift between lines keeps the quill from fusing with the ink at GATE T's midpoint
        q.shift([0, dip, 0]); q.nib = q.nib + np.array([0, dip, 0])


def grow_tree(self, q, tree, per=0.45):
    """Animate the quill drawing an `outline_tree`: each segment draws as the nib rides it; dots land last."""
    for ln in tree.lines:
        start = np.array(ln.get_start(), dtype=float)
        self.play(q.animate.shift(start - q.nib), run_time=0.18, rate_func=smooth)
        q.nib = start.copy()
        off = np.array(q.get_center(), dtype=float) - q.nib
        def ride(m, a, ln=ln, off=off):
            m.move_to(np.array(ln.point_from_proportion(min(1.0, a)), dtype=float) + off)
        self.play(Create(ln), UpdateFromAlphaFunc(q, ride), run_time=per, rate_func=linear)
        q.nib = np.array(ln.get_end(), dtype=float)
    self.play(LaggedStart(*[GrowFromCenter(d) for d in tree.dots], lag_ratio=0.15), run_time=0.6)


# ═════════════════════════════ PROFESSOR BEAR (a person is never an icon) ═════════════════════════════
# PROFESSOR BEAR LAW (Bear, 2026-10-07): when a beat needs an icon of a person, or Professor Bear himself,
# do not draw a person token and do not pull a person icon. Show one of the Professor Bear portraits in
# brutalist.art/professor-bear/, chosen at random among those of the right aspect ratio (1x1 · 2x3 · 16x9).
# `./art bear <ratio> --seed <beat>` picks the same way from the shell.
def _pb_dir():
    env = _os.environ.get("ART_HOME")
    cands = [env and _os.path.join(env, "professor-bear")]
    here = _os.path.dirname(_os.path.abspath(__file__))
    for _ in range(8):
        cands.append(_os.path.join(here, "brutalist.art", "professor-bear"))
        cands.append(_os.path.join(here, "professor-bear"))
        here = _os.path.dirname(here)
    cands.append("/Users/bear/Documents/CoWork/bear-textbooks/books/brutalist.art/professor-bear")
    for c in cands:
        if c and _os.path.isdir(c):
            return c
    return cands[-1]


_PB_RATIOS = {"1x1": (1.0, 287), "2x3": (2 / 3, 46), "16x9": (16 / 9, 13)}


def _pb_circle(path):
    """A circular cut (alpha outside the circle), cached beside the set in _crops/. Cropping is fine (Bear, 2026-10-07)."""
    from PIL import Image as _Im, ImageDraw as _Dr
    out_dir = _os.path.join(_os.path.dirname(path), "_crops"); _os.makedirs(out_dir, exist_ok=True)
    out = _os.path.join(out_dir, _os.path.splitext(_os.path.basename(path))[0] + "-circle.png")
    if not _os.path.exists(out):
        im = _Im.open(path).convert("RGBA"); w, h = im.size; s = min(w, h); top = max(0, (h - s) // 3)
        im = im.crop(((w - s) // 2, top, (w - s) // 2 + s, top + s))
        mask = _Im.new("L", (s, s), 0); _Dr.Draw(mask).ellipse((0, 0, s - 1, s - 1), fill=255)
        im.putalpha(mask); im.save(out)
    return out


def professor_bear(ratio="2x3", height=3.0, seed=None, x=0.0, y=0.0, frame=True, shape="rect"):
    """A Professor Bear portrait (random within `ratio`; `seed` = the beat id for a stable pick across re-renders).
    Returns a Group: kraft drop shadow, the photo, an ink frame. Place with `x, y`; size with `height`.
    `shape="circle"` gives a round cut (use a 1x1 portrait). Cropping is fine: circle, rounded square, tight head shot."""
    import random as _random
    ar, n = _PB_RATIOS[ratio]
    k = _random.Random(str(seed) if seed is not None else None).randint(1, n)
    path = _os.path.join(_pb_dir(), f"professor-bear-{ratio}-{k:02d}.png")
    circle = shape == "circle"
    if circle:
        ar = 1.0
    w = height * ar
    if circle:
        shadow = Circle(radius=height / 2, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.12, y - 0.12, 0])
        border = Circle(radius=height / 2, stroke_color=INK, stroke_width=4, fill_opacity=0).move_to([x, y, 0])
    else:
        shadow = Rectangle(width=w, height=height, fill_color=BOX_L, fill_opacity=1, stroke_width=0).move_to([x + 0.12, y - 0.12, 0])
        border = Rectangle(width=w, height=height, stroke_color=INK, stroke_width=4, fill_opacity=0).move_to([x, y, 0])
    try:
        img = ImageMobject(_pb_circle(path) if circle else path)
        img.height = height
        img.move_to([x, y, 0])
    except Exception:
        img = Rectangle(width=w, height=height, fill_color=BAR2, fill_opacity=1, stroke_width=0).move_to([x, y, 0])
    g = Group(shadow, img, border) if frame else Group(img)
    g.path = path
    return g


# ═════════════════════════════ pacing (narration is the clock) ═════════════════════════════
try:
    _SHEET = _json.load(open(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "beat_sheet.json")))
    _TARGET = {b["beat_id"]: float(b.get("actual_duration_s") or b.get("estimated_duration_s") or 0) for b in _SHEET["beats"]}
    _NARR = {b["beat_id"]: b["narration_text"] for b in _SHEET["beats"]}
except Exception:
    _TARGET, _NARR = {}, {}


def _elapsed(self):
    rt = getattr(getattr(self, "renderer", None), "time", None)
    return float(rt) if isinstance(rt, (int, float)) else 0.0


def until(self, phrase, lead=0.25):
    """Wait until `phrase` is spoken (its character share of the narration × the measured audio)."""
    bid = type(self).__name__.split("_")[0]
    n, target = _NARR.get(bid, ""), _TARGET.get(bid, 0)
    if not n or not target or phrase not in n:
        return
    gap = target * n.index(phrase) / len(n) - lead - _elapsed(self)
    if gap > 0.05:
        self.wait(gap)


def finish(self):
    target = _TARGET.get(type(self).__name__.split("_")[0], 0)
    self.wait(max(0.3, target - _elapsed(self)) if target else 2.0)


"""Approved original Show-Tell props. Generated by scripts/build_original_props.py.
Paste into scenes.py; no sibling files required.
"""
_ST_ORIGINALS_25 = {'context-crate': {'parts': {'crate-back': [{'kind': 'polygon',
                                             'pts': [[0.0, 0.0],
                                                     [-2.0784609690826525, -1.2],
                                                     [-2.0784609690826525, -1.33],
                                                     [0.0, -0.13]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, 0.0],
                                                     [2.25166604983954, -1.3],
                                                     [2.25166604983954, -1.4300000000000002],
                                                     [0.0, -0.13]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, -0.13],
                                                     [2.25166604983954, -1.4300000000000002],
                                                     [0.17320508075688787, -2.63],
                                                     [-2.0784609690826525, -1.33]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.1477430013854075, -1.24],
                                                     [0.06928203230275515, -2.44],
                                                     [0.06928203230275515, -3.54],
                                                     [2.1477430013854075, -2.34]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.1477430013854075, -1.24],
                                                     [2.25166604983954, -1.3],
                                                     [2.25166604983954, -2.4000000000000004],
                                                     [2.1477430013854075, -2.34]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.1477430013854075, -2.34],
                                                     [2.25166604983954, -2.4000000000000004],
                                                     [0.17320508075688787, -3.6],
                                                     [0.06928203230275515, -3.54]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-1.9745379206285198, -1.14],
                                                     [-2.0784609690826525, -1.2],
                                                     [-2.0784609690826525, -2.3],
                                                     [-1.9745379206285198, -2.24]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-1.9745379206285198, -1.14],
                                                     [0.2771281292110206, -2.44],
                                                     [0.2771281292110206, -3.54],
                                                     [-1.9745379206285198, -2.24]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-1.9745379206285198, -2.24],
                                                     [0.2771281292110206, -3.54],
                                                     [0.17320508075688787, -3.6],
                                                     [-2.0784609690826525, -2.3]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035}],
                             'context': [{'kind': 'polygon',
                                          'pts': [[0.0, -0.6000000000000001],
                                                  [-1.299038105676658, -1.3499999999999999],
                                                  [-1.299038105676658, -1.42],
                                                  [0.0, -0.67]],
                                          'fill': '#ECE7DF',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.6000000000000001],
                                                  [1.4722431864335457, -1.45],
                                                  [1.4722431864335457, -1.52],
                                                  [0.0, -0.67]],
                                          'fill': '#E2DCD2',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.67],
                                                  [1.4722431864335457, -1.52],
                                                  [0.17320508075688787, -2.27],
                                                  [-1.299038105676658, -1.42]],
                                          'fill': '#FFFFFF',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polyline',
                                          'pts': [[-0.1299038105676657, -0.9500000000000001],
                                                  [0.9959292143521045, -1.6]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'polyline',
                                          'pts': [[-0.3897114317029973, -1.1], [0.7361215932167728, -1.75]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'polyline',
                                          'pts': [[-0.649519052838329, -1.25], [0.4763139720814413, -1.9]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'circle',
                                          'cx': -0.8660254037844385,
                                          'cy': -1.41,
                                          'r': 0.055,
                                          'fill': '#D97757',
                                          'stroke': 'none',
                                          'width': 0}],
                             'crate-front': [{'kind': 'polygon',
                                              'pts': [[0.0, 0.0],
                                                      [-2.0784609690826525, -1.2],
                                                      [-2.0784609690826525, -2.3],
                                                      [0.0, -1.1]],
                                              'fill': '#DCC9AA',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, 0.0],
                                                      [0.10392304845413262, -0.06],
                                                      [0.10392304845413262, -1.1600000000000001],
                                                      [0.0, -1.1]],
                                              'fill': '#C7AE86',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, -1.1],
                                                      [0.10392304845413262, -1.1600000000000001],
                                                      [-1.9745379206285198, -2.3600000000000003],
                                                      [-2.0784609690826525, -2.3]],
                                              'fill': '#F3E9D8',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, 0.0],
                                                      [-0.10392304845413262, -0.06],
                                                      [-0.10392304845413262, -1.1600000000000001],
                                                      [0.0, -1.1]],
                                              'fill': '#DCC9AA',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, 0.0],
                                                      [2.25166604983954, -1.3],
                                                      [2.25166604983954, -2.4000000000000004],
                                                      [0.0, -1.1]],
                                              'fill': '#C7AE86',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, -1.1],
                                                      [2.25166604983954, -2.4000000000000004],
                                                      [2.1477430013854075, -2.46],
                                                      [-0.10392304845413262, -1.1600000000000001]],
                                              'fill': '#F3E9D8',
                                              'stroke': '#3D3929',
                                              'width': 0.035}],
                             'lid': [{'kind': 'polygon',
                                      'pts': [[0.0, -1.0999999999999999],
                                              [-2.1823840175367852, -2.36],
                                              [-2.1823840175367852, -2.54],
                                              [0.0, -1.2799999999999998]],
                                      'fill': '#DCC9AA',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -1.0999999999999999],
                                              [2.3555890982936734, -2.46],
                                              [2.3555890982936734, -2.6399999999999997],
                                              [0.0, -1.2799999999999998]],
                                      'fill': '#C7AE86',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -1.2799999999999998],
                                              [2.3555890982936734, -2.6399999999999997],
                                              [0.17320508075688787, -3.9],
                                              [-2.1823840175367852, -2.54]],
                                      'fill': '#F3E9D8',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polyline',
                                      'pts': [[1.12583302491977, -2.0], [-0.9526279441628823, -3.2]],
                                      'fill': 'none',
                                      'stroke': '#8B8F96',
                                      'width': 0.18}]},
                   'moves': {'lid': [0.0, -1.0]}},
 'skill-stack': {'parts': {'pages': [{'kind': 'polygon',
                                      'pts': [[0.0, -0.0],
                                              [-2.0784609690826525, -1.2],
                                              [-2.0784609690826525, -1.27],
                                              [0.0, -0.07]],
                                      'fill': '#ECE7DF',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -0.0],
                                              [1.7320508075688772, -1.0],
                                              [1.7320508075688772, -1.07],
                                              [0.0, -0.07]],
                                      'fill': '#E2DCD2',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -0.07],
                                              [1.7320508075688772, -1.07],
                                              [-0.34641016151377535, -2.27],
                                              [-2.0784609690826525, -1.27]],
                                      'fill': '#FFFFFF',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polyline',
                                      'pts': [[-0.12990381056766576, -0.35000000000000003], [1.255736835487436, -1.15]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'polyline',
                                      'pts': [[-0.3897114317029974, -0.5], [0.9959292143521044, -1.3]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'polyline',
                                      'pts': [[-0.649519052838329, -0.6499999999999999], [0.7361215932167728, -1.45]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'circle',
                                      'cx': -1.6454482671904334,
                                      'cy': -1.26,
                                      'r': 0.055,
                                      'fill': '#D97757',
                                      'stroke': 'none',
                                      'width': 0},
                                     {'kind': 'polygon',
                                      'pts': [[0.025980762113533156, -0.245],
                                              [-2.0524802069691193, -1.4449999999999998],
                                              [-2.0524802069691193, -1.515],
                                              [0.025980762113533156, -0.315]],
                                      'fill': '#ECE7DF',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.025980762113533156, -0.245],
                                              [1.7580315696824105, -1.245],
                                              [1.7580315696824105, -1.315],
                                              [0.025980762113533156, -0.315]],
                                      'fill': '#E2DCD2',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.025980762113533156, -0.315],
                                              [1.7580315696824105, -1.315],
                                              [-0.320429399400242, -2.5149999999999997],
                                              [-2.0524802069691193, -1.515]],
                                      'fill': '#FFFFFF',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polyline',
                                      'pts': [[-0.10392304845413258, -0.595],
                                              [1.2817175976009694, -1.3950000000000002]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'polyline',
                                      'pts': [[-0.3637306695894642, -0.7450000000000001],
                                              [1.0219099764656376, -1.5450000000000002]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'polyline',
                                      'pts': [[-0.6235382907247957, -0.895], [0.762102355330306, -1.695]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'circle',
                                      'cx': -1.6194675050768998,
                                      'cy': -1.505,
                                      'r': 0.055,
                                      'fill': '#D97757',
                                      'stroke': 'none',
                                      'width': 0},
                                     {'kind': 'polygon',
                                      'pts': [[0.05196152422706631, -0.49],
                                              [-2.026499444855586, -1.6900000000000002],
                                              [-2.026499444855586, -1.7600000000000002],
                                              [0.05196152422706631, -0.56]],
                                      'fill': '#ECE7DF',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.05196152422706631, -0.49],
                                              [1.7840123317959435, -1.4900000000000002],
                                              [1.7840123317959435, -1.5600000000000003],
                                              [0.05196152422706631, -0.56]],
                                      'fill': '#E2DCD2',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.05196152422706631, -0.56],
                                              [1.7840123317959435, -1.5600000000000003],
                                              [-0.294448637286709, -2.7600000000000002],
                                              [-2.026499444855586, -1.7600000000000002]],
                                      'fill': '#FFFFFF',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polyline',
                                      'pts': [[-0.07794228634059949, -0.8400000000000001],
                                              [1.3076983597145022, -1.6400000000000001]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'polyline',
                                      'pts': [[-0.3377499074759311, -0.99], [1.0478907385791707, -1.79]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'polyline',
                                      'pts': [[-0.5975575286112625, -1.14], [0.7880831174438393, -1.94]],
                                      'fill': 'none',
                                      'stroke': '#D9D4C7',
                                      'width': 0.04},
                                     {'kind': 'circle',
                                      'cx': -1.593486742963367,
                                      'cy': -1.7500000000000002,
                                      'r': 0.055,
                                      'fill': '#D97757',
                                      'stroke': 'none',
                                      'width': 0}],
                           'selected-page': [{'kind': 'polygon',
                                              'pts': [[0.07794228634059945, -0.815],
                                                      [-2.000518682742053, -2.0149999999999997],
                                                      [-2.000518682742053, -2.085],
                                                      [0.07794228634059945, -0.885]],
                                              'fill': '#ECE7DF',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.07794228634059945, -0.815],
                                                      [1.8099930939094766, -1.815],
                                                      [1.8099930939094766, -1.885],
                                                      [0.07794228634059945, -0.885]],
                                              'fill': '#E2DCD2',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.07794228634059945, -0.885],
                                                      [1.8099930939094766, -1.885],
                                                      [-0.268467875173176, -3.085],
                                                      [-2.000518682742053, -2.085]],
                                              'fill': '#FFFFFF',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polyline',
                                              'pts': [[-0.051961524227066264, -1.165],
                                                      [1.333679121828035, -1.9649999999999999]],
                                              'fill': 'none',
                                              'stroke': '#D9D4C7',
                                              'width': 0.04},
                                             {'kind': 'polyline',
                                              'pts': [[-0.31176914536239786, -1.315],
                                                      [1.0738715006927038, -2.1149999999999998]],
                                              'fill': 'none',
                                              'stroke': '#D9D4C7',
                                              'width': 0.04},
                                             {'kind': 'polyline',
                                              'pts': [[-0.5715767664977294, -1.4649999999999999],
                                                      [0.814063879557372, -2.2649999999999997]],
                                              'fill': 'none',
                                              'stroke': '#D9D4C7',
                                              'width': 0.04},
                                             {'kind': 'circle',
                                              'cx': -1.567505980849834,
                                              'cy': -2.0749999999999997,
                                              'r': 0.055,
                                              'fill': '#D97757',
                                              'stroke': 'none',
                                              'width': 0}]},
                 'moves': {'selected-page': [0.9526279441628825, -1.15]}},
 'tool-block': {'parts': {'dock': [{'kind': 'polygon',
                                    'pts': [[0.0, 0.2],
                                            [-1.9918584287042087, -0.9499999999999998],
                                            [-1.9918584287042087, -1.15],
                                            [0.0, 0.0]],
                                    'fill': '#B4AFA6',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.0, 0.2],
                                            [2.25166604983954, -1.0999999999999999],
                                            [2.25166604983954, -1.2999999999999998],
                                            [0.0, 0.0]],
                                    'fill': '#8B8F96',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.0, 0.0],
                                            [2.25166604983954, -1.2999999999999998],
                                            [0.2598076211353318, -2.45],
                                            [-1.9918584287042087, -1.15]],
                                    'fill': '#D9D4C7',
                                    'stroke': '#3D3929',
                                    'width': 0.035}],
                          'tool': [{'kind': 'polygon',
                                    'pts': [[0.0, -0.23],
                                            [-1.6454482671904334, -1.18],
                                            [-1.6454482671904334, -2.33],
                                            [0.0, -1.38]],
                                    'fill': '#26221F',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.0, -0.23],
                                            [1.905255888325765, -1.33],
                                            [1.905255888325765, -2.48],
                                            [0.0, -1.38]],
                                    'fill': '#1E1B18',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.0, -1.38],
                                            [1.905255888325765, -2.48],
                                            [0.2598076211353318, -3.4299999999999997],
                                            [-1.6454482671904334, -2.33]],
                                    'fill': '#3A3530',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.44167295593006367, -0.645],
                                            [0.2944486372867091, -0.73],
                                            [0.2944486372867091, -1.03],
                                            [0.44167295593006367, -0.9450000000000001]],
                                    'fill': '#B4AFA6',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.44167295593006367, -0.645],
                                            [0.8313843876330611, -0.8700000000000001],
                                            [0.8313843876330611, -1.1700000000000002],
                                            [0.44167295593006367, -0.9450000000000001]],
                                    'fill': '#8B8F96',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.44167295593006367, -0.9450000000000001],
                                            [0.8313843876330611, -1.1700000000000002],
                                            [0.6841600689897065, -1.2550000000000001],
                                            [0.2944486372867091, -1.03]],
                                    'fill': '#D9D4C7',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[1.2210958193360584, -1.0950000000000002],
                                            [1.0738715006927038, -1.1800000000000002],
                                            [1.0738715006927038, -1.48],
                                            [1.2210958193360584, -1.395]],
                                    'fill': '#B4AFA6',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[1.2210958193360584, -1.0950000000000002],
                                            [1.6108072510390556, -1.32],
                                            [1.6108072510390556, -1.62],
                                            [1.2210958193360584, -1.395]],
                                    'fill': '#8B8F96',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[1.2210958193360584, -1.395],
                                            [1.6108072510390556, -1.62],
                                            [1.4635829323957013, -1.705],
                                            [1.0738715006927038, -1.48]],
                                    'fill': '#D9D4C7',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'circle',
                                    'cx': 1.1691342951089922,
                                    'cy': -2.565,
                                    'r': 0.07,
                                    'fill': '#D97757',
                                    'stroke': 'none',
                                    'width': 0}]},
                'moves': {'tool': [0.0, -0.9]}},
 'connector-pair': {'parts': {'socket': [{'kind': 'polygon',
                                          'pts': [[0.7794228634059948, -0.8500000000000001],
                                                  [-0.606217782649107, -1.65],
                                                  [-0.606217782649107, -2.45],
                                                  [0.7794228634059948, -1.6500000000000001]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.7794228634059948, -0.8500000000000001],
                                                  [2.0784609690826525, -1.5999999999999999],
                                                  [2.0784609690826525, -2.4],
                                                  [0.7794228634059948, -1.6500000000000001]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.7794228634059948, -1.6500000000000001],
                                                  [2.0784609690826525, -2.4],
                                                  [0.6928203230275507, -3.2],
                                                  [-0.606217782649107, -2.45]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.3163586137523466, -1.17],
                                                  [1.117172770881926, -1.285],
                                                  [1.117172770881926, -1.585],
                                                  [1.3163586137523466, -1.47]],
                                          'fill': '#B4AFA6',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.3163586137523466, -1.17],
                                                  [1.8792751262122316, -1.495],
                                                  [1.8792751262122316, -1.7950000000000002],
                                                  [1.3163586137523466, -1.47]],
                                          'fill': '#8B8F96',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.3163586137523466, -1.47],
                                                  [1.8792751262122316, -1.7950000000000002],
                                                  [1.6800892833418108, -1.9100000000000001],
                                                  [1.117172770881926, -1.585]],
                                          'fill': '#D9D4C7',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                              'plug': [{'kind': 'polygon',
                                        'pts': [[1.5588457268119893, -0.4099999999999999],
                                                [1.12583302491977, -0.6599999999999999],
                                                [1.12583302491977, -1.1099999999999999],
                                                [1.5588457268119893, -0.8599999999999999]],
                                        'fill': '#26221F',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.5588457268119893, -0.4099999999999999],
                                                [2.25166604983954, -0.8099999999999999],
                                                [2.25166604983954, -1.2599999999999998],
                                                [1.5588457268119893, -0.8599999999999999]],
                                        'fill': '#1E1B18',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.5588457268119893, -0.8599999999999999],
                                                [2.25166604983954, -1.2599999999999998],
                                                [1.818653347947321, -1.5099999999999998],
                                                [1.12583302491977, -1.1099999999999999]],
                                        'fill': '#3A3530',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.2210958193360586, -0.835],
                                                [0.961288198200727, -0.985],
                                                [0.961288198200727, -1.115],
                                                [1.2210958193360586, -0.965]],
                                        'fill': '#B4AFA6',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.2210958193360586, -0.835],
                                                [1.3336791218280355, -0.9000000000000001],
                                                [1.3336791218280355, -1.0300000000000002],
                                                [1.2210958193360586, -0.965]],
                                        'fill': '#8B8F96',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.2210958193360586, -0.965],
                                                [1.3336791218280355, -1.0300000000000002],
                                                [1.073871500692704, -1.1800000000000002],
                                                [0.961288198200727, -1.115]],
                                        'fill': '#D9D4C7',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.5415252187363004, -1.02],
                                                [1.2817175976009691, -1.17],
                                                [1.2817175976009691, -1.2999999999999998],
                                                [1.5415252187363004, -1.15]],
                                        'fill': '#B4AFA6',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.5415252187363004, -1.02],
                                                [1.6541085212282776, -1.085],
                                                [1.6541085212282776, -1.2149999999999999],
                                                [1.5415252187363004, -1.15]],
                                        'fill': '#8B8F96',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.5415252187363004, -1.15],
                                                [1.6541085212282776, -1.2149999999999999],
                                                [1.394300900092946, -1.3649999999999998],
                                                [1.2817175976009691, -1.2999999999999998]],
                                        'fill': '#D9D4C7',
                                        'stroke': '#3D3929',
                                        'width': 0.035}]},
                    'moves': {'plug': [0.08660254037844384, -0.37]}},
 'server-tower': {'parts': {'rack': [{'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [-1.6454482671904334, -0.95],
                                              [-1.6454482671904334, -1.47],
                                              [0.0, -0.52]],
                                      'fill': '#26221F',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [1.7320508075688772, -1.0],
                                              [1.7320508075688772, -1.52],
                                              [0.0, -0.52]],
                                      'fill': '#1E1B18',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -0.52],
                                              [1.7320508075688772, -1.52],
                                              [0.08660254037844393, -2.4699999999999998],
                                              [-1.6454482671904334, -1.47]],
                                      'fill': '#3A3530',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'circle',
                                      'cx': 0.27712812921102037,
                                      'cy': -0.39,
                                      'r': 0.06,
                                      'fill': '#D9D4C7',
                                      'stroke': 'none',
                                      'width': 0},
                                     {'kind': 'polyline',
                                      'pts': [[0.6192081637058736, -0.5925], [1.3986310271118683, -1.0425]],
                                      'fill': 'none',
                                      'stroke': '#8B8F96',
                                      'width': 0.06},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -0.65],
                                              [-1.6454482671904334, -1.6],
                                              [-1.6454482671904334, -2.12],
                                              [0.0, -1.17]],
                                      'fill': '#26221F',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -0.65],
                                              [1.7320508075688772, -1.65],
                                              [1.7320508075688772, -2.17],
                                              [0.0, -1.17]],
                                      'fill': '#1E1B18',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -1.17],
                                              [1.7320508075688772, -2.17],
                                              [0.08660254037844393, -3.12],
                                              [-1.6454482671904334, -2.12]],
                                      'fill': '#3A3530',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'circle',
                                      'cx': 0.27712812921102037,
                                      'cy': -1.04,
                                      'r': 0.06,
                                      'fill': '#D9D4C7',
                                      'stroke': 'none',
                                      'width': 0},
                                     {'kind': 'polyline',
                                      'pts': [[0.6192081637058736, -1.2425], [1.3986310271118683, -1.6925000000000001]],
                                      'fill': 'none',
                                      'stroke': '#8B8F96',
                                      'width': 0.06}],
                            'node': [{'kind': 'polygon',
                                      'pts': [[0.0, -1.3],
                                              [-1.6454482671904334, -2.25],
                                              [-1.6454482671904334, -2.77],
                                              [0.0, -1.82]],
                                      'fill': '#26221F',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -1.3],
                                              [1.7320508075688772, -2.3],
                                              [1.7320508075688772, -2.8200000000000003],
                                              [0.0, -1.82]],
                                      'fill': '#1E1B18',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -1.82],
                                              [1.7320508075688772, -2.8200000000000003],
                                              [0.08660254037844393, -3.77],
                                              [-1.6454482671904334, -2.77]],
                                      'fill': '#3A3530',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'circle',
                                      'cx': 0.27712812921102037,
                                      'cy': -1.69,
                                      'r': 0.06,
                                      'fill': '#D97757',
                                      'stroke': 'none',
                                      'width': 0},
                                     {'kind': 'polyline',
                                      'pts': [[0.6192081637058736, -1.8925], [1.3986310271118683, -2.3425000000000002]],
                                      'fill': 'none',
                                      'stroke': '#8B8F96',
                                      'width': 0.06}]},
                  'moves': {'node': [0.0, -0.65]}},
 'memory-drawers': {'parts': {'cabinet': [{'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [-1.3856406460551018, -0.8],
                                                   [-1.3856406460551018, -2.8],
                                                   [0.0, -2.0]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [1.7320508075688772, -1.0],
                                                   [1.7320508075688772, -3.0],
                                                   [0.0, -2.0]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, -2.0],
                                                   [1.7320508075688772, -3.0],
                                                   [0.34641016151377535, -3.8],
                                                   [-1.3856406460551018, -2.8]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035}],
                              'fixed-drawer-0': [{'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -0.16499999999999998],
                                                          [-0.9266471820493491, -0.8150000000000001],
                                                          [-0.9266471820493491, -1.275],
                                                          [0.19918584287042088, -0.625]],
                                                  'fill': '#B4AFA6',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -0.16499999999999998],
                                                          [1.7060700454553441, -1.035],
                                                          [1.7060700454553441, -1.495],
                                                          [0.19918584287042088, -0.625]],
                                                  'fill': '#8B8F96',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -0.625],
                                                          [1.7060700454553441, -1.495],
                                                          [0.580237020535574, -2.145],
                                                          [-0.9266471820493491, -1.275]],
                                                  'fill': '#D9D4C7',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -0.515],
                                                          [0.6408587988004846, -0.5900000000000001],
                                                          [0.6408587988004846, -0.68],
                                                          [0.7707626093681503, -0.605]],
                                                  'fill': '#26221F',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -0.515],
                                                          [1.3336791218280355, -0.8400000000000001],
                                                          [1.3336791218280355, -0.93],
                                                          [0.7707626093681503, -0.605]],
                                                  'fill': '#1E1B18',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -0.605],
                                                          [1.3336791218280355, -0.93],
                                                          [1.2037753112603697, -1.005],
                                                          [0.6408587988004846, -0.68]],
                                                  'fill': '#3A3530',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035}],
                              'drawer': [{'kind': 'polygon',
                                          'pts': [[0.19918584287042088, -0.765],
                                                  [-0.9266471820493491, -1.415],
                                                  [-0.9266471820493491, -1.875],
                                                  [0.19918584287042088, -1.2249999999999999]],
                                          'fill': '#B4AFA6',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.19918584287042088, -0.765],
                                                  [1.7060700454553441, -1.635],
                                                  [1.7060700454553441, -2.0949999999999998],
                                                  [0.19918584287042088, -1.2249999999999999]],
                                          'fill': '#8B8F96',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.19918584287042088, -1.2249999999999999],
                                                  [1.7060700454553441, -2.0949999999999998],
                                                  [0.580237020535574, -2.745],
                                                  [-0.9266471820493491, -1.875]],
                                          'fill': '#D9D4C7',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.7707626093681503, -1.115],
                                                  [0.6408587988004846, -1.19],
                                                  [0.6408587988004846, -1.2799999999999998],
                                                  [0.7707626093681503, -1.2049999999999998]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.7707626093681503, -1.115],
                                                  [1.3336791218280355, -1.44],
                                                  [1.3336791218280355, -1.5299999999999998],
                                                  [0.7707626093681503, -1.2049999999999998]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.7707626093681503, -1.2049999999999998],
                                                  [1.3336791218280355, -1.5299999999999998],
                                                  [1.2037753112603697, -1.605],
                                                  [0.6408587988004846, -1.2799999999999998]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                              'fixed-drawer-2': [{'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -1.3649999999999998],
                                                          [-0.9266471820493491, -2.0149999999999997],
                                                          [-0.9266471820493491, -2.4749999999999996],
                                                          [0.19918584287042088, -1.8249999999999997]],
                                                  'fill': '#B4AFA6',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -1.3649999999999998],
                                                          [1.7060700454553441, -2.235],
                                                          [1.7060700454553441, -2.695],
                                                          [0.19918584287042088, -1.8249999999999997]],
                                                  'fill': '#8B8F96',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.19918584287042088, -1.8249999999999997],
                                                          [1.7060700454553441, -2.695],
                                                          [0.580237020535574, -3.3449999999999998],
                                                          [-0.9266471820493491, -2.4749999999999996]],
                                                  'fill': '#D9D4C7',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -1.715],
                                                          [0.6408587988004846, -1.79],
                                                          [0.6408587988004846, -1.8800000000000001],
                                                          [0.7707626093681503, -1.8050000000000002]],
                                                  'fill': '#26221F',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -1.715],
                                                          [1.3336791218280355, -2.04],
                                                          [1.3336791218280355, -2.13],
                                                          [0.7707626093681503, -1.8050000000000002]],
                                                  'fill': '#1E1B18',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.7707626093681503, -1.8050000000000002],
                                                          [1.3336791218280355, -2.13],
                                                          [1.2037753112603697, -2.205],
                                                          [0.6408587988004846, -1.8800000000000001]],
                                                  'fill': '#3A3530',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035}],
                              'cabinet-top': [{'kind': 'polygon',
                                               'pts': [[0.0, -1.96],
                                                       [-1.3856406460551018, -2.76],
                                                       [-1.3856406460551018, -2.88],
                                                       [0.0, -2.08]],
                                               'fill': '#DCC9AA',
                                               'stroke': '#3D3929',
                                               'width': 0.035},
                                              {'kind': 'polygon',
                                               'pts': [[0.0, -1.96],
                                                       [1.7320508075688772, -2.96],
                                                       [1.7320508075688772, -3.08],
                                                       [0.0, -2.08]],
                                               'fill': '#C7AE86',
                                               'stroke': '#3D3929',
                                               'width': 0.035},
                                              {'kind': 'polygon',
                                               'pts': [[0.0, -2.08],
                                                       [1.7320508075688772, -3.08],
                                                       [0.34641016151377535, -3.88],
                                                       [-1.3856406460551018, -2.88]],
                                               'fill': '#F3E9D8',
                                               'stroke': '#3D3929',
                                               'width': 0.035}]},
                    'moves': {'drawer': [0.7794228634059948, 0.45]}},
 'context-inbox': {'parts': {'tray-back': [{'kind': 'polygon',
                                            'pts': [[0.0, 0.0],
                                                    [-2.25166604983954, -1.3],
                                                    [-2.25166604983954, -1.4300000000000002],
                                                    [0.0, -0.13]],
                                            'fill': '#DCC9AA',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, 0.0],
                                                    [2.25166604983954, -1.3],
                                                    [2.25166604983954, -1.4300000000000002],
                                                    [0.0, -0.13]],
                                            'fill': '#C7AE86',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.13],
                                                    [2.25166604983954, -1.4300000000000002],
                                                    [0.0, -2.73],
                                                    [-2.25166604983954, -1.4300000000000002]],
                                            'fill': '#F3E9D8',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[2.1477430013854075, -1.24],
                                                    [-0.10392304845413272, -2.54],
                                                    [-0.10392304845413272, -2.99],
                                                    [2.1477430013854075, -1.69]],
                                            'fill': '#DCC9AA',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[2.1477430013854075, -1.24],
                                                    [2.25166604983954, -1.3],
                                                    [2.25166604983954, -1.75],
                                                    [2.1477430013854075, -1.69]],
                                            'fill': '#C7AE86',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[2.1477430013854075, -1.69],
                                                    [2.25166604983954, -1.75],
                                                    [0.0, -3.0500000000000003],
                                                    [-0.10392304845413272, -2.99]],
                                            'fill': '#F3E9D8',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-2.1477430013854075, -1.24],
                                                    [-2.25166604983954, -1.3],
                                                    [-2.25166604983954, -1.75],
                                                    [-2.1477430013854075, -1.69]],
                                            'fill': '#DCC9AA',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-2.1477430013854075, -1.24],
                                                    [0.10392304845413272, -2.54],
                                                    [0.10392304845413272, -2.99],
                                                    [-2.1477430013854075, -1.69]],
                                            'fill': '#C7AE86',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-2.1477430013854075, -1.69],
                                                    [0.10392304845413272, -2.99],
                                                    [0.0, -3.0500000000000003],
                                                    [-2.25166604983954, -1.75]],
                                            'fill': '#F3E9D8',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                             'records': [{'kind': 'polygon',
                                          'pts': [[0.0, -0.47],
                                                  [-1.732050807568877, -1.4699999999999998],
                                                  [-1.732050807568877, -1.5399999999999998],
                                                  [0.0, -0.54]],
                                          'fill': '#ECE7DF',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.47],
                                                  [1.732050807568877, -1.4699999999999998],
                                                  [1.732050807568877, -1.5399999999999998],
                                                  [0.0, -0.54]],
                                          'fill': '#E2DCD2',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.54],
                                                  [1.732050807568877, -1.5399999999999998],
                                                  [0.0, -2.54],
                                                  [-1.732050807568877, -1.5399999999999998]],
                                          'fill': '#FFFFFF',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polyline',
                                          'pts': [[-0.1299038105676657, -0.82],
                                                  [1.2557368354874356, -1.6199999999999997]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'polyline',
                                          'pts': [[-0.3897114317029973, -0.97], [0.9959292143521041, -1.77]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'polyline',
                                          'pts': [[-0.649519052838329, -1.12], [0.7361215932167725, -1.92]],
                                          'fill': 'none',
                                          'stroke': '#D9D4C7',
                                          'width': 0.04},
                                         {'kind': 'circle',
                                          'cx': -1.2990381056766578,
                                          'cy': -1.5299999999999998,
                                          'r': 0.055,
                                          'fill': '#D97757',
                                          'stroke': 'none',
                                          'width': 0}],
                             'new-page': [{'kind': 'polygon',
                                           'pts': [[0.0, -0.64],
                                                   [-1.732050807568877, -1.64],
                                                   [-1.732050807568877, -1.71],
                                                   [0.0, -0.71]],
                                           'fill': '#ECE7DF',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, -0.64],
                                                   [1.732050807568877, -1.64],
                                                   [1.732050807568877, -1.71],
                                                   [0.0, -0.71]],
                                           'fill': '#E2DCD2',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, -0.71],
                                                   [1.732050807568877, -1.71],
                                                   [0.0, -2.71],
                                                   [-1.732050807568877, -1.71]],
                                           'fill': '#FFFFFF',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polyline',
                                           'pts': [[-0.1299038105676657, -0.99],
                                                   [1.2557368354874356, -1.7899999999999998]],
                                           'fill': 'none',
                                           'stroke': '#D9D4C7',
                                           'width': 0.04},
                                          {'kind': 'polyline',
                                           'pts': [[-0.3897114317029973, -1.1400000000000001],
                                                   [0.9959292143521041, -1.94]],
                                           'fill': 'none',
                                           'stroke': '#D9D4C7',
                                           'width': 0.04},
                                          {'kind': 'polyline',
                                           'pts': [[-0.649519052838329, -1.29], [0.7361215932167725, -2.09]],
                                           'fill': 'none',
                                           'stroke': '#D9D4C7',
                                           'width': 0.04},
                                          {'kind': 'circle',
                                           'cx': -1.2990381056766578,
                                           'cy': -1.6999999999999997,
                                           'r': 0.055,
                                           'fill': '#D97757',
                                           'stroke': 'none',
                                           'width': 0}],
                             'tray-front': [{'kind': 'polygon',
                                             'pts': [[0.0, 0.0],
                                                     [-2.25166604983954, -1.3],
                                                     [-2.25166604983954, -1.75],
                                                     [0.0, -0.45]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, 0.0],
                                                     [0.10392304845413262, -0.06],
                                                     [0.10392304845413262, -0.51],
                                                     [0.0, -0.45]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, -0.45],
                                                     [0.10392304845413262, -0.51],
                                                     [-2.1477430013854075, -1.81],
                                                     [-2.25166604983954, -1.75]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, 0.0],
                                                     [-0.10392304845413262, -0.06],
                                                     [-0.10392304845413262, -0.51],
                                                     [0.0, -0.45]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, 0.0],
                                                     [2.25166604983954, -1.3],
                                                     [2.25166604983954, -1.75],
                                                     [0.0, -0.45]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.0, -0.45],
                                                     [2.25166604983954, -1.75],
                                                     [2.1477430013854075, -1.81],
                                                     [-0.10392304845413262, -0.51]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035}]},
                   'moves': {'new-page': [0.0, -1.1]}},
 'agent-workstation': {'parts': {'foot': [{'kind': 'polygon',
                                           'pts': [[-0.17320508075688767, -0.5],
                                                   [-1.1258330249197703, -1.05],
                                                   [-1.1258330249197703, -1.2],
                                                   [-0.17320508075688767, -0.65]],
                                           'fill': '#B4AFA6',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-0.17320508075688767, -0.5],
                                                   [1.4722431864335455, -1.45],
                                                   [1.4722431864335455, -1.5999999999999999],
                                                   [-0.17320508075688767, -0.65]],
                                           'fill': '#8B8F96',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-0.17320508075688767, -0.65],
                                                   [1.4722431864335455, -1.5999999999999999],
                                                   [0.5196152422706628, -2.15],
                                                   [-1.1258330249197703, -1.2]],
                                           'fill': '#D9D4C7',
                                           'stroke': '#3D3929',
                                           'width': 0.035}],
                                 'stand': [{'kind': 'polygon',
                                            'pts': [[0.08660254037844393, -1.21],
                                                    [-0.17320508075688767, -1.36],
                                                    [-0.17320508075688767, -1.9600000000000002],
                                                    [0.08660254037844393, -1.81]],
                                            'fill': '#26221F',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844393, -1.21],
                                                    [0.34641016151377557, -1.36],
                                                    [0.34641016151377557, -1.9600000000000002],
                                                    [0.08660254037844393, -1.81]],
                                            'fill': '#1E1B18',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844393, -1.81],
                                                    [0.34641016151377557, -1.9600000000000002],
                                                    [0.08660254037844393, -2.1100000000000003],
                                                    [-0.17320508075688767, -1.9600000000000002]],
                                            'fill': '#3A3530',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                                 'screen': [{'kind': 'polygon',
                                             'pts': [[-0.8660254037844386, -1.26],
                                                     [-1.0392304845413263, -1.3599999999999999],
                                                     [-1.0392304845413263, -3.0100000000000002],
                                                     [-0.8660254037844386, -2.91]],
                                             'fill': '#26221F',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.8660254037844386, -1.26],
                                                     [1.4722431864335457, -2.6100000000000003],
                                                     [1.4722431864335457, -4.26],
                                                     [-0.8660254037844386, -2.91]],
                                             'fill': '#1E1B18',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.8660254037844386, -2.91],
                                                     [1.4722431864335457, -4.26],
                                                     [1.299038105676658, -4.36],
                                                     [-1.0392304845413263, -3.0100000000000002]],
                                             'fill': '#3A3530',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.7361215932167728, -1.505],
                                                     [1.3596598839415686, -2.715],
                                                     [1.3596598839415686, -4.025],
                                                     [-0.7361215932167728, -2.815]],
                                             'fill': '#FAF9F5',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[-0.49363448015712996, -1.885], [0.7188010851410841, -2.585]],
                                             'fill': 'none',
                                             'stroke': '#8B8F96',
                                             'width': 0.06},
                                            {'kind': 'polyline',
                                             'pts': [[-0.49363448015712996, -2.185], [0.7188010851410841, -2.885]],
                                             'fill': 'none',
                                             'stroke': '#8B8F96',
                                             'width': 0.06},
                                            {'kind': 'polyline',
                                             'pts': [[-0.49363448015712996, -2.4850000000000003],
                                                     [0.7188010851410841, -3.185]],
                                             'fill': 'none',
                                             'stroke': '#8B8F96',
                                             'width': 0.06}],
                                 'tool': [{'kind': 'polygon',
                                           'pts': [[2.598076211353316, -1.2000000000000002],
                                                   [1.905255888325765, -1.6],
                                                   [1.905255888325765, -2.1500000000000004],
                                                   [2.598076211353316, -1.7500000000000002]],
                                           'fill': '#26221F',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[2.598076211353316, -1.2000000000000002],
                                                   [3.334197804570089, -1.6250000000000002],
                                                   [3.334197804570089, -2.1750000000000003],
                                                   [2.598076211353316, -1.7500000000000002]],
                                           'fill': '#1E1B18',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[2.598076211353316, -1.7500000000000002],
                                                   [3.334197804570089, -2.1750000000000003],
                                                   [2.641377481542538, -2.575],
                                                   [1.905255888325765, -2.1500000000000004]],
                                           'fill': '#3A3530',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'circle',
                                           'cx': 2.9618068809427798,
                                           'cy': -1.6700000000000002,
                                           'r': 0.07,
                                           'fill': '#D97757',
                                           'stroke': 'none',
                                           'width': 0}]},
                       'moves': {'tool': [-0.4763139720814413, 0.575]}},
 'review-desk': {'parts': {'legs': [{'kind': 'polygon',
                                     'pts': [[0.0, 0.0],
                                             [-0.13856406460551018, -0.08],
                                             [-0.13856406460551018, -1.28],
                                             [0.0, -1.2]],
                                     'fill': '#26221F',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.0, 0.0],
                                             [0.13856406460551018, -0.08],
                                             [0.13856406460551018, -1.28],
                                             [0.0, -1.2]],
                                     'fill': '#1E1B18',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.0, -1.2],
                                             [0.13856406460551018, -1.28],
                                             [0.0, -1.3599999999999999],
                                             [-0.13856406460551018, -1.28]],
                                     'fill': '#3A3530',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.1650635094610964, -1.25],
                                             [2.026499444855586, -1.33],
                                             [2.026499444855586, -2.5300000000000002],
                                             [2.1650635094610964, -2.45]],
                                     'fill': '#26221F',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.1650635094610964, -1.25],
                                             [2.303627574066607, -1.33],
                                             [2.303627574066607, -2.5300000000000002],
                                             [2.1650635094610964, -2.45]],
                                     'fill': '#1E1B18',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.1650635094610964, -2.45],
                                             [2.303627574066607, -2.5300000000000002],
                                             [2.1650635094610964, -2.6100000000000003],
                                             [2.026499444855586, -2.5300000000000002]],
                                     'fill': '#3A3530',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[-1.4289419162443235, -0.825],
                                             [-1.5675059808498337, -0.9049999999999999],
                                             [-1.5675059808498337, -2.105],
                                             [-1.4289419162443235, -2.025]],
                                     'fill': '#26221F',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[-1.4289419162443235, -0.825],
                                             [-1.2903778516388136, -0.9049999999999999],
                                             [-1.2903778516388136, -2.105],
                                             [-1.4289419162443235, -2.025]],
                                     'fill': '#1E1B18',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[-1.4289419162443235, -2.025],
                                             [-1.2903778516388136, -2.105],
                                             [-1.4289419162443235, -2.1849999999999996],
                                             [-1.5675059808498337, -2.105]],
                                     'fill': '#3A3530',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.7361215932167728, -2.075],
                                             [0.5975575286112628, -2.155],
                                             [0.5975575286112628, -3.3549999999999995],
                                             [0.7361215932167728, -3.2750000000000004]],
                                     'fill': '#26221F',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.7361215932167728, -2.075],
                                             [0.8746856578222831, -2.1550000000000002],
                                             [0.8746856578222831, -3.3550000000000004],
                                             [0.7361215932167728, -3.2750000000000004]],
                                     'fill': '#1E1B18',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.7361215932167728, -3.2750000000000004],
                                             [0.8746856578222831, -3.3550000000000004],
                                             [0.7361215932167731, -3.4349999999999996],
                                             [0.5975575286112628, -3.3549999999999995]],
                                     'fill': '#3A3530',
                                     'stroke': '#3D3929',
                                     'width': 0.035}],
                           'desktop': [{'kind': 'polygon',
                                        'pts': [[0.0, -1.0999999999999999],
                                                [-1.7320508075688772, -2.0999999999999996],
                                                [-1.7320508075688772, -2.26],
                                                [0.0, -1.2599999999999998]],
                                        'fill': '#DCC9AA',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[0.0, -1.0999999999999999],
                                                [2.5114736709748717, -2.55],
                                                [2.5114736709748717, -2.71],
                                                [0.0, -1.2599999999999998]],
                                        'fill': '#C7AE86',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[0.0, -1.2599999999999998],
                                                [2.5114736709748717, -2.71],
                                                [0.7794228634059946, -3.7099999999999995],
                                                [-1.7320508075688772, -2.26]],
                                        'fill': '#F3E9D8',
                                        'stroke': '#3D3929',
                                        'width': 0.035}],
                           'evidence': [{'kind': 'polygon',
                                         'pts': [[0.38971143170299744, -1.7249999999999999],
                                                 [-0.9093266739736605, -2.475],
                                                 [-0.9093266739736605, -2.545],
                                                 [0.38971143170299744, -1.795]],
                                         'fill': '#ECE7DF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.38971143170299744, -1.7249999999999999],
                                                 [1.688749537379655, -2.4749999999999996],
                                                 [1.688749537379655, -2.545],
                                                 [0.38971143170299744, -1.795]],
                                         'fill': '#E2DCD2',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.38971143170299744, -1.795],
                                                 [1.688749537379655, -2.545],
                                                 [0.38971143170299716, -3.295],
                                                 [-0.9093266739736605, -2.545]],
                                         'fill': '#FFFFFF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polyline',
                                         'pts': [[0.2598076211353316, -2.0749999999999997],
                                                 [1.212435565298214, -2.625]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[0.0, -2.2249999999999996], [0.9526279441628823, -2.7749999999999995]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[-0.2598076211353316, -2.375], [0.6928203230275507, -2.925]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'circle',
                                         'cx': -0.4763139720814413,
                                         'cy': -2.535,
                                         'r': 0.055,
                                         'fill': '#D97757',
                                         'stroke': 'none',
                                         'width': 0}]},
                 'moves': {'evidence': [1.12583302491977, 0.19999999999999998]}},
 'permission-gate': {'parts': {'base': [{'kind': 'polygon',
                                         'pts': [[0.0, 0.1],
                                                 [-1.299038105676658, -0.6499999999999999],
                                                 [-1.299038105676658, -0.7799999999999999],
                                                 [0.0, -0.03]],
                                         'fill': '#B4AFA6',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, 0.1],
                                                 [2.68467875173176, -1.45],
                                                 [2.68467875173176, -1.58],
                                                 [0.0, -0.03]],
                                         'fill': '#8B8F96',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -0.03],
                                                 [2.68467875173176, -1.58],
                                                 [1.3856406460551018, -2.33],
                                                 [-1.299038105676658, -0.7799999999999999]],
                                         'fill': '#D9D4C7',
                                         'stroke': '#3D3929',
                                         'width': 0.035}],
                               'posts': [{'kind': 'polygon',
                                          'pts': [[-0.5196152422706631, -0.43],
                                                  [-0.8227241335952167, -0.605],
                                                  [-0.8227241335952167, -2.305],
                                                  [-0.5196152422706631, -2.13]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[-0.5196152422706631, -0.43],
                                                  [-0.2771281292110203, -0.5700000000000001],
                                                  [-0.2771281292110203, -2.27],
                                                  [-0.5196152422706631, -2.13]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[-0.5196152422706631, -2.13],
                                                  [-0.2771281292110203, -2.27],
                                                  [-0.5802370205355738, -2.4450000000000003],
                                                  [-0.8227241335952167, -2.305]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.6454482671904334, -1.6800000000000002],
                                                  [1.34233937586588, -1.855],
                                                  [1.34233937586588, -3.555],
                                                  [1.6454482671904334, -3.38]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.6454482671904334, -1.6800000000000002],
                                                  [1.8879353802500762, -1.8200000000000003],
                                                  [1.8879353802500762, -3.5200000000000005],
                                                  [1.6454482671904334, -3.38]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.6454482671904334, -3.38],
                                                  [1.8879353802500762, -3.5200000000000005],
                                                  [1.5848264889255228, -3.6950000000000003],
                                                  [1.34233937586588, -3.555]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'circle',
                                          'cx': -0.38105117766515295,
                                          'cy': -1.96,
                                          'r': 0.07,
                                          'fill': '#D97757',
                                          'stroke': 'none',
                                          'width': 0}],
                               'barrier': [{'kind': 'polygon',
                                            'pts': [[-0.2424871130596428, -1.3399999999999999],
                                                    [-0.381051177665153, -1.42],
                                                    [-0.381051177665153, -1.69],
                                                    [-0.2424871130596428, -1.6099999999999999]],
                                            'fill': '#DCC9AA',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-0.2424871130596428, -1.3399999999999999],
                                                    [1.749371315644566, -2.49],
                                                    [1.749371315644566, -2.76],
                                                    [-0.2424871130596428, -1.6099999999999999]],
                                            'fill': '#C7AE86',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-0.2424871130596428, -1.6099999999999999],
                                                    [1.749371315644566, -2.76],
                                                    [1.6108072510390556, -2.84],
                                                    [-0.381051177665153, -1.69]],
                                            'fill': '#F3E9D8',
                                            'stroke': '#3D3929',
                                            'width': 0.035}]},
                     'moves': {'barrier': [0.0, -0.95]}},
 'approval-stamp': {'parts': {'document': [{'kind': 'polygon',
                                            'pts': [[0.0, 0.0],
                                                    [-2.1650635094610964, -1.25],
                                                    [-2.1650635094610964, -1.32],
                                                    [0.0, -0.07]],
                                            'fill': '#ECE7DF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, 0.0],
                                                    [1.9918584287042087, -1.15],
                                                    [1.9918584287042087, -1.22],
                                                    [0.0, -0.07]],
                                            'fill': '#E2DCD2',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.07],
                                                    [1.9918584287042087, -1.22],
                                                    [-0.17320508075688787, -2.4699999999999998],
                                                    [-2.1650635094610964, -1.32]],
                                            'fill': '#FFFFFF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polyline',
                                            'pts': [[-0.12990381056766576, -0.35000000000000003],
                                                    [1.5155444566227672, -1.2999999999999998]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.3897114317029974, -0.5],
                                                    [1.2557368354874356, -1.4499999999999997]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.649519052838329, -0.6499999999999999],
                                                    [0.9959292143521041, -1.5999999999999999]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'circle',
                                            'cx': -1.7320508075688772,
                                            'cy': -1.31,
                                            'r': 0.055,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0}],
                              'stamp': [{'kind': 'polygon',
                                         'pts': [[0.0, -1.25],
                                                 [-0.9526279441628825, -1.7999999999999998],
                                                 [-0.9526279441628825, -2.0],
                                                 [0.0, -1.4500000000000002]],
                                         'fill': '#26221F',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.25],
                                                 [0.9526279441628825, -1.7999999999999998],
                                                 [0.9526279441628825, -2.0],
                                                 [0.0, -1.4500000000000002]],
                                         'fill': '#1E1B18',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.4500000000000002],
                                                 [0.9526279441628825, -2.0],
                                                 [0.0, -2.55],
                                                 [-0.9526279441628825, -2.0]],
                                         'fill': '#3A3530',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.85],
                                                 [-0.2598076211353316, -2.0],
                                                 [-0.2598076211353316, -2.6],
                                                 [0.0, -2.45]],
                                         'fill': '#DCC9AA',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.85],
                                                 [0.2598076211353316, -2.0],
                                                 [0.2598076211353316, -2.6],
                                                 [0.0, -2.45]],
                                         'fill': '#C7AE86',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -2.45],
                                                 [0.2598076211353316, -2.6],
                                                 [0.0, -2.75],
                                                 [-0.2598076211353316, -2.6]],
                                         'fill': '#F3E9D8',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -2.15],
                                                 [-0.7794228634059946, -2.5999999999999996],
                                                 [-0.7794228634059946, -2.7699999999999996],
                                                 [0.0, -2.32]],
                                         'fill': '#DCC9AA',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -2.15],
                                                 [0.7794228634059946, -2.5999999999999996],
                                                 [0.7794228634059946, -2.7699999999999996],
                                                 [0.0, -2.32]],
                                         'fill': '#C7AE86',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -2.32],
                                                 [0.7794228634059946, -2.7699999999999996],
                                                 [0.0, -3.2199999999999998],
                                                 [-0.7794228634059946, -2.7699999999999996]],
                                         'fill': '#F3E9D8',
                                         'stroke': '#3D3929',
                                         'width': 0.035}]},
                    'moves': {'stamp': [0.0, 0.5]}},
 'secure-vault': {'parts': {'body': [{'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [-1.5588457268119895, -0.9],
                                              [-1.5588457268119895, -2.9],
                                              [0.0, -2.0]],
                                      'fill': '#26221F',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [1.9918584287042087, -1.15],
                                              [1.9918584287042087, -3.15],
                                              [0.0, -2.0]],
                                      'fill': '#1E1B18',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -2.0],
                                              [1.9918584287042087, -3.15],
                                              [0.43301270189221913, -4.05],
                                              [-1.5588457268119895, -2.9]],
                                      'fill': '#3A3530',
                                      'stroke': '#3D3929',
                                      'width': 0.035}],
                            'door': [{'kind': 'polygon',
                                      'pts': [[0.25114736709748725, -0.20500000000000002],
                                              [0.12124355652982141, -0.28],
                                              [0.12124355652982141, -1.92],
                                              [0.25114736709748725, -1.8449999999999998]],
                                      'fill': '#B4AFA6',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.25114736709748725, -0.20500000000000002],
                                              [1.9485571585149868, -1.1849999999999998],
                                              [1.9485571585149868, -2.8249999999999997],
                                              [0.25114736709748725, -1.8449999999999998]],
                                      'fill': '#8B8F96',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.25114736709748725, -1.8449999999999998],
                                              [1.9485571585149868, -2.8249999999999997],
                                              [1.818653347947321, -2.8999999999999995],
                                              [0.12124355652982141, -1.92]],
                                      'fill': '#D9D4C7',
                                      'stroke': '#3D3929',
                                      'width': 0.035}],
                            'lock-bar': [{'kind': 'polygon',
                                          'pts': [[0.562916512459885, -0.925],
                                                  [0.4070319397786861, -1.0150000000000001],
                                                  [0.4070319397786861, -1.195],
                                                  [0.562916512459885, -1.105]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.562916512459885, -0.925],
                                                  [1.9485571585149868, -1.725],
                                                  [1.9485571585149868, -1.9050000000000002],
                                                  [0.562916512459885, -1.105]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.562916512459885, -1.105],
                                                  [1.9485571585149868, -1.9050000000000002],
                                                  [1.7926725858337882, -1.995],
                                                  [0.4070319397786861, -1.195]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.5242047106606118, -1.24],
                                                  [1.3683201379794128, -1.33],
                                                  [1.3683201379794128, -1.88],
                                                  [1.5242047106606118, -1.79]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.5242047106606118, -1.24],
                                                  [1.6974097914174997, -1.3399999999999999],
                                                  [1.6974097914174997, -1.89],
                                                  [1.5242047106606118, -1.79]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.5242047106606118, -1.79],
                                                  [1.6974097914174997, -1.89],
                                                  [1.5415252187363004, -1.98],
                                                  [1.3683201379794128, -1.88]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035}]},
                  'moves': {'lock-bar': [0.562916512459885, -0.325]}},
 'conveyor': {'parts': {'frame': [{'kind': 'polygon',
                                   'pts': [[0.0, 0.0],
                                           [-1.299038105676658, -0.75],
                                           [-1.299038105676658, -1.15],
                                           [0.0, -0.4]],
                                   'fill': '#26221F',
                                   'stroke': '#3D3929',
                                   'width': 0.035},
                                  {'kind': 'polygon',
                                   'pts': [[0.0, 0.0],
                                           [3.4641016151377544, -2.0],
                                           [3.4641016151377544, -2.4],
                                           [0.0, -0.4]],
                                   'fill': '#1E1B18',
                                   'stroke': '#3D3929',
                                   'width': 0.035},
                                  {'kind': 'polygon',
                                   'pts': [[0.0, -0.4],
                                           [3.4641016151377544, -2.4],
                                           [2.1650635094610964, -3.15],
                                           [-1.299038105676658, -1.15]],
                                   'fill': '#3A3530',
                                   'stroke': '#3D3929',
                                   'width': 0.035}],
                        'rollers': [{'kind': 'polygon',
                                     'pts': [[0.05196152422706631, -0.5],
                                             [-1.1258330249197703, -1.1800000000000002],
                                             [-1.1258330249197703, -1.26],
                                             [0.05196152422706631, -0.5800000000000001]],
                                     'fill': '#B4AFA6',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.05196152422706631, -0.5],
                                             [0.31176914536239786, -0.65],
                                             [0.31176914536239786, -0.73],
                                             [0.05196152422706631, -0.5800000000000001]],
                                     'fill': '#8B8F96',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.05196152422706631, -0.5800000000000001],
                                             [0.31176914536239786, -0.73],
                                             [-0.8660254037844388, -1.4100000000000001],
                                             [-1.1258330249197703, -1.26]],
                                     'fill': '#D9D4C7',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.4676537180435969, -0.74],
                                             [-0.7101408311032398, -1.42],
                                             [-0.7101408311032398, -1.5],
                                             [0.4676537180435969, -0.8200000000000001]],
                                     'fill': '#B4AFA6',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.4676537180435969, -0.74],
                                             [0.7274613391789283, -0.89],
                                             [0.7274613391789283, -0.97],
                                             [0.4676537180435969, -0.8200000000000001]],
                                     'fill': '#8B8F96',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.4676537180435969, -0.8200000000000001],
                                             [0.7274613391789283, -0.97],
                                             [-0.45033320996790827, -1.65],
                                             [-0.7101408311032398, -1.5]],
                                     'fill': '#D9D4C7',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.8833459118601272, -0.98],
                                             [-0.2944486372867094, -1.6600000000000001],
                                             [-0.2944486372867094, -1.74],
                                             [0.8833459118601272, -1.06]],
                                     'fill': '#B4AFA6',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.8833459118601272, -0.98],
                                             [1.1431535329954587, -1.13],
                                             [1.1431535329954587, -1.21],
                                             [0.8833459118601272, -1.06]],
                                     'fill': '#8B8F96',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[0.8833459118601272, -1.06],
                                             [1.1431535329954587, -1.21],
                                             [-0.03464101615137777, -1.8900000000000001],
                                             [-0.2944486372867094, -1.74]],
                                     'fill': '#D9D4C7',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[1.2990381056766578, -1.22],
                                             [0.12124355652982112, -1.9],
                                             [0.12124355652982112, -1.98],
                                             [1.2990381056766578, -1.3]],
                                     'fill': '#B4AFA6',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[1.2990381056766578, -1.22],
                                             [1.5588457268119893, -1.37],
                                             [1.5588457268119893, -1.45],
                                             [1.2990381056766578, -1.3]],
                                     'fill': '#8B8F96',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[1.2990381056766578, -1.3],
                                             [1.5588457268119893, -1.45],
                                             [0.38105117766515273, -2.13],
                                             [0.12124355652982112, -1.98]],
                                     'fill': '#D9D4C7',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[1.7147302994931881, -1.46],
                                             [0.5369357503463517, -2.14],
                                             [0.5369357503463517, -2.22],
                                             [1.7147302994931881, -1.5399999999999998]],
                                     'fill': '#B4AFA6',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[1.7147302994931881, -1.46],
                                             [1.9745379206285198, -1.6099999999999999],
                                             [1.9745379206285198, -1.6899999999999997],
                                             [1.7147302994931881, -1.5399999999999998]],
                                     'fill': '#8B8F96',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[1.7147302994931881, -1.5399999999999998],
                                             [1.9745379206285198, -1.6899999999999997],
                                             [0.7967433714816831, -2.37],
                                             [0.5369357503463517, -2.22]],
                                     'fill': '#D9D4C7',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.130422493309719, -1.6999999999999997],
                                             [0.9526279441628821, -2.38],
                                             [0.9526279441628821, -2.46],
                                             [2.130422493309719, -1.7799999999999998]],
                                     'fill': '#B4AFA6',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.130422493309719, -1.6999999999999997],
                                             [2.39023011444505, -1.8499999999999996],
                                             [2.39023011444505, -1.9299999999999997],
                                             [2.130422493309719, -1.7799999999999998]],
                                     'fill': '#8B8F96',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.130422493309719, -1.7799999999999998],
                                             [2.39023011444505, -1.9299999999999997],
                                             [1.2124355652982135, -2.61],
                                             [0.9526279441628821, -2.46]],
                                     'fill': '#D9D4C7',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.5461146871262494, -1.94],
                                             [1.3683201379794128, -2.6199999999999997],
                                             [1.3683201379794128, -2.6999999999999997],
                                             [2.5461146871262494, -2.02]],
                                     'fill': '#B4AFA6',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.5461146871262494, -1.94],
                                             [2.805922308261581, -2.09],
                                             [2.805922308261581, -2.17],
                                             [2.5461146871262494, -2.02]],
                                     'fill': '#8B8F96',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.5461146871262494, -2.02],
                                             [2.805922308261581, -2.17],
                                             [1.628127759114744, -2.85],
                                             [1.3683201379794128, -2.6999999999999997]],
                                     'fill': '#D9D4C7',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.9618068809427798, -2.1799999999999997],
                                             [1.784012331795943, -2.86],
                                             [1.784012331795943, -2.94],
                                             [2.9618068809427798, -2.26]],
                                     'fill': '#B4AFA6',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.9618068809427798, -2.1799999999999997],
                                             [3.2216145020781113, -2.3299999999999996],
                                             [3.2216145020781113, -2.4099999999999997],
                                             [2.9618068809427798, -2.26]],
                                     'fill': '#8B8F96',
                                     'stroke': '#3D3929',
                                     'width': 0.035},
                                    {'kind': 'polygon',
                                     'pts': [[2.9618068809427798, -2.26],
                                             [3.2216145020781113, -2.4099999999999997],
                                             [2.0438199529312744, -3.09],
                                             [1.784012331795943, -2.94]],
                                     'fill': '#D9D4C7',
                                     'stroke': '#3D3929',
                                     'width': 0.035}],
                        'parcel': [{'kind': 'polygon',
                                    'pts': [[0.18186533479473213, -0.875],
                                            [-0.6841600689897065, -1.375],
                                            [-0.6841600689897065, -2.125],
                                            [0.18186533479473213, -1.625]],
                                    'fill': '#DCC9AA',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.18186533479473213, -0.875],
                                            [1.0478907385791707, -1.375],
                                            [1.0478907385791707, -2.125],
                                            [0.18186533479473213, -1.625]],
                                    'fill': '#C7AE86',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.18186533479473213, -1.625],
                                            [1.0478907385791707, -2.125],
                                            [0.18186533479473208, -2.625],
                                            [-0.6841600689897065, -2.125]],
                                    'fill': '#F3E9D8',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'circle',
                                    'cx': 0.19052558883257656,
                                    'cy': -2.1100000000000003,
                                    'r': 0.07,
                                    'fill': '#D97757',
                                    'stroke': 'none',
                                    'width': 0}]},
              'moves': {'parcel': [1.5588457268119895, -0.9]}},
 'branch-junction': {'parts': {'inbound': [{'kind': 'polygon',
                                            'pts': [[0.0, 0.0],
                                                    [-0.9526279441628825, -0.55],
                                                    [-0.9526279441628825, -0.7000000000000001],
                                                    [0.0, -0.15]],
                                            'fill': '#B4AFA6',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, 0.0],
                                                    [1.12583302491977, -0.65],
                                                    [1.12583302491977, -0.8],
                                                    [0.0, -0.15]],
                                            'fill': '#8B8F96',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.15],
                                                    [1.12583302491977, -0.8],
                                                    [0.17320508075688767, -1.35],
                                                    [-0.9526279441628825, -0.7000000000000001]],
                                            'fill': '#D9D4C7',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                               'route-a': [{'kind': 'polygon',
                                            'pts': [[1.299038105676658, -0.75],
                                                    [0.9093266739736605, -0.975],
                                                    [0.9093266739736605, -1.125],
                                                    [1.299038105676658, -0.9]],
                                            'fill': '#B4AFA6',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[1.299038105676658, -0.75],
                                                    [2.857883832488647, -1.65],
                                                    [2.857883832488647, -1.7999999999999998],
                                                    [1.299038105676658, -0.9]],
                                            'fill': '#8B8F96',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[1.299038105676658, -0.9],
                                                    [2.857883832488647, -1.7999999999999998],
                                                    [2.4681724007856496, -2.025],
                                                    [0.9093266739736605, -1.125]],
                                            'fill': '#D9D4C7',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                               'route-b': [{'kind': 'polygon',
                                            'pts': [[0.606217782649107, -1.15],
                                                    [-0.9526279441628825, -2.05],
                                                    [-0.9526279441628825, -2.1999999999999997],
                                                    [0.606217782649107, -1.2999999999999998]],
                                            'fill': '#B4AFA6',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.606217782649107, -1.15],
                                                    [0.9959292143521044, -1.375],
                                                    [0.9959292143521044, -1.525],
                                                    [0.606217782649107, -1.2999999999999998]],
                                            'fill': '#8B8F96',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.606217782649107, -1.2999999999999998],
                                                    [0.9959292143521044, -1.525],
                                                    [-0.5629165124598852, -2.425],
                                                    [-0.9526279441628825, -2.1999999999999997]],
                                            'fill': '#D9D4C7',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                               'packet': [{'kind': 'polygon',
                                           'pts': [[-0.060621778264910706, -0.385],
                                                   [-0.6235382907247957, -0.71],
                                                   [-0.6235382907247957, -1.1600000000000001],
                                                   [-0.060621778264910706, -0.835]],
                                           'fill': '#26221F',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-0.060621778264910706, -0.385],
                                                   [0.5455960043841963, -0.7350000000000001],
                                                   [0.5455960043841963, -1.185],
                                                   [-0.060621778264910706, -0.835]],
                                           'fill': '#1E1B18',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-0.060621778264910706, -0.835],
                                                   [0.5455960043841963, -1.185],
                                                   [-0.017320508075688787, -1.51],
                                                   [-0.6235382907247957, -1.1600000000000001]],
                                           'fill': '#3A3530',
                                           'stroke': '#3D3929',
                                           'width': 0.035}]},
                     'moves': {'packet': [1.6887495373796555, -0.875]}},
 'checkpoint-scanner': {'parts': {'track': [{'kind': 'polygon',
                                             'pts': [[0.2598076211353316, 0.25],
                                                     [-1.7320508075688772, -0.8999999999999999],
                                                     [-1.7320508075688772, -1.0499999999999998],
                                                     [0.2598076211353316, 0.1]],
                                             'fill': '#B4AFA6',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.2598076211353316, 0.25],
                                                     [2.7712812921102032, -1.2],
                                                     [2.7712812921102032, -1.3499999999999999],
                                                     [0.2598076211353316, 0.1]],
                                             'fill': '#8B8F96',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.2598076211353316, 0.1],
                                                     [2.7712812921102032, -1.3499999999999999],
                                                     [0.7794228634059946, -2.4999999999999996],
                                                     [-1.7320508075688772, -1.0499999999999998]],
                                             'fill': '#D9D4C7',
                                             'stroke': '#3D3929',
                                             'width': 0.035}],
                                  'arch': [{'kind': 'polygon',
                                            'pts': [[1.4289419162443235, -1.6249999999999998],
                                                    [1.039230484541326, -1.8499999999999999],
                                                    [1.039230484541326, -3.8499999999999996],
                                                    [1.4289419162443235, -3.625]],
                                            'fill': '#26221F',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[1.4289419162443235, -1.6249999999999998],
                                                    [1.688749537379655, -1.7749999999999997],
                                                    [1.688749537379655, -3.7749999999999995],
                                                    [1.4289419162443235, -3.625]],
                                            'fill': '#1E1B18',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[1.4289419162443235, -3.625],
                                                    [1.688749537379655, -3.7749999999999995],
                                                    [1.2990381056766576, -4.0],
                                                    [1.039230484541326, -3.8499999999999996]],
                                            'fill': '#3A3530',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-0.562916512459885, -2.475],
                                                    [-0.9526279441628825, -2.7],
                                                    [-0.9526279441628825, -2.95],
                                                    [-0.562916512459885, -2.725]],
                                            'fill': '#26221F',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-0.562916512459885, -2.475],
                                                    [1.6887495373796555, -3.775],
                                                    [1.6887495373796555, -4.025],
                                                    [-0.562916512459885, -2.725]],
                                            'fill': '#1E1B18',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[-0.562916512459885, -2.725],
                                                    [1.6887495373796555, -4.025],
                                                    [1.299038105676658, -4.25],
                                                    [-0.9526279441628825, -2.95]],
                                            'fill': '#3A3530',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'circle',
                                            'cx': 0.5802370205355739,
                                            'cy': -3.2249999999999996,
                                            'r': 0.07,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0}],
                                  'parcel': [{'kind': 'polygon',
                                              'pts': [[0.8660254037844386, -0.4],
                                                      [-0.08660254037844393, -0.95],
                                                      [-0.08660254037844393, -1.65],
                                                      [0.8660254037844386, -1.0999999999999999]],
                                              'fill': '#DCC9AA',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.8660254037844386, -0.4],
                                                      [1.818653347947321, -0.95],
                                                      [1.818653347947321, -1.65],
                                                      [0.8660254037844386, -1.0999999999999999]],
                                              'fill': '#C7AE86',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.8660254037844386, -1.0999999999999999],
                                                      [1.818653347947321, -1.65],
                                                      [0.8660254037844386, -2.2],
                                                      [-0.08660254037844393, -1.65]],
                                              'fill': '#F3E9D8',
                                              'stroke': '#3D3929',
                                              'width': 0.035}],
                                  'near-post': [{'kind': 'polygon',
                                                 'pts': [[-0.562916512459885, -0.475],
                                                         [-0.9526279441628825, -0.7000000000000001],
                                                         [-0.9526279441628825, -2.7],
                                                         [-0.562916512459885, -2.475]],
                                                 'fill': '#26221F',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035},
                                                {'kind': 'polygon',
                                                 'pts': [[-0.562916512459885, -0.475],
                                                         [-0.30310889132455354, -0.625],
                                                         [-0.30310889132455354, -2.625],
                                                         [-0.562916512459885, -2.475]],
                                                 'fill': '#1E1B18',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035},
                                                {'kind': 'polygon',
                                                 'pts': [[-0.562916512459885, -2.475],
                                                         [-0.30310889132455354, -2.625],
                                                         [-0.6928203230275509, -2.85],
                                                         [-0.9526279441628825, -2.7]],
                                                 'fill': '#3A3530',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035}]},
                        'moves': {'parcel': [-1.0825317547305482, -0.625]}},
 'evidence-binder': {'parts': {'back-cover': [{'kind': 'polygon',
                                               'pts': [[0.0, 0.0],
                                                       [-2.424871130596428, -1.4],
                                                       [-2.424871130596428, -1.52],
                                                       [0.0, -0.12]],
                                               'fill': '#26221F',
                                               'stroke': '#3D3929',
                                               'width': 0.035},
                                              {'kind': 'polygon',
                                               'pts': [[0.0, 0.0],
                                                       [2.0784609690826525, -1.2],
                                                       [2.0784609690826525, -1.3199999999999998],
                                                       [0.0, -0.12]],
                                               'fill': '#1E1B18',
                                               'stroke': '#3D3929',
                                               'width': 0.035},
                                              {'kind': 'polygon',
                                               'pts': [[0.0, -0.12],
                                                       [2.0784609690826525, -1.3199999999999998],
                                                       [-0.34641016151377535, -2.7199999999999998],
                                                       [-2.424871130596428, -1.52]],
                                               'fill': '#3A3530',
                                               'stroke': '#3D3929',
                                               'width': 0.035}],
                               'records': [{'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.34],
                                                    [-2.035159698893431, -1.565],
                                                    [-2.035159698893431, -1.635],
                                                    [0.08660254037844387, -0.41000000000000003]],
                                            'fill': '#ECE7DF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.34],
                                                    [1.7753520777580993, -1.315],
                                                    [1.7753520777580993, -1.385],
                                                    [0.08660254037844387, -0.41000000000000003]],
                                            'fill': '#E2DCD2',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.41000000000000003],
                                                    [1.7753520777580993, -1.385],
                                                    [-0.34641016151377535, -2.6100000000000003],
                                                    [-2.035159698893431, -1.635]],
                                            'fill': '#FFFFFF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polyline',
                                            'pts': [[-0.04330127018922192, -0.69], [1.299038105676658, -1.465]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.30310889132455354, -0.8400000000000001],
                                                    [1.0392304845413263, -1.615]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.562916512459885, -0.99], [0.7794228634059949, -1.765]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'circle',
                                            'cx': -1.6021469970012114,
                                            'cy': -1.625,
                                            'r': 0.055,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.46],
                                                    [-2.035159698893431, -1.685],
                                                    [-2.035159698893431, -1.7550000000000001],
                                                    [0.08660254037844387, -0.53]],
                                            'fill': '#ECE7DF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.46],
                                                    [1.7753520777580993, -1.435],
                                                    [1.7753520777580993, -1.5050000000000001],
                                                    [0.08660254037844387, -0.53]],
                                            'fill': '#E2DCD2',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.53],
                                                    [1.7753520777580993, -1.5050000000000001],
                                                    [-0.34641016151377535, -2.7300000000000004],
                                                    [-2.035159698893431, -1.7550000000000001]],
                                            'fill': '#FFFFFF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polyline',
                                            'pts': [[-0.04330127018922192, -0.81], [1.299038105676658, -1.585]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.30310889132455354, -0.96],
                                                    [1.0392304845413263, -1.7349999999999999]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.562916512459885, -1.1099999999999999],
                                                    [0.7794228634059949, -1.8849999999999998]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'circle',
                                            'cx': -1.6021469970012114,
                                            'cy': -1.745,
                                            'r': 0.055,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.5800000000000001],
                                                    [-2.035159698893431, -1.8050000000000002],
                                                    [-2.035159698893431, -1.875],
                                                    [0.08660254037844387, -0.65]],
                                            'fill': '#ECE7DF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.5800000000000001],
                                                    [1.7753520777580993, -1.5550000000000002],
                                                    [1.7753520777580993, -1.625],
                                                    [0.08660254037844387, -0.65]],
                                            'fill': '#E2DCD2',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.08660254037844387, -0.65],
                                                    [1.7753520777580993, -1.625],
                                                    [-0.34641016151377535, -2.8500000000000005],
                                                    [-2.035159698893431, -1.875]],
                                            'fill': '#FFFFFF',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polyline',
                                            'pts': [[-0.04330127018922192, -0.9299999999999999],
                                                    [1.299038105676658, -1.705]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.30310889132455354, -1.08], [1.0392304845413263, -1.855]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'polyline',
                                            'pts': [[-0.562916512459885, -1.23], [0.7794228634059949, -2.005]],
                                            'fill': 'none',
                                            'stroke': '#D9D4C7',
                                            'width': 0.04},
                                           {'kind': 'circle',
                                            'cx': -1.6021469970012114,
                                            'cy': -1.865,
                                            'r': 0.055,
                                            'fill': '#D97757',
                                            'stroke': 'none',
                                            'width': 0}],
                               'spine': [{'kind': 'polygon',
                                          'pts': [[0.0, -0.12],
                                                  [-2.424871130596428, -1.52],
                                                  [-2.424871130596428, -2.17],
                                                  [0.0, -0.77]],
                                          'fill': '#26221F',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.12],
                                                  [0.15588457268119893, -0.21],
                                                  [0.15588457268119893, -0.86],
                                                  [0.0, -0.77]],
                                          'fill': '#1E1B18',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.77],
                                                  [0.15588457268119893, -0.86],
                                                  [-2.2689865579152286, -2.26],
                                                  [-2.424871130596428, -2.17]],
                                          'fill': '#3A3530',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                               'cover': [{'kind': 'polygon',
                                          'pts': [[0.16454482671904333, -0.6749999999999999],
                                                  [-2.2603263038773846, -2.0749999999999997],
                                                  [-2.2603263038773846, -2.195],
                                                  [0.16454482671904333, -0.7949999999999999]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.16454482671904333, -0.6749999999999999],
                                                  [2.0698007150448086, -1.775],
                                                  [2.0698007150448086, -1.895],
                                                  [0.16454482671904333, -0.7949999999999999]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.16454482671904333, -0.7949999999999999],
                                                  [2.0698007150448086, -1.895],
                                                  [-0.35507041555161956, -3.295],
                                                  [-2.2603263038773846, -2.195]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035}]},
                     'moves': {'cover': [0.0, -0.9]}},
 'inspection-lamp': {'parts': {'base': [{'kind': 'polygon',
                                         'pts': [[0.0, -0.1],
                                                 [-0.8660254037844386, -0.6000000000000001],
                                                 [-0.8660254037844386, -0.78],
                                                 [0.0, -0.28]],
                                         'fill': '#26221F',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -0.1],
                                                 [0.8660254037844386, -0.6000000000000001],
                                                 [0.8660254037844386, -0.78],
                                                 [0.0, -0.28]],
                                         'fill': '#1E1B18',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -0.28],
                                                 [0.8660254037844386, -0.78],
                                                 [0.0, -1.28],
                                                 [-0.8660254037844386, -0.78]],
                                         'fill': '#3A3530',
                                         'stroke': '#3D3929',
                                         'width': 0.035}],
                               'upright': [{'kind': 'polygon',
                                            'pts': [[0.0, -0.61],
                                                    [-0.17320508075688773, -0.71],
                                                    [-0.17320508075688773, -2.8100000000000005],
                                                    [0.0, -2.7100000000000004]],
                                            'fill': '#B4AFA6',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.61],
                                                    [0.17320508075688773, -0.71],
                                                    [0.17320508075688773, -2.8100000000000005],
                                                    [0.0, -2.7100000000000004]],
                                            'fill': '#8B8F96',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -2.7100000000000004],
                                                    [0.17320508075688773, -2.8100000000000005],
                                                    [0.0, -2.91],
                                                    [-0.17320508075688773, -2.8100000000000005]],
                                            'fill': '#D9D4C7',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                               'lamp-head': [{'kind': 'polygon',
                                              'pts': [[0.0, -2.71],
                                                      [-0.17320508075688773, -2.8099999999999996],
                                                      [-0.17320508075688773, -2.9699999999999998],
                                                      [0.0, -2.87]],
                                              'fill': '#B4AFA6',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, -2.71],
                                                      [1.4722431864335457, -3.5599999999999996],
                                                      [1.4722431864335457, -3.7199999999999998],
                                                      [0.0, -2.87]],
                                              'fill': '#8B8F96',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[0.0, -2.87],
                                                      [1.4722431864335457, -3.7199999999999998],
                                                      [1.299038105676658, -3.82],
                                                      [-0.17320508075688773, -2.9699999999999998]],
                                              'fill': '#D9D4C7',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[1.368320137979413, -2.86],
                                                      [0.718801085141084, -3.235],
                                                      [0.718801085141084, -3.665],
                                                      [1.368320137979413, -3.29]],
                                              'fill': '#26221F',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[1.368320137979413, -2.86],
                                                      [2.104441731196186, -3.285],
                                                      [2.104441731196186, -3.715],
                                                      [1.368320137979413, -3.29]],
                                              'fill': '#1E1B18',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[1.368320137979413, -3.29],
                                                      [2.104441731196186, -3.715],
                                                      [1.454922678357857, -4.09],
                                                      [0.718801085141084, -3.665]],
                                              'fill': '#3A3530',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[1.4635829323957015, -2.955],
                                                      [2.0091789367798976, -3.27],
                                                      [2.0091789367798976, -3.4000000000000004],
                                                      [1.4635829323957015, -3.085]],
                                              'fill': '#FFFFFF',
                                              'stroke': 'none',
                                              'width': 0.035}],
                               'evidence': [{'kind': 'polygon',
                                             'pts': [[1.255736835487436, -0.645],
                                                     [-0.1299038105676657, -1.445],
                                                     [-0.1299038105676657, -1.5150000000000001],
                                                     [1.255736835487436, -0.715]],
                                             'fill': '#ECE7DF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.255736835487436, -0.645],
                                                     [2.554774941164094, -1.395],
                                                     [2.554774941164094, -1.465],
                                                     [1.255736835487436, -0.715]],
                                             'fill': '#E2DCD2',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.255736835487436, -0.715],
                                                     [2.554774941164094, -1.465],
                                                     [1.1691342951089922, -2.2649999999999997],
                                                     [-0.1299038105676657, -1.5150000000000001]],
                                             'fill': '#FFFFFF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[1.12583302491977, -0.995], [2.0784609690826525, -1.545]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[0.8660254037844386, -1.145], [1.8186533479473208, -1.695]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[0.6062177826491071, -1.295], [1.5588457268119893, -1.845]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'circle',
                                             'cx': 0.3031088913245536,
                                             'cy': -1.5050000000000001,
                                             'r': 0.055,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0}]},
                     'moves': {'lamp-head': [0.0, 0.5]}},
 'experiment-bench': {'parts': {'base': [{'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [-1.905255888325765, -1.1],
                                                  [-1.905255888325765, -1.35],
                                                  [0.0, -0.25]],
                                          'fill': '#B4AFA6',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [2.598076211353316, -1.5],
                                                  [2.598076211353316, -1.75],
                                                  [0.0, -0.25]],
                                          'fill': '#8B8F96',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.25],
                                                  [2.598076211353316, -1.75],
                                                  [0.6928203230275507, -2.85],
                                                  [-1.905255888325765, -1.35]],
                                          'fill': '#D9D4C7',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                                'fixture': [{'kind': 'polygon',
                                             'pts': [[-0.25980762113533157, -0.6],
                                                     [-1.2124355652982142, -1.15],
                                                     [-1.2124355652982142, -2.05],
                                                     [-0.25980762113533157, -1.5]],
                                             'fill': '#26221F',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.25980762113533157, -0.6],
                                                     [-0.04330127018922192, -0.725],
                                                     [-0.04330127018922192, -1.625],
                                                     [-0.25980762113533157, -1.5]],
                                             'fill': '#1E1B18',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.25980762113533157, -1.5],
                                                     [-0.04330127018922192, -1.625],
                                                     [-0.9959292143521045, -2.175],
                                                     [-1.2124355652982142, -2.05]],
                                             'fill': '#3A3530',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.7320508075688772, -1.75],
                                                     [0.7794228634059946, -2.3],
                                                     [0.7794228634059946, -3.1999999999999997],
                                                     [1.7320508075688772, -2.65]],
                                             'fill': '#26221F',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.7320508075688772, -1.75],
                                                     [1.9485571585149868, -1.875],
                                                     [1.9485571585149868, -2.775],
                                                     [1.7320508075688772, -2.65]],
                                             'fill': '#1E1B18',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.7320508075688772, -2.65],
                                                     [1.9485571585149868, -2.775],
                                                     [0.9959292143521044, -3.3249999999999997],
                                                     [0.7794228634059946, -3.1999999999999997]],
                                             'fill': '#3A3530',
                                             'stroke': '#3D3929',
                                             'width': 0.035}],
                                'sample': [{'kind': 'polygon',
                                            'pts': [[0.34641016151377557, -1.2],
                                                    [-0.3031088913245534, -1.575],
                                                    [-0.3031088913245534, -2.275],
                                                    [0.34641016151377557, -1.9]],
                                            'fill': '#DCC9AA',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.34641016151377557, -1.2],
                                                    [0.9959292143521045, -1.575],
                                                    [0.9959292143521045, -2.275],
                                                    [0.34641016151377557, -1.9]],
                                            'fill': '#C7AE86',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.34641016151377557, -1.9],
                                                    [0.9959292143521045, -2.275],
                                                    [0.34641016151377557, -2.65],
                                                    [-0.3031088913245534, -2.275]],
                                            'fill': '#F3E9D8',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                                'control': [{'kind': 'polygon',
                                             'pts': [[0.3897114317029973, -0.47500000000000003],
                                                     [0.12990381056766578, -0.625],
                                                     [0.12990381056766578, -1.0750000000000002],
                                                     [0.3897114317029973, -0.925]],
                                             'fill': '#26221F',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.3897114317029973, -0.47500000000000003],
                                                     [0.9526279441628823, -0.8],
                                                     [0.9526279441628823, -1.25],
                                                     [0.3897114317029973, -0.925]],
                                             'fill': '#1E1B18',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.3897114317029973, -0.925],
                                                     [0.9526279441628823, -1.25],
                                                     [0.6928203230275508, -1.4],
                                                     [0.12990381056766578, -1.0750000000000002]],
                                             'fill': '#3A3530',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'circle',
                                             'cx': 0.6928203230275509,
                                             'cy': -0.86,
                                             'r': 0.07,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0}]},
                      'moves': {'sample': [0.0, -1.0]}},
 'version-shelves': {'parts': {'back': [{'kind': 'polygon',
                                         'pts': [[-1.5588457268119895, -0.9],
                                                 [-1.6887495373796553, -0.975],
                                                 [-1.6887495373796553, -3.1750000000000003],
                                                 [-1.5588457268119895, -3.1]],
                                         'fill': '#DCC9AA',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[-1.5588457268119895, -0.9],
                                                 [0.8660254037844384, -2.3],
                                                 [0.8660254037844384, -4.5],
                                                 [-1.5588457268119895, -3.1]],
                                         'fill': '#C7AE86',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[-1.5588457268119895, -3.1],
                                                 [0.8660254037844384, -4.5],
                                                 [0.7361215932167727, -4.575],
                                                 [-1.6887495373796553, -3.1750000000000003]],
                                         'fill': '#F3E9D8',
                                         'stroke': '#3D3929',
                                         'width': 0.035}],
                               'supports': [{'kind': 'polygon',
                                             'pts': [[-0.08660254037844387, -0.05],
                                                     [-0.21650635094610965, -0.125],
                                                     [-0.21650635094610965, -2.225],
                                                     [-0.08660254037844387, -2.15]],
                                             'fill': '#26221F',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.08660254037844387, -0.05],
                                                     [0.04330127018922192, -0.125],
                                                     [0.04330127018922192, -2.225],
                                                     [-0.08660254037844387, -2.15]],
                                             'fill': '#1E1B18',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.08660254037844387, -2.15],
                                                     [0.04330127018922192, -2.225],
                                                     [-0.08660254037844387, -2.3000000000000003],
                                                     [-0.21650635094610965, -2.225]],
                                             'fill': '#3A3530',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.208364779650318, -1.375],
                                                     [2.0784609690826525, -1.45],
                                                     [2.0784609690826525, -3.55],
                                                     [2.208364779650318, -3.475]],
                                             'fill': '#26221F',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.208364779650318, -1.375],
                                                     [2.338268590217984, -1.45],
                                                     [2.338268590217984, -3.55],
                                                     [2.208364779650318, -3.475]],
                                             'fill': '#1E1B18',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[2.208364779650318, -3.475],
                                                     [2.338268590217984, -3.55],
                                                     [2.208364779650318, -3.625],
                                                     [2.0784609690826525, -3.55]],
                                             'fill': '#3A3530',
                                             'stroke': '#3D3929',
                                             'width': 0.035}],
                               'shelves': [{'kind': 'polygon',
                                            'pts': [[0.0, -0.05],
                                                    [-1.6454482671904334, -1.0],
                                                    [-1.6454482671904334, -1.1],
                                                    [0.0, -0.15000000000000002]],
                                            'fill': '#B4AFA6',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.05],
                                                    [2.424871130596428, -1.45],
                                                    [2.424871130596428, -1.5499999999999998],
                                                    [0.0, -0.15000000000000002]],
                                            'fill': '#8B8F96',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.15000000000000002],
                                                    [2.424871130596428, -1.5499999999999998],
                                                    [0.7794228634059946, -2.4999999999999996],
                                                    [-1.6454482671904334, -1.1]],
                                            'fill': '#D9D4C7',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.75],
                                                    [-1.6454482671904334, -1.7],
                                                    [-1.6454482671904334, -1.7999999999999998],
                                                    [0.0, -0.85]],
                                            'fill': '#B4AFA6',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.75],
                                                    [2.424871130596428, -2.15],
                                                    [2.424871130596428, -2.25],
                                                    [0.0, -0.85]],
                                            'fill': '#8B8F96',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -0.85],
                                                    [2.424871130596428, -2.25],
                                                    [0.7794228634059946, -3.1999999999999997],
                                                    [-1.6454482671904334, -1.7999999999999998]],
                                            'fill': '#D9D4C7',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -1.45],
                                                    [-1.6454482671904334, -2.4],
                                                    [-1.6454482671904334, -2.5],
                                                    [0.0, -1.55]],
                                            'fill': '#B4AFA6',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -1.45],
                                                    [2.424871130596428, -2.8499999999999996],
                                                    [2.424871130596428, -2.95],
                                                    [0.0, -1.55]],
                                            'fill': '#8B8F96',
                                            'stroke': '#3D3929',
                                            'width': 0.035},
                                           {'kind': 'polygon',
                                            'pts': [[0.0, -1.55],
                                                    [2.424871130596428, -2.95],
                                                    [0.7794228634059946, -3.8999999999999995],
                                                    [-1.6454482671904334, -2.5]],
                                            'fill': '#D9D4C7',
                                            'stroke': '#3D3929',
                                            'width': 0.035}],
                               'versions': [{'kind': 'polygon',
                                             'pts': [[0.1732050807568877, -0.45],
                                                     [-1.12583302491977, -1.2],
                                                     [-1.12583302491977, -1.27],
                                                     [0.1732050807568877, -0.52]],
                                             'fill': '#ECE7DF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.1732050807568877, -0.45],
                                                     [1.905255888325765, -1.45],
                                                     [1.905255888325765, -1.52],
                                                     [0.1732050807568877, -0.52]],
                                             'fill': '#E2DCD2',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.1732050807568877, -0.52],
                                                     [1.905255888325765, -1.52],
                                                     [0.6062177826491072, -2.27],
                                                     [-1.12583302491977, -1.27]],
                                             'fill': '#FFFFFF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[0.04330127018922197, -0.8], [1.4289419162443235, -1.6]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[-0.21650635094610965, -0.9500000000000001],
                                                     [1.169134295108992, -1.75]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[-0.47631397208144105, -1.1], [0.9093266739736605, -1.9]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'circle',
                                             'cx': -0.6928203230275508,
                                             'cy': -1.26,
                                             'r': 0.055,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0},
                                            {'kind': 'polygon',
                                             'pts': [[0.1732050807568877, -1.8499999999999999],
                                                     [-1.12583302491977, -2.5999999999999996],
                                                     [-1.12583302491977, -2.67],
                                                     [0.1732050807568877, -1.92]],
                                             'fill': '#ECE7DF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.1732050807568877, -1.8499999999999999],
                                                     [1.905255888325765, -2.8499999999999996],
                                                     [1.905255888325765, -2.92],
                                                     [0.1732050807568877, -1.92]],
                                             'fill': '#E2DCD2',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.1732050807568877, -1.92],
                                                     [1.905255888325765, -2.92],
                                                     [0.6062177826491072, -3.67],
                                                     [-1.12583302491977, -2.67]],
                                             'fill': '#FFFFFF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[0.04330127018922197, -2.1999999999999997],
                                                     [1.4289419162443235, -3.0]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[-0.21650635094610965, -2.3499999999999996],
                                                     [1.169134295108992, -3.15]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[-0.47631397208144105, -2.5], [0.9093266739736605, -3.3]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'circle',
                                             'cx': -0.6928203230275508,
                                             'cy': -2.66,
                                             'r': 0.055,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0}],
                               'selected-version': [{'kind': 'polygon',
                                                     'pts': [[0.1732050807568877, -1.15],
                                                             [-1.12583302491977, -1.9],
                                                             [-1.12583302491977, -1.97],
                                                             [0.1732050807568877, -1.22]],
                                                     'fill': '#ECE7DF',
                                                     'stroke': '#3D3929',
                                                     'width': 0.035},
                                                    {'kind': 'polygon',
                                                     'pts': [[0.1732050807568877, -1.15],
                                                             [1.905255888325765, -2.15],
                                                             [1.905255888325765, -2.2199999999999998],
                                                             [0.1732050807568877, -1.22]],
                                                     'fill': '#E2DCD2',
                                                     'stroke': '#3D3929',
                                                     'width': 0.035},
                                                    {'kind': 'polygon',
                                                     'pts': [[0.1732050807568877, -1.22],
                                                             [1.905255888325765, -2.2199999999999998],
                                                             [0.6062177826491072, -2.9699999999999998],
                                                             [-1.12583302491977, -1.97]],
                                                     'fill': '#FFFFFF',
                                                     'stroke': '#3D3929',
                                                     'width': 0.035},
                                                    {'kind': 'polyline',
                                                     'pts': [[0.04330127018922197, -1.5], [1.4289419162443235, -2.3]],
                                                     'fill': 'none',
                                                     'stroke': '#D9D4C7',
                                                     'width': 0.04},
                                                    {'kind': 'polyline',
                                                     'pts': [[-0.21650635094610965, -1.65], [1.169134295108992, -2.45]],
                                                     'fill': 'none',
                                                     'stroke': '#D9D4C7',
                                                     'width': 0.04},
                                                    {'kind': 'polyline',
                                                     'pts': [[-0.47631397208144105, -1.7999999999999998],
                                                             [0.9093266739736605, -2.5999999999999996]],
                                                     'fill': 'none',
                                                     'stroke': '#D9D4C7',
                                                     'width': 0.04},
                                                    {'kind': 'circle',
                                                     'cx': -0.6928203230275508,
                                                     'cy': -1.96,
                                                     'r': 0.055,
                                                     'fill': '#D97757',
                                                     'stroke': 'none',
                                                     'width': 0}]},
                     'moves': {'selected-version': [0.8660254037844386, 0.3]}},
 'comparison-trays': {'parts': {'trays': [{'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [-1.6454482671904334, -0.95],
                                                   [-1.6454482671904334, -1.08],
                                                   [0.0, -0.13]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [1.5588457268119895, -0.9],
                                                   [1.5588457268119895, -1.03],
                                                   [0.0, -0.13]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, -0.13],
                                                   [1.5588457268119895, -1.03],
                                                   [-0.08660254037844374, -1.98],
                                                   [-1.6454482671904334, -1.08]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.454922678357857, -0.8400000000000001],
                                                   [-0.19052558883257628, -1.79],
                                                   [-0.19052558883257628, -2.14],
                                                   [1.454922678357857, -1.19]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.454922678357857, -0.8400000000000001],
                                                   [1.5588457268119897, -0.9000000000000001],
                                                   [1.5588457268119897, -1.25],
                                                   [1.454922678357857, -1.19]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.454922678357857, -1.19],
                                                   [1.5588457268119897, -1.25],
                                                   [-0.08660254037844355, -2.2],
                                                   [-0.19052558883257628, -2.14]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-1.5415252187363004, -0.8899999999999999],
                                                   [-1.6454482671904334, -0.95],
                                                   [-1.6454482671904334, -1.2999999999999998],
                                                   [-1.5415252187363004, -1.2399999999999998]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-1.5415252187363004, -0.8899999999999999],
                                                   [0.01732050807568898, -1.79],
                                                   [0.01732050807568898, -2.14],
                                                   [-1.5415252187363004, -1.2399999999999998]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[-1.5415252187363004, -1.2399999999999998],
                                                   [0.01732050807568898, -2.14],
                                                   [-0.08660254037844374, -2.2],
                                                   [-1.6454482671904334, -1.2999999999999998]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.818653347947321, -1.05],
                                                   [0.17320508075688787, -2.0],
                                                   [0.17320508075688787, -2.13],
                                                   [1.818653347947321, -1.1800000000000002]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.818653347947321, -1.05],
                                                   [3.377499074759311, -1.9500000000000002],
                                                   [3.377499074759311, -2.08],
                                                   [1.818653347947321, -1.1800000000000002]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[1.818653347947321, -1.1800000000000002],
                                                   [3.377499074759311, -2.08],
                                                   [1.7320508075688776, -3.0300000000000002],
                                                   [0.17320508075688787, -2.13]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[3.2735760263051783, -1.8900000000000001],
                                                   [1.628127759114745, -2.84],
                                                   [1.628127759114745, -3.19],
                                                   [3.2735760263051783, -2.24]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[3.2735760263051783, -1.8900000000000001],
                                                   [3.377499074759311, -1.9500000000000002],
                                                   [3.377499074759311, -2.3000000000000003],
                                                   [3.2735760263051783, -2.24]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[3.2735760263051783, -2.24],
                                                   [3.377499074759311, -2.3000000000000003],
                                                   [1.7320508075688776, -3.2500000000000004],
                                                   [1.628127759114745, -3.19]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.2771281292110206, -1.94],
                                                   [0.17320508075688787, -2.0],
                                                   [0.17320508075688787, -2.35],
                                                   [0.2771281292110206, -2.29]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.2771281292110206, -1.94],
                                                   [1.8359738560230103, -2.84],
                                                   [1.8359738560230103, -3.19],
                                                   [0.2771281292110206, -2.29]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.2771281292110206, -2.29],
                                                   [1.8359738560230103, -3.19],
                                                   [1.7320508075688776, -3.2500000000000004],
                                                   [0.17320508075688787, -2.35]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035}],
                                'sample-a': [{'kind': 'polygon',
                                              'pts': [[-0.04330127018922192, -0.625],
                                                      [-0.8227241335952167, -1.075],
                                                      [-0.8227241335952167, -1.675],
                                                      [-0.04330127018922192, -1.225]],
                                              'fill': '#DCC9AA',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[-0.04330127018922192, -0.625],
                                                      [0.7361215932167728, -1.075],
                                                      [0.7361215932167728, -1.675],
                                                      [-0.04330127018922192, -1.225]],
                                              'fill': '#C7AE86',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[-0.04330127018922192, -1.225],
                                                      [0.7361215932167728, -1.675],
                                                      [-0.04330127018922197, -2.125],
                                                      [-0.8227241335952167, -1.675]],
                                              'fill': '#F3E9D8',
                                              'stroke': '#3D3929',
                                              'width': 0.035}],
                                'rims': [{'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [-1.6454482671904334, -0.95],
                                                  [-1.6454482671904334, -1.2999999999999998],
                                                  [0.0, -0.35]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [0.10392304845413262, -0.06],
                                                  [0.10392304845413262, -0.41],
                                                  [0.0, -0.35]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.35],
                                                  [0.10392304845413262, -0.41],
                                                  [-1.5415252187363004, -1.3599999999999999],
                                                  [-1.6454482671904334, -1.2999999999999998]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [-0.10392304845413262, -0.06],
                                                  [-0.10392304845413262, -0.41],
                                                  [0.0, -0.35]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [1.5588457268119895, -0.9],
                                                  [1.5588457268119895, -1.25],
                                                  [0.0, -0.35]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.35],
                                                  [1.5588457268119895, -1.25],
                                                  [1.454922678357857, -1.31],
                                                  [-0.10392304845413262, -0.41]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.05],
                                                  [0.17320508075688787, -2.0],
                                                  [0.17320508075688787, -2.35],
                                                  [1.818653347947321, -1.4]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.05],
                                                  [1.922576396401454, -1.11],
                                                  [1.922576396401454, -1.46],
                                                  [1.818653347947321, -1.4]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.4],
                                                  [1.922576396401454, -1.46],
                                                  [0.2771281292110206, -2.41],
                                                  [0.17320508075688787, -2.35]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.05],
                                                  [1.7147302994931883, -1.11],
                                                  [1.7147302994931883, -1.46],
                                                  [1.818653347947321, -1.4]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.05],
                                                  [3.377499074759311, -1.9500000000000002],
                                                  [3.377499074759311, -2.3000000000000003],
                                                  [1.818653347947321, -1.4]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[1.818653347947321, -1.4],
                                                  [3.377499074759311, -2.3000000000000003],
                                                  [3.2735760263051783, -2.3600000000000003],
                                                  [1.7147302994931883, -1.46]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                                'sample-b': [{'kind': 'polygon',
                                              'pts': [[1.775352077758099, -1.675],
                                                      [0.9959292143521044, -2.125],
                                                      [0.9959292143521044, -2.725],
                                                      [1.775352077758099, -2.2750000000000004]],
                                              'fill': '#26221F',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[1.775352077758099, -1.675],
                                                      [2.5547749411640934, -2.125],
                                                      [2.5547749411640934, -2.725],
                                                      [1.775352077758099, -2.2750000000000004]],
                                              'fill': '#1E1B18',
                                              'stroke': '#3D3929',
                                              'width': 0.035},
                                             {'kind': 'polygon',
                                              'pts': [[1.775352077758099, -2.2750000000000004],
                                                      [2.5547749411640934, -2.725],
                                                      [1.775352077758099, -3.175],
                                                      [0.9959292143521044, -2.725]],
                                              'fill': '#3A3530',
                                              'stroke': '#3D3929',
                                              'width': 0.035}]},
                      'moves': {'sample-b': [0.0, -0.9]}},
 'human-handoff': {'parts': {'counter': [{'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [-1.6454482671904334, -0.95],
                                                  [-1.6454482671904334, -1.17],
                                                  [0.0, -0.22]],
                                          'fill': '#DCC9AA',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, 0.0],
                                                  [3.204293994002423, -1.85],
                                                  [3.204293994002423, -2.0700000000000003],
                                                  [0.0, -0.22]],
                                          'fill': '#C7AE86',
                                          'stroke': '#3D3929',
                                          'width': 0.035},
                                         {'kind': 'polygon',
                                          'pts': [[0.0, -0.22],
                                                  [3.204293994002423, -2.0700000000000003],
                                                  [1.5588457268119897, -3.02],
                                                  [-1.6454482671904334, -1.17]],
                                          'fill': '#F3E9D8',
                                          'stroke': '#3D3929',
                                          'width': 0.035}],
                             'human-side': [{'kind': 'polygon',
                                             'pts': [[-0.7794228634059949, -0.89],
                                                     [-1.255736835487436, -1.165],
                                                     [-1.255736835487436, -1.715],
                                                     [-0.7794228634059949, -1.44]],
                                             'fill': '#B4AFA6',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.7794228634059949, -0.89],
                                                     [-0.1299038105676659, -1.265],
                                                     [-0.1299038105676659, -1.815],
                                                     [-0.7794228634059949, -1.44]],
                                             'fill': '#8B8F96',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[-0.7794228634059949, -1.44],
                                                     [-0.1299038105676659, -1.815],
                                                     [-0.6062177826491072, -2.09],
                                                     [-1.255736835487436, -1.715]],
                                             'fill': '#D9D4C7',
                                             'stroke': '#3D3929',
                                             'width': 0.035}],
                             'agent-side': [{'kind': 'polygon',
                                             'pts': [[1.3856406460551018, -2.14],
                                                     [0.9093266739736605, -2.415],
                                                     [0.9093266739736605, -2.9650000000000003],
                                                     [1.3856406460551018, -2.6900000000000004]],
                                             'fill': '#26221F',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.3856406460551018, -2.14],
                                                     [2.035159698893431, -2.5150000000000006],
                                                     [2.035159698893431, -3.0650000000000004],
                                                     [1.3856406460551018, -2.6900000000000004]],
                                             'fill': '#1E1B18',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.3856406460551018, -2.6900000000000004],
                                                     [2.035159698893431, -3.0650000000000004],
                                                     [1.5588457268119895, -3.3400000000000003],
                                                     [0.9093266739736605, -2.9650000000000003]],
                                             'fill': '#3A3530',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'circle',
                                             'cx': 1.7320508075688772,
                                             'cy': -2.62,
                                             'r': 0.07,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0}],
                             'packet': [{'kind': 'polygon',
                                         'pts': [[0.1732050807568877, -0.47000000000000003],
                                                 [-0.5196152422706632, -0.87],
                                                 [-0.5196152422706632, -0.94],
                                                 [0.1732050807568877, -0.54]],
                                         'fill': '#ECE7DF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.1732050807568877, -0.47000000000000003],
                                                 [1.0825317547305482, -0.9950000000000001],
                                                 [1.0825317547305482, -1.0650000000000002],
                                                 [0.1732050807568877, -0.54]],
                                         'fill': '#E2DCD2',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.1732050807568877, -0.54],
                                                 [1.0825317547305482, -1.0650000000000002],
                                                 [0.38971143170299744, -1.465],
                                                 [-0.5196152422706632, -0.94]],
                                         'fill': '#FFFFFF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polyline',
                                         'pts': [[0.04330127018922197, -0.8200000000000001],
                                                 [0.6062177826491072, -1.145]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[-0.21650635094610965, -0.97],
                                                 [0.34641016151377557, -1.2950000000000002]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[-0.4763139720814413, -1.12], [0.08660254037844393, -1.445]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'circle',
                                         'cx': -0.08660254037844384,
                                         'cy': -0.9300000000000002,
                                         'r': 0.055,
                                         'fill': '#D97757',
                                         'stroke': 'none',
                                         'width': 0}]},
                   'moves': {'packet': [1.775352077758099, -1.025]}},
 'task-queue': {'parts': {'rail': [{'kind': 'polygon',
                                    'pts': [[0.0, 0.0],
                                            [-1.299038105676658, -0.75],
                                            [-1.299038105676658, -0.9],
                                            [0.0, -0.15]],
                                    'fill': '#B4AFA6',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.0, 0.0],
                                            [3.117691453623979, -1.8],
                                            [3.117691453623979, -1.95],
                                            [0.0, -0.15]],
                                    'fill': '#8B8F96',
                                    'stroke': '#3D3929',
                                    'width': 0.035},
                                   {'kind': 'polygon',
                                    'pts': [[0.0, -0.15],
                                            [3.117691453623979, -1.95],
                                            [1.818653347947321, -2.6999999999999997],
                                            [-1.299038105676658, -0.9]],
                                    'fill': '#D9D4C7',
                                    'stroke': '#3D3929',
                                    'width': 0.035}],
                          'next-task': [{'kind': 'polygon',
                                         'pts': [[0.0, -0.4],
                                                 [-0.9093266739736605, -0.925],
                                                 [-0.9093266739736605, -1.8250000000000002],
                                                 [0.0, -1.3]],
                                         'fill': '#DCC9AA',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -0.4],
                                                 [0.7361215932167728, -0.825],
                                                 [0.7361215932167728, -1.725],
                                                 [0.0, -1.3]],
                                         'fill': '#C7AE86',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.0, -1.3],
                                                 [0.7361215932167728, -1.725],
                                                 [-0.17320508075688767, -2.25],
                                                 [-0.9093266739736605, -1.8250000000000002]],
                                         'fill': '#F3E9D8',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[-0.034641016151377525, -1.4100000000000001],
                                                 [-0.7101408311032397, -1.8000000000000003],
                                                 [-0.7101408311032397, -1.87],
                                                 [-0.034641016151377525, -1.4800000000000002]],
                                         'fill': '#ECE7DF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[-0.034641016151377525, -1.4100000000000001],
                                                 [0.536935750346352, -1.7400000000000002],
                                                 [0.536935750346352, -1.81],
                                                 [-0.034641016151377525, -1.4800000000000002]],
                                         'fill': '#E2DCD2',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[-0.034641016151377525, -1.4800000000000002],
                                                 [0.536935750346352, -1.81],
                                                 [-0.1385640646055102, -2.2],
                                                 [-0.7101408311032397, -1.87]],
                                         'fill': '#FFFFFF',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polyline',
                                         'pts': [[-0.16454482671904325, -1.76],
                                                 [0.060621778264910754, -1.8900000000000001]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[-0.42435244785437487, -1.9100000000000001],
                                                 [-0.19918584287042085, -2.04]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'polyline',
                                         'pts': [[-0.6841600689897065, -2.06], [-0.45899346400575247, -2.19]],
                                         'fill': 'none',
                                         'stroke': '#D9D4C7',
                                         'width': 0.04},
                                        {'kind': 'circle',
                                         'cx': -0.2771281292110204,
                                         'cy': -1.8600000000000003,
                                         'r': 0.055,
                                         'fill': '#D97757',
                                         'stroke': 'none',
                                         'width': 0}],
                          'waiting-tasks': [{'kind': 'polygon',
                                             'pts': [[0.9699484522385713, -0.96],
                                                     [0.060621778264910754, -1.485],
                                                     [0.060621778264910754, -2.3850000000000002],
                                                     [0.9699484522385713, -1.86]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9699484522385713, -0.96],
                                                     [1.706070045455344, -1.385],
                                                     [1.706070045455344, -2.285],
                                                     [0.9699484522385713, -1.86]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9699484522385713, -1.86],
                                                     [1.706070045455344, -2.285],
                                                     [0.7967433714816834, -2.81],
                                                     [0.060621778264910754, -2.3850000000000002]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9353074360871938, -1.9700000000000002],
                                                     [0.2598076211353316, -2.3600000000000003],
                                                     [0.2598076211353316, -2.43],
                                                     [0.9353074360871938, -2.04]],
                                             'fill': '#ECE7DF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9353074360871938, -1.9700000000000002],
                                                     [1.5068842025849232, -2.3],
                                                     [1.5068842025849232, -2.37],
                                                     [0.9353074360871938, -2.04]],
                                             'fill': '#E2DCD2',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[0.9353074360871938, -2.04],
                                                     [1.5068842025849232, -2.37],
                                                     [0.831384387633061, -2.7600000000000002],
                                                     [0.2598076211353316, -2.43]],
                                             'fill': '#FFFFFF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[0.805403625519528, -2.3200000000000003],
                                                     [1.030570230503482, -2.45]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[0.5455960043841964, -2.47], [0.7707626093681504, -2.6]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[0.2857883832488648, -2.62], [0.5109549882328188, -2.75]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'circle',
                                             'cx': 0.6928203230275509,
                                             'cy': -2.42,
                                             'r': 0.055,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0},
                                            {'kind': 'polygon',
                                             'pts': [[1.9398969044771426, -1.5200000000000002],
                                                     [1.0305702305034823, -2.0450000000000004],
                                                     [1.0305702305034823, -2.9450000000000003],
                                                     [1.9398969044771426, -2.4200000000000004]],
                                             'fill': '#DCC9AA',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9398969044771426, -1.5200000000000002],
                                                     [2.6760184976939154, -1.9450000000000003],
                                                     [2.6760184976939154, -2.8450000000000006],
                                                     [1.9398969044771426, -2.4200000000000004]],
                                             'fill': '#C7AE86',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9398969044771426, -2.4200000000000004],
                                                     [2.6760184976939154, -2.8450000000000006],
                                                     [1.7666918237202551, -3.3700000000000006],
                                                     [1.0305702305034823, -2.9450000000000003]],
                                             'fill': '#F3E9D8',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9052558883257655, -2.5300000000000002],
                                                     [1.229756073373903, -2.9200000000000004],
                                                     [1.229756073373903, -2.99],
                                                     [1.9052558883257655, -2.6000000000000005]],
                                             'fill': '#ECE7DF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9052558883257655, -2.5300000000000002],
                                                     [2.476832654823495, -2.8600000000000003],
                                                     [2.476832654823495, -2.9300000000000006],
                                                     [1.9052558883257655, -2.6000000000000005]],
                                             'fill': '#E2DCD2',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polygon',
                                             'pts': [[1.9052558883257655, -2.6000000000000005],
                                                     [2.476832654823495, -2.9300000000000006],
                                                     [1.8013328398716326, -3.3200000000000007],
                                                     [1.229756073373903, -2.99]],
                                             'fill': '#FFFFFF',
                                             'stroke': '#3D3929',
                                             'width': 0.035},
                                            {'kind': 'polyline',
                                             'pts': [[1.7753520777580998, -2.8800000000000003],
                                                     [2.0005186827420536, -3.0100000000000002]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[1.515544456622768, -3.0300000000000002],
                                                     [1.740711061606722, -3.16]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'polyline',
                                             'pts': [[1.2557368354874365, -3.1800000000000006],
                                                     [1.4809034404713903, -3.31]],
                                             'fill': 'none',
                                             'stroke': '#D9D4C7',
                                             'width': 0.04},
                                            {'kind': 'circle',
                                             'cx': 1.6627687752661224,
                                             'cy': -2.9800000000000004,
                                             'r': 0.055,
                                             'fill': '#D97757',
                                             'stroke': 'none',
                                             'width': 0}]},
                'moves': {'next-task': [-0.1299038105676658, 0.32500000000000007]}},
 'budget-slots': {'parts': {'tray': [{'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [-1.5588457268119895, -0.9],
                                              [-1.5588457268119895, -1.2],
                                              [0.0, -0.3]],
                                      'fill': '#26221F',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, 0.0],
                                              [3.117691453623979, -1.8],
                                              [3.117691453623979, -2.1],
                                              [0.0, -0.3]],
                                      'fill': '#1E1B18',
                                      'stroke': '#3D3929',
                                      'width': 0.035},
                                     {'kind': 'polygon',
                                      'pts': [[0.0, -0.3],
                                              [3.117691453623979, -2.1],
                                              [1.5588457268119895, -3.0],
                                              [-1.5588457268119895, -1.2]],
                                      'fill': '#3A3530',
                                      'stroke': '#3D3929',
                                      'width': 0.035}],
                            'available-tokens': [{'kind': 'polygon',
                                                  'pts': [[-0.10392304845413265, -0.52],
                                                          [-1.1864548031846809, -1.145],
                                                          [-1.1864548031846809, -1.395],
                                                          [-0.10392304845413265, -0.77]],
                                                  'fill': '#DCC9AA',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[-0.10392304845413265, -0.52],
                                                          [0.45899346400575247, -0.845],
                                                          [0.45899346400575247, -1.0950000000000002],
                                                          [-0.10392304845413265, -0.77]],
                                                  'fill': '#C7AE86',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[-0.10392304845413265, -0.77],
                                                          [0.45899346400575247, -1.0950000000000002],
                                                          [-0.6235382907247957, -1.7200000000000002],
                                                          [-1.1864548031846809, -1.395]],
                                                  'fill': '#F3E9D8',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.6321985447626401, -0.9450000000000001],
                                                          [-0.4503332099679081, -1.57],
                                                          [-0.4503332099679081, -1.82],
                                                          [0.6321985447626401, -1.195]],
                                                  'fill': '#DCC9AA',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.6321985447626401, -0.9450000000000001],
                                                          [1.195115057222525, -1.27],
                                                          [1.195115057222525, -1.52],
                                                          [0.6321985447626401, -1.195]],
                                                  'fill': '#C7AE86',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[0.6321985447626401, -1.195],
                                                          [1.195115057222525, -1.52],
                                                          [0.11258330249197693, -2.145],
                                                          [-0.4503332099679081, -1.82]],
                                                  'fill': '#F3E9D8',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[1.3683201379794128, -1.37],
                                                          [0.28578838324886463, -1.995],
                                                          [0.28578838324886463, -2.245],
                                                          [1.3683201379794128, -1.62]],
                                                  'fill': '#DCC9AA',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[1.3683201379794128, -1.37],
                                                          [1.9312366504392982, -1.695],
                                                          [1.9312366504392982, -1.945],
                                                          [1.3683201379794128, -1.62]],
                                                  'fill': '#C7AE86',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035},
                                                 {'kind': 'polygon',
                                                  'pts': [[1.3683201379794128, -1.62],
                                                          [1.9312366504392982, -1.945],
                                                          [0.8487048957087499, -2.57],
                                                          [0.28578838324886463, -2.245]],
                                                  'fill': '#F3E9D8',
                                                  'stroke': '#3D3929',
                                                  'width': 0.035}],
                            'allocated-token': [{'kind': 'polygon',
                                                 'pts': [[2.1044417311961854, -1.795],
                                                         [1.0219099764656372, -2.42],
                                                         [1.0219099764656372, -2.67],
                                                         [2.1044417311961854, -2.045]],
                                                 'fill': '#DCC9AA',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035},
                                                {'kind': 'polygon',
                                                 'pts': [[2.1044417311961854, -1.795],
                                                         [2.6673582436560705, -2.1199999999999997],
                                                         [2.6673582436560705, -2.37],
                                                         [2.1044417311961854, -2.045]],
                                                 'fill': '#C7AE86',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035},
                                                {'kind': 'polygon',
                                                 'pts': [[2.1044417311961854, -2.045],
                                                         [2.6673582436560705, -2.37],
                                                         [1.5848264889255224, -2.9949999999999997],
                                                         [1.0219099764656372, -2.67]],
                                                 'fill': '#F3E9D8',
                                                 'stroke': '#3D3929',
                                                 'width': 0.035}]},
                  'moves': {'allocated-token': [0.25980762113533157, -1.0]}},
 'recovery-dock': {'parts': {'base': [{'kind': 'polygon',
                                       'pts': [[0.0, 0.0],
                                               [-2.0784609690826525, -1.2],
                                               [-2.0784609690826525, -1.3499999999999999],
                                               [0.0, -0.15]],
                                       'fill': '#B4AFA6',
                                       'stroke': '#3D3929',
                                       'width': 0.035},
                                      {'kind': 'polygon',
                                       'pts': [[0.0, 0.0],
                                               [2.424871130596428, -1.4],
                                               [2.424871130596428, -1.5499999999999998],
                                               [0.0, -0.15]],
                                       'fill': '#8B8F96',
                                       'stroke': '#3D3929',
                                       'width': 0.035},
                                      {'kind': 'polygon',
                                       'pts': [[0.0, -0.15],
                                               [2.424871130596428, -1.5499999999999998],
                                               [0.34641016151377535, -2.7499999999999996],
                                               [-2.0784609690826525, -1.3499999999999999]],
                                       'fill': '#D9D4C7',
                                       'stroke': '#3D3929',
                                       'width': 0.035}],
                             'rails': [{'kind': 'polygon',
                                        'pts': [[0.04330127018922192, -0.375],
                                                [-1.6887495373796555, -1.375],
                                                [-1.6887495373796555, -1.625],
                                                [0.04330127018922192, -0.625]],
                                        'fill': '#26221F',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[0.04330127018922192, -0.375],
                                                [0.30310889132455354, -0.525],
                                                [0.30310889132455354, -0.775],
                                                [0.04330127018922192, -0.625]],
                                        'fill': '#1E1B18',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[0.04330127018922192, -0.625],
                                                [0.30310889132455354, -0.775],
                                                [-1.4289419162443238, -1.775],
                                                [-1.6887495373796555, -1.625]],
                                        'fill': '#3A3530',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.6887495373796553, -1.325],
                                                [-0.04330127018922216, -2.3249999999999997],
                                                [-0.04330127018922216, -2.5749999999999997],
                                                [1.6887495373796553, -1.5750000000000002]],
                                        'fill': '#26221F',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.6887495373796553, -1.325],
                                                [1.9485571585149866, -1.4749999999999999],
                                                [1.9485571585149866, -1.725],
                                                [1.6887495373796553, -1.5750000000000002]],
                                        'fill': '#1E1B18',
                                        'stroke': '#3D3929',
                                        'width': 0.035},
                                       {'kind': 'polygon',
                                        'pts': [[1.6887495373796553, -1.5750000000000002],
                                                [1.9485571585149866, -1.725],
                                                [0.21650635094610926, -2.725],
                                                [-0.04330127018922216, -2.5749999999999997]],
                                        'fill': '#3A3530',
                                        'stroke': '#3D3929',
                                        'width': 0.035}],
                             'module': [{'kind': 'polygon',
                                         'pts': [[0.17320508075688773, -1.6500000000000001],
                                                 [-1.12583302491977, -2.4000000000000004],
                                                 [-1.12583302491977, -3.0],
                                                 [0.17320508075688773, -2.25]],
                                         'fill': '#DCC9AA',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.17320508075688773, -1.6500000000000001],
                                                 [1.3856406460551016, -2.35],
                                                 [1.3856406460551016, -2.95],
                                                 [0.17320508075688773, -2.25]],
                                         'fill': '#C7AE86',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'polygon',
                                         'pts': [[0.17320508075688773, -2.25],
                                                 [1.3856406460551016, -2.95],
                                                 [0.08660254037844374, -3.7],
                                                 [-1.12583302491977, -3.0]],
                                         'fill': '#F3E9D8',
                                         'stroke': '#3D3929',
                                         'width': 0.035},
                                        {'kind': 'circle',
                                         'cx': 0.7967433714816836,
                                         'cy': -2.29,
                                         'r': 0.07,
                                         'fill': '#D97757',
                                         'stroke': 'none',
                                         'width': 0}]},
                   'moves': {'module': [0.0, 0.68]}},
 'release-parcel': {'parts': {'package': [{'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [-2.0784609690826525, -1.2],
                                                   [-2.0784609690826525, -2.45],
                                                   [0.0, -1.25]],
                                           'fill': '#DCC9AA',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, 0.0],
                                                   [2.1650635094610964, -1.25],
                                                   [2.1650635094610964, -2.5],
                                                   [0.0, -1.25]],
                                           'fill': '#C7AE86',
                                           'stroke': '#3D3929',
                                           'width': 0.035},
                                          {'kind': 'polygon',
                                           'pts': [[0.0, -1.25],
                                                   [2.1650635094610964, -2.5],
                                                   [0.08660254037844393, -3.7],
                                                   [-2.0784609690826525, -2.45]],
                                           'fill': '#F3E9D8',
                                           'stroke': '#3D3929',
                                           'width': 0.035}],
                              'lid': [{'kind': 'polygon',
                                       'pts': [[0.0, -1.23],
                                               [-2.199704525612474, -2.5],
                                               [-2.199704525612474, -2.7],
                                               [0.0, -1.43]],
                                       'fill': '#DCC9AA',
                                       'stroke': '#3D3929',
                                       'width': 0.035},
                                      {'kind': 'polygon',
                                       'pts': [[0.0, -1.23],
                                               [2.286307065990918, -2.5500000000000003],
                                               [2.286307065990918, -2.75],
                                               [0.0, -1.43]],
                                       'fill': '#C7AE86',
                                       'stroke': '#3D3929',
                                       'width': 0.035},
                                      {'kind': 'polygon',
                                       'pts': [[0.0, -1.43],
                                               [2.286307065990918, -2.75],
                                               [0.08660254037844393, -4.0200000000000005],
                                               [-2.199704525612474, -2.7]],
                                       'fill': '#F3E9D8',
                                       'stroke': '#3D3929',
                                       'width': 0.035},
                                      {'kind': 'polyline',
                                       'pts': [[1.0825317547305482, -2.135], [-0.9959292143521044, -3.335]],
                                       'fill': 'none',
                                       'stroke': '#8B8F96',
                                       'width': 0.22},
                                      {'kind': 'circle',
                                       'cx': 0.1299038105676657,
                                       'cy': -2.705,
                                       'r': 0.1,
                                       'fill': '#D97757',
                                       'stroke': 'none',
                                       'width': 0}],
                              'packing-slip': [{'kind': 'polygon',
                                                'pts': [[2.2949673200287624, -1.505],
                                                        [1.169134295108992, -2.155],
                                                        [1.169134295108992, -2.225],
                                                        [2.2949673200287624, -1.575]],
                                                'fill': '#ECE7DF',
                                                'stroke': '#3D3929',
                                                'width': 0.035},
                                               {'kind': 'polygon',
                                                'pts': [[2.2949673200287624, -1.505],
                                                        [3.1609927238132007, -2.005],
                                                        [3.1609927238132007, -2.0749999999999997],
                                                        [2.2949673200287624, -1.575]],
                                                'fill': '#E2DCD2',
                                                'stroke': '#3D3929',
                                                'width': 0.035},
                                               {'kind': 'polygon',
                                                'pts': [[2.2949673200287624, -1.575],
                                                        [3.1609927238132007, -2.0749999999999997],
                                                        [2.0351596988934304, -2.725],
                                                        [1.169134295108992, -2.225]],
                                                'fill': '#FFFFFF',
                                                'stroke': '#3D3929',
                                                'width': 0.035},
                                               {'kind': 'polyline',
                                                'pts': [[2.1650635094610964, -1.855], [2.6846787517317594, -2.155]],
                                                'fill': 'none',
                                                'stroke': '#D9D4C7',
                                                'width': 0.04},
                                               {'kind': 'polyline',
                                                'pts': [[1.905255888325765, -2.005],
                                                        [2.424871130596428, -2.3049999999999997]],
                                                'fill': 'none',
                                                'stroke': '#D9D4C7',
                                                'width': 0.04},
                                               {'kind': 'polyline',
                                                'pts': [[1.6454482671904334, -2.155],
                                                        [2.1650635094610964, -2.4549999999999996]],
                                                'fill': 'none',
                                                'stroke': '#D9D4C7',
                                                'width': 0.04},
                                               {'kind': 'circle',
                                                'cx': 1.6021469970012112,
                                                'cy': -2.215,
                                                'r': 0.055,
                                                'fill': '#D97757',
                                                'stroke': 'none',
                                                'width': 0}]},
                    'moves': {'lid': [0.0, -0.8]}}}

def make_original(prop_id, height=3.2, x=0.0, y=0.0):
    """Return native VGroup with .parts and scale-correct .action_vectors."""
    from manim import VGroup, Polygon, VMobject, Circle
    import numpy as np
    if not np.isfinite(height) or height <= 0:
        raise ValueError('height must be positive and finite')
    p = _ST_ORIGINALS_25[prop_id]
    pts = []
    for name, shapes in p['parts'].items():
        dx, dy = p['moves'].get(name, (0, 0))
        for s in shapes:
            q = s.get('pts') or [(s['cx']-s['r'],s['cy']-s['r']), (s['cx']+s['r'],s['cy']+s['r'])]
            pts.extend(q)
            pts.extend((a+dx, b+dy) for a,b in q)
    x0,y0 = min(a for a,b in pts), min(b for a,b in pts)
    x1,y1 = max(a for a,b in pts), max(b for a,b in pts)
    scale = min(height/(y1-y0), 4.8/(x1-x0))
    cx,cy = (x0+x1)/2, (y0+y1)/2
    def point(a,b): return np.array([(a-cx)*scale+x, -(b-cy)*scale+y, 0])
    rig = VGroup()
    rig.parts, rig.action_vectors = {}, {}
    for name, shapes in p['parts'].items():
        part = VGroup()
        for s in shapes:
            if s['kind'] == 'circle':
                mob = Circle(radius=s['r']*scale).move_to(point(s['cx'],s['cy']))
            elif s['kind'] == 'polygon':
                mob = Polygon(*[point(a,b) for a,b in s['pts']])
            else:
                mob = VMobject().set_points_as_corners([point(a,b) for a,b in s['pts']])
            mob.set_fill(s['fill'] if s['fill']!='none' else '#FFFFFF', opacity=0 if s['fill']=='none' else 1)
            mob.set_stroke(s['stroke'] if s['stroke']!='none' else '#FFFFFF', width=s['width']*100, opacity=0 if s['stroke']=='none' else 1)
            part.add(mob)
        rig.parts[name] = part
        rig.add(part)
        if name in p['moves']:
            dx,dy = p['moves'][name]
            rig.action_vectors[name] = np.array([dx*scale, -dy*scale, 0])
    return rig



# ═════════════════════════ FILM HELPERS (ClaimCheck, four-part project film) ═════════════════════════
# This block is appended after iso_kit.py and iso_originals_25.py by build_scenes.py; scenes.py is the
# single self-contained file Gate A copies. Cast for the whole film: the claim file (binder), a quote slip,
# the inspection lamp (the checker), the stamp (the human gate), kraft crates and question cards.
_HERE = _os.path.dirname(_os.path.abspath(__file__))
PARTS = {1: "1 · Summary", 2: "2 · Prior work", 3: "3 · Methods", 4: "4 · Evaluation"}
PNG_LOGOS = {"github-01"}   # its SVG uses an even-odd fill Manim drops; the 1024 px PNG is used
CONNECT = "#9C8462"   # deep kraft for connector lines (ink connectors fuse into text blobs at GATE T)


def chip(n):
    t = T(PARTS[n], 34)
    t.move_to(np.array([-6.05 + t.width / 2, 3.08, 0.0]))
    return t


def lab(s, x, y, size=40):
    return T(s, size).move_to(np.array([x, y, 0.0]))


def hero(s, x, y, size=120):
    return T(s, size, bold=True).move_to(np.array([x, y, 0.0]))


def floor(x, y, w=3.6, h=0.7):
    return Ellipse(width=w, height=h, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to(np.array([x, y, 0.0]))


def cross(x, y, s=0.22, color=INK, w=8):
    return VGroup(Line([x - s, y - s, 0], [x + s, y + s, 0], color=color, stroke_width=w),
                  Line([x - s, y + s, 0], [x + s, y - s, 0], color=color, stroke_width=w))


def scrib(x, y, w):
    """One handwriting line, tall enough to clear GATE T's 41 px type floor at 4K."""
    return scribble(x, y, w, amp=0.095, sw=5)


def scrib_block(x, y, w, n=3, gap=0.34, last=0.62):
    return VGroup(*[scrib(x, y - i * gap, w * (last if i == n - 1 else 1.0)) for i in range(n)])


def page(x, y, w, h, tilt=0.0):
    """kit paper() with a grey edge: DIM is above GATE T's ink threshold, so the edge is not type."""
    pg = paper(x, y, w=w, h=h, tilt=tilt)
    pg.sheet.set_stroke(DIM, width=4)
    return pg


def scrib_on(pg, n=3, inset=0.28, gap=0.3):
    w = pg.w - 2 * inset
    return scrib_block(pg.cx - w / 2, pg.cy + pg.h / 2 - inset - 0.12, w, n=n, gap=gap)


def slip(x, y, w=2.6, h=1.2, n=2, tab=False):
    """A flat answer slip: white page with a grey edge, kraft shadow, n handwriting lines, optional tab."""
    pg = page(x, y, w, h)
    g = VGroup(pg, scrib_on(pg, n=n))
    if tab:
        g.add(Rectangle(width=0.42, height=0.3, fill_color=BOX_R, fill_opacity=1, stroke_color=INK, stroke_width=3)
              .move_to(np.array([x + w / 2 - 0.1, y - h / 2 + 0.05, 0.0])))
    return g


def qcard(x, y, w=0.6, h=0.82, fill=BOX_L):
    return RoundedRectangle(width=w, height=h, corner_radius=0.06, fill_color=fill, fill_opacity=1,
                            stroke_color=INK, stroke_width=3).move_to(np.array([x, y, 0.0]))


def crate(x, y, s=1.0, ghost=False, h=0.75):
    iso = Iso(x, y, s)
    if ghost:
        # planned, not built: card-white faces (Gate V treats them as background) carried by DIM outlines
        return iso.box(-0.5, -0.5, 0, 1, 1, h, top=CARD, left=CARD, right=CARD, sw=4).set_stroke(DIM, width=5)
    return iso.box(-0.5, -0.5, 0, 1, 1, h)


def logo(name, height=0.9, x=0.0, y=0.0):
    if name in PNG_LOGOS:
        m = ImageMobject(_os.path.join(_HERE, "images", f"{name}.png"))
    else:
        m = SVGMobject(_os.path.join(_HERE, "images", f"{name}.svg"))
    m.scale_to_fit_height(height)
    m.move_to(np.array([x, y, 0.0]))
    return m


def _bid(s):
    return type(s).__name__.split("_")[0]


def gplay(s, *anims, run_time=0.6, **kw):
    """play(), but never across the clip midpoint, where GATE T and Gate V sample a still."""
    target = _TARGET.get(_bid(s), 0) or 10.0
    mid, m, now = target / 2, 0.24, _elapsed(s)
    if now < mid + m and now + run_time > mid - m:
        s.wait(max(0.02, mid + m + 0.02 - now))
    s.play(*anims, run_time=run_time, **kw)


def done(s):
    """Hold to the end of the narration, leaving 0.05 s of slack so the clip never outruns its audio."""
    target = _TARGET.get(_bid(s), 0)
    now = _elapsed(s)
    if not target:
        s.wait(2.0)
        return
    if now > target - 0.05:
        print(f"[timing] {_bid(s)} OVERRUN {now:.2f}s of {target:.2f}s")
        return
    s.wait(target - now - 0.05)


def binder_set():
    b = make_original('evidence-binder', height=2.5, x=-2.4, y=-0.1)
    sh = floor(-2.4, -1.0, 4.2, 0.6)
    sh.set_z_index(-1)
    return b, sh, lab("claim file", -2.4, -1.95, 42)


# ═════════════════════════ PART 1 · EXECUTIVE SUMMARY ═════════════════════════
class B00_ClaimFile(Scene):
    def construct(self):
        self.add(chip(1))
        binder, sh, cf = binder_set()
        binder.shift(UP * 5)
        self.play(binder.animate.shift(DOWN * 5), FadeIn(sh), run_time=0.8, rate_func=ease_in)
        self.play(FadeIn(cf), run_time=0.4)
        until(self, "Is this covered")
        q = slip(2.9, 0.5, w=3.2, h=1.5, n=2)
        gplay(self, FadeIn(q, shift=RIGHT * 2.4), run_time=0.8)
        gplay(self, FadeIn(lab("question", 2.9, -0.75, 42)), run_time=0.4)
        done(self)


class B01_QuoteOrRefuse(Scene):
    def construct(self):
        binder, sh, cf = binder_set()
        q = slip(2.9, 0.5, w=3.2, h=1.5, n=2)
        qlab = lab("question", 2.9, -0.75, 42)
        self.add(chip(1), sh, binder, cf, q, qlab)
        self.play(FadeOut(qlab), FadeOut(q, shift=UP * 0.4), run_time=0.7)
        until(self, "word-for-word quote")
        gplay(self, binder.parts['cover'].animate.shift(binder.action_vectors['cover']), run_time=0.5)
        a = slip(2.9, 0.35, w=3.2, h=1.1, n=1)
        gplay(self, FadeIn(a, shift=RIGHT * 2.0), run_time=0.7)
        gplay(self, FadeIn(lab("quote", 2.9, -0.65, 42)), run_time=0.3)
        until(self, "checked against the file")
        gplay(self, Create(check(4.95, 0.45, 0.24)), run_time=0.4)
        until(self, "If no clause answers")
        r = slip(2.9, -1.65, w=3.2, h=1.0, n=0)
        gplay(self, FadeIn(r, shift=RIGHT * 2.0), run_time=0.6)
        gplay(self, Create(Line([2.3, -1.65, 0], [3.5, -1.65, 0], color=INK, stroke_width=8)),
              FadeIn(lab("refuse", 2.9, -2.55, 42)), run_time=0.4)
        done(self)


class B02_LookAlike(Scene):
    def construct(self):
        self.add(chip(1))
        A = slip(-2.6, 1.3, w=3.4, h=1.5, n=2, tab=True)
        B = slip(2.6, 1.3, w=3.4, h=1.5, n=2, tab=True)
        pol = page(0.0, -1.75, 10.4, 1.5)
        rows = VGroup(*[scrib(-4.6 + i * 3.4, -1.75, 2.4) for i in range(3)])
        self.play(FadeIn(A, shift=UP * 0.4), FadeIn(B, shift=UP * 0.4), FadeIn(pol), FadeIn(rows), run_time=0.8)
        until(self, "cites the wrong clause")
        gplay(self, FadeIn(lab("same look", 0.0, 2.45, 42)), run_time=0.4)
        until(self, "looks exactly like a right one")
        l1 = Line([-1.0, 0.42, 0], [0.0, -0.98, 0], color=CONNECT, stroke_width=6)
        l2 = Line([4.2, 0.42, 0], [3.4, -0.98, 0], color=CONNECT, stroke_width=6)
        gplay(self, Create(l1), Create(l2), run_time=0.6)
        gplay(self, Create(check(0.55, -0.62, 0.2)), Create(cross(3.95, -0.62, 0.18)), run_time=0.4)
        gplay(self, FadeIn(lab("right clause", 0.0, -2.9, 38)), FadeIn(lab("wrong clause", 3.4, -2.9, 38)), run_time=0.4)
        done(self)


def mini_stamp(x, y):
    """B12's stamp, smaller; (x, y) is the centre of its base."""
    g = VGroup(
        RoundedRectangle(width=0.8, height=0.27, corner_radius=0.1, fill_color=BOX_R, fill_opacity=1,
                         stroke_color=INK, stroke_width=4).move_to([x, y + 0.78, 0]),
        Rectangle(width=0.28, height=0.5, fill_color=BOX_L, fill_opacity=1, stroke_color=INK,
                  stroke_width=4).move_to([x, y + 0.4, 0]),
        RoundedRectangle(width=1.1, height=0.3, corner_radius=0.08, fill_color=DARK_TOP, fill_opacity=1,
                         stroke_color=INK, stroke_width=4).move_to([x, y, 0]))
    g.set_z_index(4)
    return g


class B02B_Consequence(Scene):
    def construct(self):
        self.add(chip(1))
        L, R = -3.3, 3.3
        pages, slips = [], []
        for x, name in ((L, "excluded claim"), (R, "covered claim")):
            pg = page(x, 0.35, 3.6, 3.0)
            lines = scrib_block(x - 1.45, 1.45, 1.9, n=2, gap=0.36, last=0.6)
            sl = slip(x - 0.55, -0.3, w=2.1, h=0.85, n=0, tab=True)
            sl.set_z_index(2)
            pages.append(VGroup(pg, lines, lab(name, x, 2.35, 40)))
            slips.append(sl)
        self.play(*[FadeIn(p_, shift=UP * 0.3) for p_ in pages], *[FadeIn(s_) for s_ in slips], run_time=0.8)
        for ph, x, word in (("could pay a claim", L, "paid"), ("or deny a covered claim", R, "denied")):
            until(self, ph)
            mx, my = x + 1.05, -0.35
            st = mini_stamp(mx, my + 1.0)
            ring = Circle(radius=0.3, stroke_color=INK, stroke_width=6, fill_opacity=0).move_to([mx, my, 0])
            ring.set_z_index(3)
            gplay(self, FadeIn(st), run_time=0.25)
            gplay(self, st.animate.shift(DOWN * 0.85), run_time=0.3, rate_func=ease_in)
            gplay(self, st.animate.shift(UP * 0.85), Create(ring), run_time=0.35)
            w = lab(word, x, -1.6, 42)
            gplay(self, FadeOut(st), FadeIn(w), Create(cross(x + w.width / 2 + 0.4, -1.6, 0.18)), run_time=0.35)
        until(self, "Either way")
        ticks = [check(s_.get_center()[0] - 0.15, -0.3, 0.2) for s_ in slips]
        for k in ticks:
            k.set_z_index(3)   # above the slips (z 2)
        gplay(self, *[Create(k) for k in ticks], run_time=0.4)
        until(self, "look checked")
        gplay(self, FadeIn(lab("looks checked", 0.0, -2.55, 42)), run_time=0.3)
        done(self)


class B03_Roadmap(Scene):
    def construct(self):
        self.add(chip(1))
        rail = RoundedRectangle(width=11.6, height=0.22, corner_radius=0.11, fill_color=BAR2, fill_opacity=1,
                                stroke_width=0).move_to([0, -1.05, 0])
        xs = [-4.4, -1.47, 1.47, 4.4]
        built = crate(xs[0], -1.0, 1.2)
        ghosts = [crate(x, -1.0, 1.2, ghost=True) for x in xs[1:]]
        self.play(FadeIn(rail), FadeIn(built, shift=DOWN * 0.4), run_time=0.7)
        gplay(self, FadeIn(lab("runs today", xs[0], -2.2, 40)), run_time=0.4)
        until(self, "The rest of this film covers")
        gplay(self, *[FadeIn(g) for g in ghosts], FadeIn(lab("parts 2–4", 2.94, 1.25, 40)), run_time=0.6)
        for x, ph in zip(xs[1:], ["what others have done", "how I'll build it", "how I'll know it worked"]):
            until(self, ph)
            gplay(self, GrowFromCenter(Dot([x, -0.1, 0], radius=0.11, color=TERRA)), run_time=0.3)
        done(self)


# ═════════════════════════ PART 2 · WHAT OTHERS HAVE DONE ═════════════════════════
class B04_SearchEngines(Scene):
    def construct(self):
        self.add(chip(2))
        pos = [(-4.55, 1.05), (-1.85, 1.05), (-4.55, -1.15), (-1.85, -1.15)]
        cards = [slip(x, y, w=2.4, h=1.8, n=3, tab=True) for x, y in pos]
        self.play(FadeIn(cards[0], shift=DOWN * 0.3), run_time=0.5)
        until(self, "AI search engines already cite sources")
        gplay(self, LaggedStart(*[FadeIn(c, shift=DOWN * 0.3) for c in cards[1:]], lag_ratio=0.25), run_time=0.9)
        until(self, "checked four of them")
        tabs = [Dot([x + 1.1, y - 0.85, 0], radius=0.07, color=TERRA) for x, y in pos]
        gplay(self, LaggedStart(*[GrowFromCenter(d) for d in tabs], lag_ratio=0.2), run_time=0.6)
        until(self, "only about half")
        num = hero("51.5%", 3.25, 1.0, 120)
        bar_o = RoundedRectangle(width=5.0, height=0.5, corner_radius=0.08, stroke_color=INK, stroke_width=4,
                                 fill_opacity=0).move_to([3.25, -0.45, 0])
        fill = Rectangle(width=5.0 * 0.515, height=0.5, fill_color=BAR1, fill_opacity=1, stroke_width=0)
        fill.move_to([3.25 - 2.5 + 5.0 * 0.515 / 2, -0.45, 0])
        gplay(self, FadeIn(num, shift=UP * 0.3), Create(bar_o), run_time=0.6)
        gplay(self, GrowFromEdge(fill, LEFT), run_time=0.8)
        gplay(self, FadeIn(lab("fully supported", 3.25, -1.25, 40)), FadeIn(lab("Liu et al., 2023", 3.25, -2.1, 32)),
              run_time=0.4)
        done(self)


class B05_LegalTools(Scene):
    def construct(self):
        self.add(chip(2))
        shelf = make_original('version-shelves', height=3.0, x=-3.9, y=0.25)
        self.play(FadeIn(shelf, shift=UP * 0.3), run_time=0.6)
        gplay(self, FadeIn(lab("case files", -3.9, -1.75, 40)), run_time=0.3)
        until(self, "fetch real cases first")
        gplay(self, shelf.parts['selected-version'].animate.shift(shelf.action_vectors['selected-version']), run_time=0.7)
        until(self, "Even so")
        xs = [0.4 + i * 1.05 for i in range(6)]
        slips_ = [slip(x, 1.05, w=0.85, h=1.2, n=0) for x in xs]
        gplay(self, LaggedStart(*[FadeIn(s_, shift=DOWN * 0.25) for s_ in slips_], lag_ratio=0.15), run_time=0.9)
        until(self, "hallucinated")
        gplay(self, FadeIn(hero("17–33%", 2.95, -0.75, 110), shift=UP * 0.3), run_time=0.5)
        until(self, "seventeen")
        gplay(self, Create(cross(xs[1], 1.05, 0.2)), run_time=0.3)
        until(self, "thirty-three")
        gplay(self, Create(cross(xs[4], 1.05, 0.2)), run_time=0.3)
        gplay(self, FadeIn(lab("hallucinated", 2.95, -1.85, 40)), FadeIn(lab("Magesh et al., 2024", 2.95, -2.6, 32)),
              run_time=0.4)
        done(self)


class B06_RealNotRight(Scene):
    def construct(self):
        self.add(chip(2))
        cl = logo("claude-01", 0.9, -5.45, 2.25)
        pg = page(-2.5, -0.4, 3.6, 3.8)
        hl = RoundedRectangle(width=3.2, height=0.36, corner_radius=0.08, fill_color=GHOST, fill_opacity=1,
                              stroke_width=0).move_to([-2.5, -0.1, 0])
        ls = scrib_block(-3.95, 0.9, 2.9, n=6, gap=0.5, last=0.6)
        pg.set_z_index(0); hl.set_z_index(1); ls.set_z_index(2)
        self.play(FadeIn(cl), FadeIn(pg), run_time=0.6)
        gplay(self, FadeIn(hl), Create(ls), FadeIn(lab("citations", -3.7, 2.25, 40)), run_time=0.8)
        until(self, "Its documentation guarantees")
        q = slip(2.9, 1.0, w=3.4, h=1.1, n=1)
        gplay(self, FadeIn(q, shift=LEFT * 0.4), run_time=0.5)
        until(self, "points to real text")
        gplay(self, Create(Line([1.15, 0.85, 0], [-0.95, -0.1, 0], color=CONNECT, stroke_width=6)), run_time=0.5)
        gplay(self, GrowFromCenter(Dot([-0.95, -0.1, 0], radius=0.09, color=TERRA)), run_time=0.2)
        until(self, "That makes a quote real")
        gplay(self, Create(check(2.15, -0.75, 0.24)), FadeIn(lab("real", 3.25, -0.8, 44)), run_time=0.4)
        until(self, "It doesn't make it the right one")
        ring = Circle(radius=0.24, stroke_color=INK, stroke_width=6, fill_opacity=0).move_to([2.2, -1.9, 0])
        gplay(self, Create(ring), FadeIn(lab("right?", 3.4, -1.95, 44)), run_time=0.4)
        done(self)


class B07A_TheGap(Scene):
    def construct(self):
        self.add(chip(2))
        studies = ((-3.3, "Liu et al., 2023", "4 AI search engines", "51.5%", "fully supported"),
                   (3.3, "Magesh et al., 2024", "Lexis+ AI, Westlaw AI", "17–33%", "hallucinated"))
        cards, finds = [], []
        for x, who, what, num, cap in studies:
            cards.append(VGroup(page(x, 0.5, 5.6, 3.5), lab(who, x, 1.8, 42), lab(what, x, 1.2, 36)))
            finds.append(VGroup(hero(num, x, 0.2, 96), lab(cap, x, -0.8, 38)))
        self.play(*[FadeIn(c_, shift=UP * 0.3) for c_ in cards], run_time=0.8)
        until(self, "wrong or unsupported")
        gplay(self, LaggedStart(*[FadeIn(f_, shift=UP * 0.2) for f_ in finds], lag_ratio=0.35), run_time=0.8)
        until(self, "That's the gap")
        gap = lab("the gap: catch it before the reader", 0.25, -2.2, 44)
        dot = Dot([-3.95, -2.2, 0], radius=0.09, color=TERRA)   # fixed coords: Gate A cannot measure text
        gplay(self, GrowFromCenter(dot), FadeIn(gap, shift=UP * 0.2), run_time=0.5)
        until(self, "before a reader relies on it")
        ring = Circle(radius=0.24, stroke_color=INK, stroke_width=6, fill_opacity=0)
        ring.move_to([4.55, -2.2, 0])
        gplay(self, Create(ring), run_time=0.35)
        done(self)


class B07_AddsTheCheck(Scene):
    def construct(self):
        self.add(chip(2))
        lamp = make_original('inspection-lamp', height=3.3, x=-2.3, y=0.15)
        self.play(FadeIn(lamp, shift=UP * 0.3), run_time=0.6)
        gplay(self, FadeIn(lab("the check", -2.3, -1.95, 42)), run_time=0.3)
        until(self, "ClaimCheck adds the check")
        gplay(self, lamp.parts['lamp-head'].animate.shift(lamp.action_vectors['lamp-head']), run_time=0.6)
        ev = lamp.parts['evidence']
        c = np.array(ev.get_center(), dtype=float)
        w_ = float(ev.width)
        gplay(self, Create(Line(c + np.array([-w_ * 0.3, 0.0, 0]), c + np.array([w_ * 0.3, 0.0, 0]), color=TERRA,
                                stroke_width=6)), run_time=0.5)
        until(self, "the tool should refuse when the file is silent")
        r = slip(3.0, 1.15, w=3.0, h=1.0, n=0)
        gplay(self, FadeIn(r, shift=LEFT * 0.4), run_time=0.4)
        gplay(self, Create(Line([2.4, 1.15, 0], [3.6, 1.15, 0], color=INK, stroke_width=8)), run_time=0.3)
        until(self, "it counts how often")
        board = RoundedRectangle(width=3.0, height=1.5, corner_radius=0.12, fill_color=CARD, fill_opacity=1,
                                 stroke_color=BAR1, stroke_width=4).move_to([3.0, -1.05, 0])
        gplay(self, FadeIn(board), FadeIn(lab("tally", 3.0, -2.2, 40)), run_time=0.4)
        marks = [Line([2.35 + i * 0.4, -1.45, 0], [2.35 + i * 0.4, -0.65, 0], color=INK, stroke_width=8) for i in range(4)]
        gplay(self, LaggedStart(*[Create(m) for m in marks], lag_ratio=0.3), run_time=0.8)
        done(self)


# ═════════════════════════ PART 3 · METHODS ═════════════════════════
class B08_FirstPiece(Scene):
    def construct(self):
        self.add(chip(3))
        pol = page(-4.65, 0.45, 2.3, 3.0)
        pls = scrib_on(pol, n=5, gap=0.42)
        self.play(FadeIn(pol, shift=UP * 0.3), Create(pls), run_time=0.7)
        until(self, "The first piece already runs")
        xs = [-2.45 + i * 0.8 for i in range(10)]
        cards = [qcard(x, 0.55) for x in xs]
        gplay(self, LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cards], lag_ratio=0.1), run_time=0.9)
        until(self, "a synthetic homeowner policy")
        gplay(self, FadeIn(lab("synthetic policy", -4.65, -1.5, 38)), run_time=0.4)
        until(self, "ten questions")
        gplay(self, FadeIn(lab("10 questions", 1.15, -0.25, 40)), run_time=0.3)
        until(self, "four of them traps")
        dots = [Dot([xs[i], 0.75, 0], radius=0.085, color=TERRA) for i in (5, 7, 8, 9)]
        gplay(self, *[GrowFromCenter(d) for d in dots], run_time=0.4)
        until(self, "frozen with a checksum")
        bar = RoundedRectangle(width=8.3, height=0.3, corner_radius=0.15, fill_color=DARK_TOP, fill_opacity=1,
                               stroke_color=INK, stroke_width=3).move_to([1.15, 1.32, 0])
        gplay(self, FadeIn(bar, shift=RIGHT * 0.5), run_time=0.5)
        gplay(self, FadeIn(lab("frozen", 1.15, 1.95, 40)), run_time=0.3)
        until(self, "seventeen tests passed")
        gplay(self, Create(check(-0.15, -1.35, 0.26)), FadeIn(lab("17 tests pass", 1.75, -1.4, 42)), run_time=0.5)
        done(self)


class B09_ContractChecker(Scene):
    def construct(self):
        self.add(chip(3))
        a = paper(-4.3, 0.35, w=2.8, h=2.7)
        self.play(FadeIn(a, shift=UP * 0.3), run_time=0.6)
        gplay(self, FadeIn(lab("fixed format", -4.3, -1.45, 40)), run_time=0.3)
        spec = [("an answer", 0.8, BAR1), ("a word-for-word quote", 0.95, BAR2), ("its document", 0.6, BAR1),
                ("and a status", 0.45, BAR2)]
        for i, (ph, wf, col) in enumerate(spec):
            until(self, ph)
            f = RoundedRectangle(width=2.2 * wf, height=0.28, corner_radius=0.1, fill_color=col, fill_opacity=1,
                                 stroke_width=0).move_to([-5.4 + 1.1 * wf, 1.2 - i * 0.55, 0])
            gplay(self, FadeIn(f, shift=RIGHT * 0.2), run_time=0.3)
        lamp = make_original('inspection-lamp', height=3.1, x=1.0, y=0.25)
        until(self, "Then plain code checks the quote")
        gplay(self, FadeIn(lamp, shift=UP * 0.3), FadeIn(lab("checker", 1.0, -1.75, 40)), run_time=0.5)
        gplay(self, lamp.parts['lamp-head'].animate.shift(lamp.action_vectors['lamp-head']), run_time=0.5)
        ev = lamp.parts['evidence']
        c = np.array(ev.get_center(), dtype=float)
        w_ = float(ev.width)
        gplay(self, Create(Line(c + np.array([-w_ * 0.3, 0, 0]), c + np.array([w_ * 0.3, 0, 0]), color=TERRA,
                                stroke_width=6)), run_time=0.4)
        until(self, "If not")
        gate = RoundedRectangle(width=0.32, height=2.9, corner_radius=0.12, fill_color=DARK_TOP, fill_opacity=1,
                                stroke_color=INK, stroke_width=3).move_to([4.75, 0.25, 0])
        gplay(self, GrowFromEdge(gate, DOWN), run_time=0.4)
        gplay(self, FadeIn(slip(3.55, -0.35, w=1.3, h=0.95, n=1), shift=RIGHT * 0.6), run_time=0.4)
        gplay(self, Create(cross(3.55, 0.55, 0.2)), FadeIn(lab("blocked", 4.75, -1.65, 40)), run_time=0.4)
        done(self)


def _token_top(i):
    return [-2.0 + i * 1.0, -1.95, 0]


class B10_AgentLoop(Scene):
    def construct(self):
        self.add(chip(3))
        cl = logo("claude-01", 1.1, -4.4, 1.3)
        lamp = make_original('inspection-lamp', height=2.3, x=1.25, y=1.25)
        tray = RoundedRectangle(width=3.3, height=0.7, corner_radius=0.1, fill_color=DARK_TOP, fill_opacity=1,
                                stroke_color=INK, stroke_width=3).move_to([-1.0, -2.2, 0])
        toks = [Iso(-2.0 + i * 1.0, -2.25, 0.5).box(-0.5, -0.5, 0, 1, 1, 0.6) for i in range(3)]
        self.play(FadeIn(cl), FadeIn(lamp), FadeIn(tray), *[FadeIn(t) for t in toks], run_time=0.6)
        until(self, "Claude answers")
        arr = Arrow([-3.6, 1.35, 0], [-0.15, 1.35, 0], color=INK, stroke_width=6, buff=0,
                    max_tip_length_to_length_ratio=0.12)
        gplay(self, GrowArrow(arr), GrowFromCenter(Dot(_token_top(0), radius=0.08, color=TERRA)), run_time=0.5)
        until(self, "On a failed check")
        arc = ArcBetweenPoints([-0.3, 0.6, 0], [-3.5, 0.6, 0], angle=-PI * 0.6, color=INK, stroke_width=6)
        gplay(self, Create(arc), run_time=0.6)
        gplay(self, GrowFromCenter(Dot([-3.5, 0.6, 0], radius=0.1, color=TERRA)),
              FadeIn(lab("retry once", -1.9, -0.8, 40)), run_time=0.3)
        until(self, "Claude gets one retry")
        gplay(self, GrowFromCenter(Dot(_token_top(1), radius=0.08, color=TERRA)), run_time=0.3)
        until(self, "If that fails too")
        ex = Arrow([2.55, 1.3, 0], [3.95, 1.3, 0], color=INK, stroke_width=6, buff=0, max_tip_length_to_length_ratio=0.2)
        stop = RegularPolygon(n=8, radius=0.55, fill_color=DARK_TOP, fill_opacity=1, stroke_color=INK,
                              stroke_width=3).move_to([4.65, 1.3, 0])
        gplay(self, GrowArrow(ex), GrowFromCenter(stop), run_time=0.5)
        gplay(self, FadeIn(lab("stop", 4.65, 0.35, 40)), run_time=0.3)
        until(self, "three model calls")
        gplay(self, GrowFromCenter(Dot(_token_top(2), radius=0.08, color=TERRA)),
              FadeIn(lab("3 calls", 1.95, -2.2, 40)), run_time=0.4)
        done(self)


class B11_ReadOnlyTools(Scene):
    def construct(self):
        self.add(chip(3))
        tb = make_original('tool-block', height=2.3, x=-4.3, y=0.7)
        gate = make_original('permission-gate', height=2.8, x=3.4, y=0.3)
        self.play(FadeIn(tb, shift=UP * 0.3), FadeIn(gate, shift=UP * 0.3), run_time=0.6)
        gplay(self, FadeIn(lab("read only", -4.3, -1.0, 42)), run_time=0.3)
        until(self, "search the claim file")
        gplay(self, tb.parts['tool'].animate.shift(tb.action_vectors['tool']), run_time=0.6)
        until(self, "A permission list")
        lst = page(-0.7, 0.95, 2.2, 1.7)
        rows = VGroup(*[RoundedRectangle(width=1.1, height=0.26, corner_radius=0.1, fill_color=BAR2, fill_opacity=1,
                                         stroke_width=0).move_to([-1.05, yy, 0]) for yy in (1.35, 0.6)])
        gplay(self, FadeIn(lst), Create(rows), run_time=0.5)
        gplay(self, Create(check(-0.05, 1.35, 0.16)), Create(check(-0.05, 0.6, 0.16)), run_time=0.4)
        until(self, "allows those two")
        gplay(self, gate.parts['barrier'].animate.shift(gate.action_vectors['barrier']), run_time=0.5)
        until(self, "refuses everything else")
        parcel = Iso(0.9, -1.75, 0.6).box(-0.5, -0.5, 0, 1, 1, 0.8, DARK_TOP, DARK_L, DARK_R)
        gplay(self, FadeIn(parcel, shift=RIGHT * 0.6), run_time=0.4)
        gplay(self, gate.parts['barrier'].animate.shift(-gate.action_vectors['barrier']), run_time=0.5)
        gplay(self, Create(cross(1.75, -0.95, 0.2)), FadeIn(lab("send", 0.9, -2.6, 40)), run_time=0.3)
        done(self)


class B12_HumanGate(Scene):
    def construct(self):
        self.add(chip(3))
        doc = page(-2.8, 0.2, 3.4, 3.0)
        hl = RoundedRectangle(width=2.9, height=0.34, corner_radius=0.08, fill_color=GHOST, fill_opacity=1,
                              stroke_width=0).move_to([-2.8, 0.19, 0])
        lines = scrib_block(-4.15, 1.15, 2.7, n=5, gap=0.48, last=0.55)
        doc.set_z_index(0); hl.set_z_index(1); lines.set_z_index(2)
        stamp = VGroup(
            RoundedRectangle(width=0.95, height=0.32, corner_radius=0.12, fill_color=BOX_R, fill_opacity=1,
                             stroke_color=INK, stroke_width=4).move_to([-1.9, 3.0, 0]),
            Rectangle(width=0.34, height=0.62, fill_color=BOX_L, fill_opacity=1, stroke_color=INK,
                      stroke_width=4).move_to([-1.9, 2.55, 0]),
            RoundedRectangle(width=1.4, height=0.36, corner_radius=0.08, fill_color=DARK_TOP, fill_opacity=1,
                             stroke_color=INK, stroke_width=4).move_to([-1.9, 2.08, 0]))
        stamp.set_z_index(4)
        dr = make_original('memory-drawers', height=2.8, x=3.5, y=0.25)
        self.play(FadeIn(doc, shift=UP * 0.3), Create(lines), FadeIn(stamp), FadeIn(dr), run_time=0.7)
        gplay(self, FadeIn(lab("human gate", -2.8, -1.7, 42)), run_time=0.3)
        until(self, "beside its highlighted quote")
        gplay(self, FadeIn(hl), run_time=0.4)
        until(self, "and approves")
        gplay(self, stamp.animate.shift(DOWN * 2.8), run_time=0.35, rate_func=ease_in)
        ring = Circle(radius=0.36, stroke_color=INK, stroke_width=6, fill_opacity=0).move_to([-1.9, -0.8, 0])
        ring.set_z_index(3)
        gplay(self, stamp.animate.shift(UP * 2.8), Create(ring), run_time=0.45)
        until(self, "that decision is saved")
        gplay(self, dr.parts['drawer'].animate.shift(dr.action_vectors['drawer']), run_time=0.5)
        rec = slip(-1.9, -0.8, w=1.0, h=0.7, n=1)
        rec.set_z_index(5)
        gplay(self, FadeIn(rec), run_time=0.3)
        target = np.array(dr.parts['drawer'].get_center(), dtype=float)
        gplay(self, rec.animate.move_to(target).scale(0.6), run_time=0.8)
        gplay(self, dr.parts['drawer'].animate.shift(-dr.action_vectors['drawer']), FadeOut(rec), run_time=0.4)
        gplay(self, FadeIn(lab("record", 3.5, -1.65, 42)), run_time=0.3)
        done(self)


class B13_Data(Scene):
    def construct(self):
        self.add(chip(3))
        cr = make_original('context-crate', height=3.0, x=-3.3, y=-0.1)
        cr.parts['crate-front'].set_z_index(3)
        cr.parts['lid'].set_z_index(4)
        self.play(FadeIn(cr, shift=UP * 0.3), run_time=0.6)
        gplay(self, FadeIn(lab("synthetic", -3.3, -2.0, 42)), run_time=0.3)
        until(self, "written for this project")
        gplay(self, cr.parts['lid'].animate.shift(cr.action_vectors['lid']), run_time=0.5)
        pages = [paper(-3.3 + dx, 0.55, w=1.0, h=1.3, tilt=t) for dx, t in [(-0.9, 0.12), (-0.3, -0.08), (0.3, 0.1), (0.9, -0.12)]]
        for p_ in pages:
            p_.set_z_index(2)
        gplay(self, LaggedStart(*[FadeIn(p_, shift=DOWN * 1.0) for p_ in pages], lag_ratio=0.2), run_time=0.9)
        until(self, "thirty to fifty questions")
        grid = [[qcard(0.9 + j * 0.8, 1.3 - r * 1.1, w=0.55, h=0.75) for j in range(6)] for r in range(3)]
        gplay(self, LaggedStart(*[FadeIn(VGroup(*row), shift=DOWN * 0.2) for row in grid], lag_ratio=0.3),
              FadeIn(lab("30–50 questions", 2.9, -1.95, 40)), run_time=0.9)
        until(self, "a third of them traps")
        trap = [(0, 1), (0, 4), (1, 0), (1, 3), (2, 2), (2, 5)]
        gplay(self, *[GrowFromCenter(Dot([0.9 + j * 0.8, 1.3 - r * 1.1 + 0.2, 0], radius=0.075, color=TERRA))
                      for r, j in trap], run_time=0.4)
        until(self, "someone other than me")
        other = [(0, 2), (1, 5), (2, 0)]
        gplay(self, *[FadeIn(qcard(0.9 + j * 0.8, 1.3 - r * 1.1, w=0.55, h=0.75, fill=BAR2)) for r, j in other],
              run_time=0.4)
        done(self)


class B14_Steps(Scene):
    def construct(self):
        self.add(chip(3))
        rail = RoundedRectangle(width=11.8, height=0.22, corner_radius=0.11, fill_color=BAR2, fill_opacity=1,
                                stroke_width=0).move_to([0, -1.25, 0])
        xs = [-4.8, -2.4, 0.0, 2.4, 4.8]
        ghosts = [crate(x, -1.2, 1.0, ghost=True) for x in xs]
        self.play(FadeIn(rail), *[FadeIn(g) for g in ghosts], run_time=0.6)
        for i, ph in enumerate(["One:", "Two:", "Three:", "Four:", "Five:"]):
            until(self, ph)
            gplay(self, FadeIn(crate(xs[i], -1.2, 1.0), shift=UP * 0.25), FadeIn(T(str(i + 1), 52).move_to([xs[i], 1.0, 0])),
                  run_time=0.45)
        gplay(self, FadeIn(lab("held-out", xs[4], -2.3, 40)), run_time=0.3)
        done(self)


class B15_Resources(Scene):
    def construct(self):
        self.add(chip(3))
        # two columns: what I have (left) and what is still unresolved (right)
        hv = lab("have", -3.3, 2.55, 46)
        div = Line([0.3, 2.75, 0], [0.3, -2.75, 0], color=DIM, stroke_width=4)
        ws = make_original('agent-workstation', height=2.3, x=-3.9, y=-1.05)
        self.play(FadeIn(hv), FadeIn(div), FadeIn(ws, shift=UP * 0.3), run_time=0.6)
        gplay(self, Create(check(-2.3, 2.55, 0.22)), run_time=0.3)
        until(self, "Python")
        lg = [logo(n, 0.75, -5.6 + i * 1.3, 1.4) for i, n in enumerate(["python-01", "anthropic-01", "claude-code-01", "github-01"])]
        lg[2].set_fill(INK, opacity=1).set_stroke(width=0)   # monochrome mark: GATE T §8.3
        gplay(self, LaggedStart(*[FadeIn(l_, shift=UP * 0.2) for l_ in lg], lag_ratio=0.2), run_time=0.8)
        until(self, "GitHub, and a")
        gplay(self, Create(check(-0.6, 1.4, 0.24)), run_time=0.3)
        until(self, "which is enough because")
        gplay(self, Create(check(-1.7, -1.05, 0.24)), FadeIn(lab("compute", -3.9, -2.55, 40)), run_time=0.4)
        until(self, "Still unresolved")
        un = lab("unresolved", 3.6, 2.55, 46)
        ring = Circle(radius=0.2, stroke_color=INK, stroke_width=6, fill_opacity=0).move_to([5.35, 2.55, 0])
        gplay(self, FadeIn(un), Create(ring), run_time=0.4)
        until(self, "an API key with token credits")
        tray = make_original('budget-slots', height=1.8, x=2.2, y=0.2)
        tray.remove(tray.parts['available-tokens'], tray.parts['allocated-token'])
        gplay(self, FadeIn(tray, shift=UP * 0.3), FadeIn(lab("API key", 2.2, -1.35, 40)), run_time=0.5)
        until(self, "under two dollars")
        gplay(self, FadeIn(lab("under $2, est.", 2.2, -2.0, 36)), run_time=0.3)
        until(self, "a second person")
        cards = [qcard(4.6 + i * 0.25, 0.3 - i * 0.14, w=0.8, h=1.1, fill=BAR2) for i in range(3)]
        gplay(self, LaggedStart(*[FadeIn(c_, shift=DOWN * 0.2) for c_ in cards], lag_ratio=0.3),
              FadeIn(lab("second writer", 4.85, -1.35, 40)), run_time=0.6)
        done(self)


# ═════════════════════════ PART 4 · EVALUATION ═════════════════════════
class B17_TraceableNotRight(Scene):
    def construct(self):
        self.add(chip(4))
        lamp = make_original('inspection-lamp', height=2.5, x=-3.3, y=1.0)
        xs = [-5.1, -3.9, -2.7, -1.5]
        slips_ = [slip(x, -1.35, w=0.95, h=0.8, n=0) for x in xs]
        trays = make_original('comparison-trays', height=2.6, x=3.0, y=0.4)
        self.play(FadeIn(lamp, shift=UP * 0.3), *[FadeIn(s_) for s_ in slips_], FadeIn(trays, shift=UP * 0.3), run_time=0.6)
        gplay(self, FadeIn(lab("checker", -3.3, -2.45, 42)), FadeIn(lab("gold", 3.0, -1.4, 42)), run_time=0.3)
        until(self, "so all four passed the checker")
        gplay(self, LaggedStart(*[Create(check(x, -0.6, 0.15)) for x in xs], lag_ratio=0.2), run_time=0.7)
        until(self, "Only grading against gold")
        gplay(self, trays.parts['sample-b'].animate.shift(trays.action_vectors['sample-b']), run_time=0.6)
        gplay(self, Create(cross(5.1, 1.5, 0.24)), run_time=0.3)
        done(self)


class B18_TheBar(Scene):
    def construct(self):
        self.add(chip(4))
        panel = RoundedRectangle(width=1.3, height=4.3, corner_radius=0.18, fill_color=DARK_TOP, fill_opacity=1,
                                 stroke_color=INK, stroke_width=3).move_to([-3.6, 0.0, 0])
        ys = [1.35, 0.0, -1.35]
        sockets = [Circle(radius=0.32, fill_color=GHOST, fill_opacity=1, stroke_width=0).move_to([-3.6, y, 0]) for y in ys]
        self.play(FadeIn(panel), *[FadeIn(s_) for s_ in sockets], run_time=0.6)
        rows = [("Zero wrong answers", "0 wrong answers"), ("Every not-in-the-documents trap", "100% of traps refused"),
                ("every answerable question", "100% answered correctly")]
        for y, (ph, txt) in zip(ys, rows):
            until(self, ph)
            lit = Circle(radius=0.32, fill_color=TERRA, fill_opacity=1, stroke_width=0).move_to([-3.6, y, 0])
            t = T(txt, 46)
            t.move_to([-2.55 + t.width / 2, y, 0])
            gplay(self, GrowFromCenter(lit), FadeIn(t, shift=RIGHT * 0.2), run_time=0.4)
        until(self, "Refusing everything")
        p2 = RoundedRectangle(width=1.0, height=3.5, corner_radius=0.15, fill_color=DARK_TOP, fill_opacity=1,
                              stroke_color=INK, stroke_width=3).move_to([4.6, -0.1, 0])
        l2 = [Circle(radius=0.25, fill_color=TERRA if i < 2 else GHOST, fill_opacity=1, stroke_width=0)
              .move_to([4.6, y * 0.8 - 0.1, 0]) for i, y in enumerate(ys)]
        gplay(self, FadeIn(p2), *[GrowFromCenter(l_) for l_ in l2], FadeIn(lab("refuse all", 4.6, 2.25, 40)), run_time=0.5)
        gplay(self, Create(cross(5.55, ys[2] * 0.8 - 0.1, 0.2)), run_time=0.3)
        done(self)


class B19_BreakItOnPurpose(Scene):
    def construct(self):
        self.add(chip(4))
        gate = make_original('permission-gate', height=2.6, x=-3.6, y=0.6)
        trays = make_original('comparison-trays', height=2.4, x=3.3, y=0.4)
        self.play(FadeIn(gate, shift=UP * 0.3), FadeIn(trays, shift=UP * 0.3), run_time=0.6)
        until(self, "misses any one")
        s1 = slip(-5.6, -1.55, w=1.2, h=0.85, n=0)
        gplay(self, FadeIn(s1), run_time=0.3)
        gplay(self, s1.animate.move_to([-1.6, -1.55, 0]), run_time=0.9)
        gplay(self, Create(cross(-1.6, -0.75, 0.2)), FadeIn(lab("fail", -1.6, -2.45, 42)), run_time=0.4)
        until(self, "replay an answer")
        rec = VGroup(slip(3.0, 2.25, w=1.6, h=0.95, n=1), Dot([2.42, 2.52, 0], radius=0.07, color=TERRA))
        gplay(self, FadeIn(rec, shift=DOWN * 0.3), FadeIn(lab("replay", 1.15, 2.25, 40)), run_time=0.4)
        gplay(self, rec.animate.move_to([3.3, 1.05, 0]).scale(0.7), run_time=0.8)
        until(self, "show the gold grade catches it")
        gplay(self, Create(cross(5.05, 1.4, 0.22)), FadeIn(lab("caught", 3.3, -1.35, 42)), run_time=0.4)
        done(self)


class B20_Limit(Scene):
    def construct(self):
        self.add(chip(4))
        cr = make_original('context-crate', height=2.4, x=-2.6, y=0.0)
        bound = RoundedRectangle(width=5.6, height=4.5, corner_radius=0.3, stroke_color=INK, stroke_width=4,
                                 fill_opacity=0).move_to([-2.6, -0.05, 0])
        self.play(FadeIn(cr, shift=UP * 0.3), run_time=0.6)
        gplay(self, FadeIn(lab("this file", -2.6, -2.65, 42)), run_time=0.3)
        until(self, "the data is synthetic")
        gplay(self, Create(bound), run_time=0.7)
        until(self, "works on this file")
        gplay(self, Create(check(-0.7, 1.35, 0.26)), run_time=0.4)
        until(self, "not on real claims")
        real = VGroup(*[paper(3.6 + d, 0.35 + d, w=1.9, h=2.4) for d in (0.24, 0.12, 0.0)])
        gplay(self, FadeIn(real, shift=LEFT * 0.3), FadeIn(lab("real claims", 3.6, -1.45, 42)), run_time=0.5)
        done(self)


class BOUT_Title(Scene):
    def construct(self):
        title = T("Quote It or Refuse.", 96).move_to([0, 0.75, 0])
        self.play(FadeIn(title, shift=UP * 0.2), run_time=0.6)
        gplay(self, Create(Line([-3.2, -0.15, 0], [3.2, -0.15, 0], color=INK, stroke_width=5)),
              GrowFromCenter(Dot([3.45, -0.15, 0], radius=0.09, color=TERRA)), run_time=0.5)
        gplay(self, FadeIn(lab("ClaimCheck · Shreyash Yadav · INFO 7375", 0, -0.85, 42)),
              FadeIn(lab("Narration: AI voice (Kokoro) reading my script", 0, -1.6, 32)),
              GrowFromCenter(Dot([-3.45, -0.15, 0], radius=0.09, color=TERRA)), run_time=0.5)
        done(self)
