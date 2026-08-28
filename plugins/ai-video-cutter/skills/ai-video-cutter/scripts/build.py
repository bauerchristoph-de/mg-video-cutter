# -*- coding: utf-8 -*-
"""
AI Video-Cutter · build.py — erzeugt alle Overlay-Assets eines Videos.

Eingabe:  kunden-config.yaml (Stil des Kunden) + cut-plan.json (dieses Video)
Ausgabe:  <out>/ovl/f00000.png ...   Overlay-Frames (RGBA, transparent)
          <out>/events.json          SFX-Events für make_sfx.py
          <out>/build-report.json    was gebaut wurde (Basis für qc.py)

Warum dieses Skript existiert
-----------------------------
Vorher wurde die Untertitel-Erzeugung pro Video neu geschrieben. Ergebnis:
dieselben Fehler mehrfach (Chip an der Ascender- statt Ink-Box, Wörter im
Emphasis-Fenster verschwunden, Zeilen zu breit). Alles, was bei jedem Video
gleich ist, gehört genau einmal in Code — video-spezifisch bleibt nur der Plan.

Design-Entscheidungen (bewusst so, nicht zufällig)
--------------------------------------------------
1. Ein Stil-Default-Block mit den vermessenen Referenzwerten (captions.md).
   Die Kunden-Config überschreibt punktuell — nie alles neu definieren müssen.
2. Frame-Dedupe über Signaturen: Bei Karaoke ändert sich nur alle ~9 Frames
   etwas (Wortwechsel). Identische Frames werden gehardlinkt statt neu gerendert
   → ~5-8× schneller bei 1080x1920, ohne Qualitätsverlust. Gemessen: 344 Frames,
   84 gerendert = 76 % gespart.
3. Layer-Caching pro Karte: Text- und Schattenebene werden einmal gezeichnet,
   nur der Chip wandert. Der Schatten ist der teuerste Schritt (Gaussian Blur).
4. Alle Invarianten als assert im Code, nicht als Prosa in der Doku.
   Ein stiller Fehlschlag hat schon ganze Feedbackrunden gekostet.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json, os, math, shutil, argparse, sys

# ---------------------------------------------------------------- Stil-Defaults
# Vermessen am abgenommenen Referenz-Schnitt (siehe references/captions.md).
# Kunden-Config überschreibt nur, was abweicht.
DEFAULTS = {
    "canvas":   {"w": 1080, "h": 1920, "fps": 30},
    "karaoke": {
        "font": "heavy",          # heavy | std  → Pfad kommt aus fonts
        "size": 64,
        "line_height": 86,
        "max_words": 3,           # max. Wörter pro Karte
        "max_chars": 26,
        "max_width": 860,         # nie fast volle Bildbreite
        "color": "#F0F0F0",       # Off-White, nie reines Weiß
        "band_y_pct": 0.66,       # 9:16 → Hormozi-Zone 62–70 %
        "lead": 0.10,             # Anzeige-Vorlauf vor Wort-Onset
        "gap_fill": 0.25,         # kleinere Lücken werden geschlossen
        "tail": 0.15,             # Nachlauf letztes Wort
        "chip": {"pad_x": 13, "pad_y": 7, "radius": 11},
        "shadow": {"radius": 7, "alpha": 0.72, "dy": 4},
        "outline": 0,             # KEINE Kontur (max. 1 px, nur wenn CI es fordert)
        "scrim": {"alpha": 0.0, "radius": 14, "pad_x": 22, "pad_y": 10},
    },
    "emphasis": {
        "size": 96, "line_height": 112,
        "pop": 0.20, "overshoot": 1.08, "exit": 0.15,
        "drift": 0.018, "glow_blur": 26, "glow_dur": 0.35,
        "shadow": {"radius": 9, "alpha": 0.78, "dy": 5},
        "margin": 0.35,           # Suchfenster für die Wort-Zuordnung
    },
    "hook": {
        "size": 74, "line_height": 96, "pop": 0.22,
        "shadow": {"radius": 9, "alpha": 0.80, "dy": 5},
        "chip": {"pad_x": 15, "pad_y": 8, "radius": 12},
    },
}


def deep_merge(base, over):
    """Config über Defaults legen — rekursiv, ohne den Rest zu verlieren."""
    out = dict(base)
    for k, v in (over or {}).items():
        out[k] = deep_merge(base[k], v) if isinstance(v, dict) and isinstance(base.get(k), dict) else v
    return out


def hex_rgb(v, fallback=(255, 255, 255)):
    if isinstance(v, (list, tuple)):
        return tuple(v[:3])
    if isinstance(v, str) and v.startswith("#") and len(v) == 7:
        return tuple(int(v[i:i + 2], 16) for i in (1, 3, 5))
    return fallback


# ---------------------------------------------------------------- Font-Handling
class Fonts:
    """Lädt Schriftschnitte einmal und cacht sie nach (Pfad, Größe)."""

    def __init__(self, cfg_fonts):
        self.paths = cfg_fonts
        self._c = {}
        missing = [k for k in ("heavy", "std") if not cfg_fonts.get(k)]
        assert not missing, f"Schriftschnitte fehlen in der Config: {missing}"
        for k, p in cfg_fonts.items():
            assert os.path.exists(p), f"Schriftdatei nicht gefunden: {k} -> {p}"

    def get(self, role, size):
        p = self.paths.get(role) or self.paths["std"]
        k = (p, size)
        if k not in self._c:
            self._c[k] = ImageFont.truetype(p, size)
        return self._c[k]


MEASURE = ImageDraw.Draw(Image.new("RGBA", (8, 8)))


def ink_band(font):
    """Ober-/Unterkante der tatsächlichen Schriftfläche ('Hg').

    NICHT die Ascender-Box verwenden: die enthält Leerraum über den Versalien,
    dadurch sitzt jeder Chip systematisch zu hoch. Einmal gemessen und für ALLE
    Wörter identisch benutzt, sonst springen die Chips beim Wortwechsel.
    """
    b = MEASURE.textbbox((0, 0), "Hg", font=font)
    return b[1], b[3]


def shadow_of(layer, radius, alpha, dy):
    a = layer.split()[-1].point(lambda v: int(v * alpha))
    sh = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    sh.putalpha(a)
    sh = sh.filter(ImageFilter.GaussianBlur(radius))
    out = Image.new("RGBA", layer.size, (0, 0, 0, 0))
    out.paste(sh, (0, dy), sh)
    return out


def ease_out_back(p, over=1.08):
    c1 = 1.70158 * over
    c3 = c1 + 1
    return 1 + c3 * pow(p - 1, 3) + c1 * pow(p - 1, 2)


# ---------------------------------------------------------------- Karten-Aufbau
def build_cards(words, st, gap_break=0.6):
    """Wörter zu Karten gruppieren.

    Bricht bei: max_words, max_chars, Satzzeichen — und bei einer Sprechpause
    größer gap_break. Ohne die Pausen-Regel landen Wörter aus zwei getrennten
    Sinneinheiten in einer Karte (z. B. vor und nach einer Emphasis), und das
    hintere Wort wird nie hervorgehoben.
    """
    cards, cur = [], []
    for w in words:
        pause = (w["s"] - cur[-1]["e"]) if cur else 0.0
        cand = cur + [w]
        txt = " ".join(x["w"] for x in cand)
        if cur and (len(cand) > st["max_words"] or len(txt) > st["max_chars"] or pause > gap_break):
            cards.append(cur)
            cur = [w]
        else:
            cur = cand
        if cur and cur[-1]["w"][-1:] in ".,?!":
            cards.append(cur)
            cur = []
    if cur:
        cards.append(cur)
    return cards


def display_times(cards, st, emph):
    """Anzeigezeiten: Vorlauf, lückenlose Zeilenwechsel, Emphasis weicht aus."""
    disp = [{"s": round(c[0]["s"] - st["lead"], 3),
             "e": round(c[-1]["e"] + st["tail"], 3),
             "words": c} for c in cards]
    for i in range(len(disp) - 1):
        gap = disp[i + 1]["s"] - disp[i]["e"]
        if gap < st["gap_fill"]:          # deckt auch Überlappungen (gap < 0) ab
            disp[i]["e"] = disp[i + 1]["s"]
    if emph:
        # Die Emphasis belegt die Textzone allein: Karten enden davor bzw.
        # starten danach — sie verschwinden aber nicht (siehe suppress_*).
        for d in disp:
            if d["s"] < emph["onset"] < d["e"]:
                d["e"] = emph["onset"]
            if d["s"] < emph["end"] < d["e"]:
                d["s"] = emph["end"]
    return [d for d in disp if d["e"] - d["s"] >= 0.02]


def norm(w):
    return w.strip(".,?!:;„“\"'").lower()


def suppress_emphasis_words(words, emph, margin):
    """Nur die Wörter unterdrücken, die die Emphasis SELBST anzeigt.

    Auf WORT-Ebene, nie auf Karten-Ebene — sonst verschwinden ganze Halbsätze
    aus den Untertiteln (real passiert, vom Kunden reklamiert).

    Wichtig: NICHT das ganze Zeitfenster leerräumen. Wörter, die zufällig im
    Fenster liegen, die Emphasis aber nicht zeigt (z. B. das Wort direkt davor
    oder während des Exit-Fades), müssen weiter in Karaoke-Karten erscheinen —
    sonst fehlen sie im fertigen Video. Genau dieser Fehler ist im Test
    aufgetreten ('immer', 'Bescheid' verschwanden).
    """
    if not emph:
        return words, [], []
    lo, hi = emph["onset"] - margin, emph["end"]
    shown = {norm(w) for line in emph["lines"] for w in line}
    keep, dropped, orphans = [], [], []
    for w in words:
        in_window = lo <= w["s"] < hi
        if in_window and norm(w["w"]) in shown:
            dropped.append(w)
        else:
            if in_window:
                orphans.append(w["w"])
            keep.append(w)
    assert dropped, ("Emphasis-Unterdrückung hat kein Wort getroffen — "
                     "Zeiten oder Emphasis-Text prüfen")
    return keep, dropped, orphans


def merge_short_cards(cards, st, min_show=0.35):
    """Karten, die zu kurz sichtbar wären, mit der vorherigen verschmelzen.

    Entsteht typischerweise am Emphasis-Rand: ein einzelnes Wort bliebe 0,2 s
    stehen und flackert. Nur verschmelzen, wenn die Karten zeitlich direkt
    aneinander liegen — sonst landen Wörter aus getrennten Sinneinheiten
    zusammen und das hintere wird nie hervorgehoben.
    """
    out = []
    for c in cards:
        dur = c[-1]["e"] - c[0]["s"]
        pause = (c[0]["s"] - out[-1][-1]["e"]) if out else 99
        if (out and dur < min_show and pause < 0.6
                and len(out[-1]) + len(c) <= st["max_words"] + 1):
            out[-1].extend(c)
        else:
            out.append(c)
    return out


# ---------------------------------------------------------------- Zeichnen
class Renderer:
    def __init__(self, cfg, plan, fonts):
        self.cv = cfg["canvas"]
        self.W, self.H, self.FPS = self.cv["w"], self.cv["h"], self.cv["fps"]
        self.k = cfg["karaoke"]
        self.e = cfg["emphasis"]
        self.h = cfg["hook"]
        self.fonts = fonts
        self.accent = hex_rgb(cfg.get("accent", "#FFFFFF"))
        self.text_rgb = hex_rgb(self.k["color"], (240, 240, 240))
        self.band_y = int(self.H * self.k["band_y_pct"])
        self.plan = plan
        self._card_cache, self._emph_cache, self._hook_cache = {}, {}, {}

    # -- Karaoke ---------------------------------------------------
    def card_layers(self, idx, d):
        if idx in self._card_cache:
            return self._card_cache[idx]
        st = self.k
        f = self.fonts.get(st["font"], st["size"])
        sp = MEASURE.textlength(" ", font=f)
        top, bot = ink_band(f)

        lines, cur = [[]], None
        for it in d["words"]:
            w = MEASURE.textlength(it["w"], font=f)
            cur = lines[-1]
            cw = sum(x[1] for x in cur) + sp * max(0, len(cur) - 1)
            if cur and cw + sp + w > st["max_width"]:
                lines.append([])
                cur = lines[-1]
            cur.append((it, w))

        total = len(lines) * st["line_height"]
        y0 = self.band_y - total / 2
        txt = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        dt = ImageDraw.Draw(txt)
        boxes, y = {}, y0
        line_boxes = []
        for ln in lines:
            tw = sum(x[1] for x in ln) + sp * max(0, len(ln) - 1)
            x = (self.W - tw) / 2
            line_boxes.append((x, y + top, x + tw, y + bot))
            for it, w in ln:
                dt.text((x, y), it["w"], font=f, fill=self.text_rgb)
                boxes[id(it)] = (x - st["chip"]["pad_x"], y + top - st["chip"]["pad_y"],
                                 x + w + st["chip"]["pad_x"], y + bot + st["chip"]["pad_y"])
                x += w + sp
            y += st["line_height"]

        # Scrim: dunkle Fläche hinter der GESAMTEN Zeile (Kontrast-Gate)
        scrim = None
        if st["scrim"]["alpha"] > 0:
            sc = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            ds = ImageDraw.Draw(sc)
            a = int(255 * st["scrim"]["alpha"])
            for (x0, y0_, x1, y1) in line_boxes:
                ds.rounded_rectangle(
                    [x0 - st["scrim"]["pad_x"], y0_ - st["scrim"]["pad_y"],
                     x1 + st["scrim"]["pad_x"], y1 + st["scrim"]["pad_y"]],
                    radius=st["scrim"]["radius"], fill=(0, 0, 0, a))
            scrim = sc

        sh = shadow_of(txt, **st["shadow"])
        items = {id(it): it for it in d["words"]}
        self._card_cache[idx] = (txt, sh, scrim, boxes, items)
        return self._card_cache[idx]

    def active_word(self, idx, d, t):
        _, _, _, _, items = self.card_layers(idx, d)
        act = None
        for k, it in items.items():
            if it["s"] - self.k["lead"] <= t < it["e"]:
                act = k
        return act

    def draw_card(self, img, idx, d, t):
        txt, sh, scrim, boxes, _ = self.card_layers(idx, d)
        if scrim is not None:
            img.alpha_composite(scrim)
        img.alpha_composite(sh)
        act = self.active_word(idx, d, t)
        if act is not None:
            chip = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            ImageDraw.Draw(chip).rounded_rectangle(
                boxes[act], radius=self.k["chip"]["radius"], fill=self.accent + (255,))
            img.alpha_composite(chip)
        img.alpha_composite(txt)

    # -- Emphasis --------------------------------------------------
    def emph_base(self, emph):
        if "b" in self._emph_cache:
            return self._emph_cache["b"]
        st = self.e
        f = self.fonts.get("heavy", st["size"])
        sp = MEASURE.textlength(" ", font=f)
        lay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        glow = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        dl, dg = ImageDraw.Draw(lay), ImageDraw.Draw(glow)
        total = len(emph["lines"]) * st["line_height"]
        y = self.band_y - total / 2
        for ln in emph["lines"]:
            tw = sum(MEASURE.textlength(w, font=f) for w in ln) + sp * (len(ln) - 1)
            x = (self.W - tw) / 2
            for w in ln:
                if w == emph.get("keyword"):
                    dg.text((x, y), w, font=f, fill=self.accent + (255,))
                dl.text((x, y), w, font=f, fill=self.text_rgb)
                x += MEASURE.textlength(w, font=f) + sp
            y += st["line_height"]
        glow = glow.filter(ImageFilter.GaussianBlur(st["glow_blur"]))
        sh = shadow_of(lay, **st["shadow"])
        self._emph_cache["b"] = (lay, sh, glow)
        return self._emph_cache["b"]

    def draw_emph(self, img, emph, t, fi):
        lay, sh, glow = self.emph_base(emph)
        st = self.e
        dt = t - emph["onset"]
        if dt < st["pop"]:
            sc = 0.62 + 0.38 * ease_out_back(dt / st["pop"], st["overshoot"])
        elif t < emph["hold_end"]:
            hp = (t - st["pop"] - emph["onset"]) / max(0.01, emph["hold_end"] - emph["onset"] - st["pop"])
            sc = 1.0 + st["drift"] * min(1.0, hp)
        else:
            sc = 1.0 + st["drift"]
        alpha, dy = 1.0, 0
        if t >= emph["hold_end"]:
            p = min(1.0, (t - emph["hold_end"]) / st["exit"])
            alpha, dy = 1.0 - p, int(90 * p * p)
        gp = max(0.0, min(1.0, (t - emph["onset"] - st["pop"]) / st["glow_dur"]))
        ga = math.sin(gp * math.pi) * 0.85 if gp > 0 else 0.0

        comp = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        if ga > 0.01:
            g = glow.copy()
            g.putalpha(g.split()[-1].point(lambda v: int(v * ga)))
            comp.alpha_composite(g)
        comp.alpha_composite(sh)
        comp.alpha_composite(lay)
        if 0 <= dt < 2.0 / self.FPS:
            comp = comp.filter(ImageFilter.GaussianBlur(5))       # Motion-Blur
        jit = 0
        if st["pop"] <= dt < st["pop"] + 2.0 / self.FPS:
            jit = 3 if fi % 2 else -3                            # Land-Jitter
        if abs(sc - 1.0) > 0.003 or dy or jit:
            nw, nh = max(1, int(self.W * sc)), max(1, int(self.H * sc))
            r = comp.resize((nw, nh), Image.LANCZOS)
            base = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            base.alpha_composite(r, (int((self.W - nw) / 2) + jit,
                                     int((self.H - nh) / 2 - (self.band_y - self.H / 2) * (sc - 1)) + dy))
            comp = base
        if alpha < 1.0:
            comp.putalpha(comp.split()[-1].point(lambda v: int(v * alpha)))
        img.alpha_composite(comp)

    # -- Hook ------------------------------------------------------
    def hook_layer(self, hook):
        if "h" in self._hook_cache:
            return self._hook_cache["h"]
        st = self.h
        f = self.fonts.get("heavy", st["size"])
        sp = MEASURE.textlength(" ", font=f)
        top, bot = ink_band(f)
        lay = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        chip = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        dl, dc = ImageDraw.Draw(lay), ImageDraw.Draw(chip)
        y = hook["y"]
        for ln in hook["lines"]:
            tw = sum(MEASURE.textlength(w, font=f) for w in ln) + sp * (len(ln) - 1)
            x = (self.W - tw) / 2
            for w in ln:
                ww = MEASURE.textlength(w, font=f)
                if w == hook.get("keyword"):
                    dc.rounded_rectangle([x - st["chip"]["pad_x"], y + top - st["chip"]["pad_y"],
                                          x + ww + st["chip"]["pad_x"], y + bot + st["chip"]["pad_y"]],
                                         radius=st["chip"]["radius"], fill=self.accent + (255,))
                dl.text((x, y), w, font=f, fill=self.text_rgb)
                x += ww + sp
            y += st["line_height"]
        sh = shadow_of(lay, **st["shadow"])
        self._hook_cache["h"] = (lay, sh, chip)
        return self._hook_cache["h"]

    def draw_hook(self, img, hook, t):
        if t < hook.get("in", 0.18):
            return
        lay, sh, chip = self.hook_layer(hook)
        p = min(1.0, (t - hook.get("in", 0.18)) / self.h["pop"])
        sc = 0.80 + 0.20 * ease_out_back(p)
        comp = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
        comp.alpha_composite(sh)
        comp.alpha_composite(chip)
        comp.alpha_composite(lay)
        if abs(sc - 1.0) > 0.003:
            nw, nh = int(self.W * sc), int(self.H * sc)
            r = comp.resize((nw, nh), Image.LANCZOS)
            base = Image.new("RGBA", (self.W, self.H), (0, 0, 0, 0))
            base.alpha_composite(r, (int((self.W - nw) / 2),
                                     int((self.H - nh) / 2 - (hook["y"] + 100 - self.H / 2) * (sc - 1))))
            comp = base
        img.alpha_composite(comp)


# ---------------------------------------------------------------- Hauptlauf
def main():
    ap = argparse.ArgumentParser(description="Overlay-Assets für ein Video bauen")
    ap.add_argument("--config", required=True, help="kunden-config.yaml")
    ap.add_argument("--plan", required=True, help="cut-plan.json dieses Videos")
    ap.add_argument("--out", required=True, help="Zielordner")
    args = ap.parse_args()

    try:
        import yaml
        cfg_raw = yaml.safe_load(open(args.config, encoding="utf-8"))
    except ImportError:
        print("PyYAML fehlt: pip install pyyaml --break-system-packages", file=sys.stderr)
        raise

    plan = json.load(open(args.plan, encoding="utf-8"))

    # Config zusammensetzen: Defaults ← Kunden-Stil ← Plan-Overrides (dieses Video)
    style = deep_merge(DEFAULTS, (cfg_raw.get("stil") or {}))
    style = deep_merge(style, (plan.get("style") or {}))
    style["accent"] = (plan.get("accent")
                       or (cfg_raw.get("ci", {}).get("farben", {}) or {}).get("akzent")
                       or "#FFFFFF")
    fonts = Fonts(plan.get("fonts") or cfg_raw.get("fonts") or {})

    W, H, FPS = style["canvas"]["w"], style["canvas"]["h"], style["canvas"]["fps"]
    end = float(plan["timeline"]["end"])
    emph = plan.get("emphasis")
    hook = plan.get("hook")
    words = plan["words"]                     # [{w, s, e}, ...] bereits segmentkorrigiert
    assert words, "Der Plan enthält keine Wörter"

    kept, dropped, orphans = suppress_emphasis_words(words, emph, style["emphasis"]["margin"])
    cards = merge_short_cards(build_cards(kept, style["karaoke"]), style["karaoke"])
    disp = display_times(cards, style["karaoke"], emph)

    # Invariante: kein Wort geht verloren (Vollständigkeits-Gate, Teil 1)
    in_cards = {id(w) for d in disp for w in d["words"]}
    lost = [w for w in kept if id(w) not in in_cards]
    assert not lost, f"{len(lost)} Wörter sind aus den Karten gefallen: {[w['w'] for w in lost][:5]}"
    if orphans:
        print(f"   Hinweis: {len(orphans)} Wort(e) liegen im Emphasis-Umfeld, werden aber "
              f"weiter als Karaoke gezeigt: {orphans[:5]}")

    r = Renderer(style, plan, fonts)
    ovl = os.path.join(args.out, "ovl")
    shutil.rmtree(ovl, ignore_errors=True)
    os.makedirs(ovl, exist_ok=True)

    n = int(round(end * FPS))
    hook_until = float(hook["until"]) if hook else 0.0
    rendered = linked = empty = 0
    prev_sig, prev_path = None, None

    for i in range(n):
        t = i / FPS
        path = os.path.join(ovl, f"f{i:05d}.png")

        # Signatur: was ist in diesem Frame zu sehen? Gleiche Signatur = gleiches Bild.
        if hook and t < hook_until:
            sig = ("hook", "static") if t >= hook.get("in", 0.18) + r.h["pop"] else ("hook", i)
        elif emph and emph["onset"] <= t < emph["end"]:
            sig = ("emph", i)                       # animiert → jeder Frame eigen
        else:
            hit = next(((idx, d) for idx, d in enumerate(disp) if d["s"] <= t < d["e"]), None)
            sig = ("card", hit[0], r.active_word(hit[0], hit[1], t)) if hit else ("empty",)

        if sig == prev_sig and prev_path:
            try:
                os.link(prev_path, path)
            except OSError:
                shutil.copyfile(prev_path, path)
            linked += 1
            continue

        img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if sig[0] == "hook":
            r.draw_hook(img, hook, t)
        elif sig[0] == "emph":
            r.draw_emph(img, emph, t, i)
        elif sig[0] == "card":
            hit = next((idx, d) for idx, d in enumerate(disp) if d["s"] <= t < d["e"])
            r.draw_card(img, hit[0], hit[1], t)
        else:
            empty += 1
        img.save(path, compress_level=1)
        rendered += 1
        prev_sig, prev_path = sig, path

    # ---- SFX-Events: immer aus den Definitionen ableiten, nie hartkodieren
    events = {"pop": [], "whoosh": [], "boom": []}
    if emph:
        events["pop"].append(round(emph["onset"] + 0.04, 3))
    for c in plan.get("cuts", []):
        events["whoosh"].append(round(float(c), 3))
    for b in plan.get("boom", []):
        events["boom"].append(round(float(b), 3))

    report = {
        "frames": n, "rendered": rendered, "linked": linked, "empty_frames": empty,
        "cards": [{"s": d["s"], "e": d["e"], "txt": " ".join(x["w"] for x in d["words"])} for d in disp],
        "emphasis": emph, "hook": hook,
        "words_total": len(words), "words_in_cards": len(kept), "words_in_emphasis": len(dropped),
        "style_used": {"karaoke": style["karaoke"], "accent": style["accent"]},
        "band_y": r.band_y, "canvas": style["canvas"],
    }
    json.dump(events, open(os.path.join(args.out, "events.json"), "w"), indent=1)
    json.dump(report, open(os.path.join(args.out, "build-report.json"), "w"),
              ensure_ascii=False, indent=1)

    saved = 100 * linked / n if n else 0
    print(f"OK · {n} Frames ({rendered} gerendert, {linked} dedupliziert = {saved:.0f}% gespart)")
    print(f"   {len(disp)} Karten · Emphasis: {'ja' if emph else 'nein'} · Hook: {'ja' if hook else 'nein'}")
    print(f"   Wörter: {len(words)} gesamt / {len(kept)} Karaoke / {len(dropped)} Emphasis")


if __name__ == "__main__":
    main()
