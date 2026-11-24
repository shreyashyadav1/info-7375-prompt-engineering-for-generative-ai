
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
