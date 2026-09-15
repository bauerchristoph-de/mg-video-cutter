#!/usr/bin/env python3
"""Overlays für Clip-Montagen (references/clip-montage.md): weißer Text, Glow + Schatten, kein Kasten.

  montage_build.py --config kunden-config.yaml --plan montage-plan.json [--out ov/]

Erzeugt ov/titel/fNN.png (Titel, zwei Zeilen, ein Akzentwort in der Akzentfarbe der Kunden-Config)
und ov/<slide-id>/fNN.png (Bauchbinde „Name – HH:MM Uhr" + optionaler Kommentar), je 3 Frames Pop-in.
Fonts: plan.fonts {titel,name,kommentar} (Pfade) — fehlt der Eintrag, wird aus ci.fonts.dateien der
Config nach Schnitt gewählt (ExtraBold/Black → Titel, SemiBold/Bold → Name, Medium/Regular → Kommentar).
Alle Werte sind Freigaben aus einem realen Kundenprojekt (neun Runden); Abweichungen gehören in die
Kunden-Config oder kunden-learnings.md, nicht in eine Einzelfall-Änderung hier.
"""
import argparse, json, os, sys
from PIL import Image, ImageDraw, ImageFont, ImageFilter
W, H = 1080, 1920; POP = [0.94, 0.98, 1.0]

def hex_rgb(v, fb):
    v = (v or '').strip().lstrip('#')
    return tuple(int(v[i:i + 2], 16) for i in (0, 2, 4)) if len(v) == 6 else fb

def font_auswahl(plan_fonts, cfg_dateien):
    rollen = {'titel': ('extrabold', 'black', 'heavy', 'bold'), 'name': ('semibold', 'bold'), 'kommentar': ('medium', 'regular', 'book')}
    out = {}
    for rolle, keys in rollen.items():
        if plan_fonts.get(rolle): out[rolle] = plan_fonts[rolle]; continue
        for k in keys:
            hit = [d for d in cfg_dateien if k in os.path.basename(d).lower()]
            if hit: out[rolle] = hit[0]; break
        if rolle not in out: sys.exit(f'Font für Rolle "{rolle}" fehlt: plan.fonts.{rolle} setzen oder ci.fonts.dateien in der Config pflegen (kein Raten).')
    return out

def mit_glow(canvas, glow_alpha=110, glow_radius=22, shadow_alpha=170):
    a = canvas.split()[3]
    glow = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    glow.putalpha(a.filter(ImageFilter.MaxFilter(9)).filter(ImageFilter.GaussianBlur(glow_radius)).point(lambda v: int(v * glow_alpha / 255)))
    sh = Image.new('RGBA', canvas.size, (0, 0, 0, 0))
    sh.putalpha(a.filter(ImageFilter.GaussianBlur(5)).point(lambda v: int(v * shadow_alpha / 255)))
    out = Image.new('RGBA', canvas.size, (0, 0, 0, 0)); out.alpha_composite(glow); out.alpha_composite(sh, (2, 4)); out.alpha_composite(canvas)
    return out

def sequenz(ordner, bild, cy):
    os.makedirs(ordner, exist_ok=True)
    for i, s in enumerate(POP):
        fr = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        b = bild.resize((max(1, int(bild.width * s)), max(1, int(bild.height * s))), Image.LANCZOS)
        fr.alpha_composite(b, (W // 2 - b.width // 2, cy - b.height // 2)); fr.save(f'{ordner}/f{i:02d}.png')

def titel(t, fonts, farbe_text, farbe_akzent, out):
    f = ImageFont.truetype(fonts['titel'], t.get('groesse', 52)); gap = 8; akzent = t.get('akzent')
    d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10)))
    canvas = Image.new('RGBA', (W, 120 + len(t['zeilen']) * (f.size + gap)), (0, 0, 0, 0)); d = ImageDraw.Draw(canvas); y = 60
    for zeile in t['zeilen']:
        if akzent and akzent in zeile:
            vor, nach = zeile.split(akzent, 1); teile = [(vor, farbe_text), (akzent, farbe_akzent), (nach, farbe_text)]
        else: teile = [(zeile, farbe_text)]
        x = (W - sum(d0.textlength(s, font=f) for s, _ in teile)) / 2
        for s, c in teile:
            if s: d.text((x, y), s, font=f, fill=c + (255,), anchor='la'); x += d0.textlength(s, font=f)
        y += f.size + gap
    b = mit_glow(canvas, glow_alpha=150, glow_radius=26, shadow_alpha=190); b = b.crop(b.getbbox())
    sequenz(os.path.join(out, 'titel'), b, t.get('y', 1130))

def bauchbinde(s, bb, fonts, farbe_text, out):
    groesse = bb.get('groesse', 54); f2 = ImageFont.truetype(fonts['kommentar'], bb.get('kommentar_groesse', 34))
    d0 = ImageDraw.Draw(Image.new('RGBA', (10, 10))); zeile = f"{s['name']} – {s['zeit']} Uhr" if s.get('zeit') else s['name']
    while True:
        f1 = ImageFont.truetype(fonts['name'], groesse)
        if d0.textlength(zeile, font=f1) <= bb.get('max_breite', 940) or groesse <= 40: break
        groesse -= 2
    canvas = Image.new('RGBA', (W, 320), (0, 0, 0, 0)); d = ImageDraw.Draw(canvas)
    d.text((W // 2, 60), zeile, font=f1, fill=farbe_text + (255,), anchor='ma')
    if s.get('kommentar'): d.text((W // 2, 60 + groesse + 14), s['kommentar'], font=f2, fill=farbe_text + (255,), anchor='ma')
    b = mit_glow(canvas); b = b.crop(b.getbbox()); sequenz(os.path.join(out, s['id']), b, bb.get('y', 1290))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--config', required=True); ap.add_argument('--plan', required=True); ap.add_argument('--out', default='ov')
    a = ap.parse_args()
    try:
        import yaml; cfg = yaml.safe_load(open(a.config, encoding='utf-8')) or {}
    except ImportError: sys.exit('PyYAML fehlt: pip install pyyaml --break-system-packages')
    plan = json.load(open(a.plan, encoding='utf-8')); ci = cfg.get('ci', {}) or {}
    farbe_text = hex_rgb((ci.get('farben') or {}).get('text'), (255, 255, 255))
    farbe_akzent = hex_rgb((ci.get('farben') or {}).get('akzent'), None)
    if farbe_akzent is None and plan.get('titel', {}).get('akzent'): sys.exit('ci.farben.akzent fehlt in der Kunden-Config — Setup-Interview nachholen, nicht raten.')
    fonts = font_auswahl(plan.get('fonts') or {}, (ci.get('fonts') or {}).get('dateien') or [])
    if plan.get('titel'): titel(plan['titel'], fonts, farbe_text, farbe_akzent or farbe_text, a.out)
    for s in plan['slides']: bauchbinde(s, plan.get('bauchbinde', {}), fonts, farbe_text, a.out)
    print(f'Overlays ok: {a.out}/titel + {len(plan["slides"])} Bauchbinden')

if __name__ == '__main__': main()
