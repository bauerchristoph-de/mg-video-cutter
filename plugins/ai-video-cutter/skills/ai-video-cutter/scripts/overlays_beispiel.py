"""BEISPIEL-IMPLEMENTIERUNG (references/konversionsvideo-overlays.md). Texte/Preise/Zeilen der Ticket-Karte sind Kundenwerte und gehoeren in die kunden-config, nicht ins Plugin.
Overlays fuer Danke-Videos: Reel-Hooks (dunkle Box, Versalien, Akzentwort orange) + Wert-/Ticket-Karte.
Alles wird vorab zu RGBA-Arrays gerendert; blend_*() mischt pro Ausgabeframe."""
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFont

# Fontpfad per Umgebungsvariable (Montserrat woff/ttf mit %d fuer das Gewicht)
FD = os.environ.get('OVL_FONT', '/tmp/fnt/node_modules/@fontsource/montserrat/files/montserrat-latin-%d-normal.woff')
ORANGE = (255, 97, 0, 255); WHITE = (255, 255, 255, 255); MUTED = (255, 255, 255, 170)
W_, H_ = 1280, 720
_f = {}
def font(wt, size):
    k = (wt, size)
    if k not in _f: _f[k] = ImageFont.truetype(FD % wt, size)
    return _f[k]
_dd = ImageDraw.Draw(Image.new('L', (4, 4)))
def tw(t, wt, size): return _dd.textlength(t, font=font(wt, size))


def mmss(sec):
    sec = int(sec)
    return '%d:%02d' % (sec // 60, sec % 60)


# ---------------- Hook ----------------
def make_hook(lines, maxw=760, bottom=586, minpad=30, pad_t=14, pad_b=24, line_h=1.28, fixw=None):
    """lines: [[(text, weight, size, color), ...], ...] -> dict(x,y,rgb,al). fixw: feste Mindestbreite (kein Springen beim Countdown)."""
    widths = [sum(tw(t, wt, sz) for t, wt, sz, c in L) for L in lines]
    bw = int(max(widths) + 2 * minpad)
    if fixw: bw = max(bw, fixw)
    assert bw <= maxw, ('Hook zu breit', bw, lines)
    lh = [int(max(sz for t, wt, sz, c in L) * line_h) for L in lines]
    bh = pad_t + sum(lh) + pad_b
    im = Image.new('RGBA', (bw, bh), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.rounded_rectangle((0, 0, bw - 1, bh - 1), 22, fill=(13, 15, 22, 228))
    y = pad_t
    for L, h, wd in zip(lines, lh, widths):
        x = (bw - wd) / 2
        for t, wt, sz, c in L:
            d.text((x, y + h / 2), t, font=font(wt, sz), fill=c, anchor='lm'); x += tw(t, wt, sz)
        y += h
    d.rounded_rectangle((bw / 2 - 26, bh - 13, bw / 2 + 26, bh - 10), 2, fill=ORANGE)
    a = np.array(im)
    return dict(x=(W_ - bw) // 2, y=bottom - bh, rgb=a[:, :, :3].astype(np.float32), al=a[:, :, 3:4].astype(np.float32) / 255.0)


def _cd_txt(n):
    m, sec = divmod(int(n), 60)
    return ('%d MINUTE %02d' % (m, sec)) if m == 1 else (('%d MINUTEN %02d' % (m, sec)) if m > 1 else ('%d SEKUNDEN' % sec))


def hook1_seq(n0, steps, sub='Kleiner Kontext-Satz'):
    """Zaehlt pro Schritt 1 Sekunde runter: ERFAHRE IN 1 MINUTE 45 -> ...44 ... (grosse Zeile oben, kleine darunter)."""
    def L(n):
        return [[('ERFAHRE IN ', 800, 44, WHITE), (_cd_txt(n), 800, 44, ORANGE)],
                [(sub, 500, 15, (255, 255, 255, 220))]]
    fw = max(int(sum(tw(t, wt, sz) for t, wt, sz, c in L(n0 - k)[0])) for k in range(steps)) + 2 * 28
    return [make_hook(L(n0 - k), line_h=1.22, minpad=28, fixw=fw) for k in range(steps)]


def teaser():
    return make_hook([
        [('ACHTUNG', 600, 15, ORANGE)],
        [('DAS BESTE KOMMT GLEICH', 800, 34, WHITE)],
    ], line_h=1.22)


def countdown_hooks():
    """Rehook: nur Satzanfang + Zahl, nichts vom Angebot verraten."""
    out = []
    for n in range(10, 0, -1):
        out.append(make_hook([
            [('DAS BESTE KOMMT IN', 600, 18, WHITE)],
            [(str(n), 800, 50, ORANGE)],
        ], line_h=1.15, minpad=40, fixw=250))
    return out


def blend_hook(fr, hk, f, f0, f1, fin=6, fout=8):
    if f < f0 or f >= f1: return
    a_ = min(1.0, (f - f0 + 1) / fin, (f1 - f) / fout)
    if a_ <= 0: return
    y, x = hk['y'], hk['x']; h, w = hk['al'].shape[:2]
    reg = fr[y:y + h, x:x + w].astype(np.float32)
    al = hk['al'] * a_
    fr[y:y + h, x:x + w] = (reg * (1 - al) + hk['rgb'][:, :, ::-1] * al).astype(np.uint8)


# ---------------- Wert-/Ticket-Karte (Beispielwerte, kundenspezifisch!) ----------------
CW = 322
ROWS = [('Bonus A', '97 €', None), ('Bonus B', '119 €', None),
        ('Bonus C', '197 €', 'mit persönlicher Betreuung'), ('Gutschein', '500 €', None)]
TITLE = 'ANGEBOT'; TOTAL = ('Gesamtwert', '913 €'); NORMAL = ('Normalpreis', '97 €'); PRICE = ('DEIN PREIS HEUTE', '29,90 €')


def _check(d, x, y, s=20):
    pts = [(x + s * 5 / 24, y + s * 12.5 / 24), (x + s * 9.5 / 24, y + s * 17 / 24), (x + s * 19 / 24, y + s * 7.5 / 24)]
    d.line(pts, fill=ORANGE, width=3, joint='curve')


def ticket_state(n_rows, show_total, show_normal, show_price):
    HMAX = 470
    im = Image.new('RGBA', (CW, HMAX), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    rh = [(58 if ROWS[k][2] else 40) for k in range(n_rows)]
    h = 56 + sum(rh) + (44 if show_total else 0) + (38 if show_normal else 0) + (100 if show_price else 0) + 14
    d.rounded_rectangle((0, 0, CW - 1, h), 18, fill=(5, 7, 15, 238), outline=(255, 255, 255, 46), width=1)
    d.rounded_rectangle((18, 0, CW - 19, 3), 2, fill=ORANGE)
    d.text((CW / 2, 30), TITLE, font=font(700, 16), fill=ORANGE, anchor='mm')
    y = 56
    for k in range(n_rows):
        lab, val, sub = ROWS[k]
        mid = y + 20
        _check(d, 18, mid - 11)
        d.text((46, mid), lab, font=font(600, 16), fill=WHITE, anchor='lm')
        d.text((CW - 18, mid), val, font=font(700, 16), fill=MUTED, anchor='rm')
        if sub: d.text((46, mid + 20), sub, font=font(700, 13), fill=ORANGE, anchor='lm')
        y += rh[k]
    def struck(y, label, v, vsize):
        d.text((18, y + 22), label, font=font(600, 15), fill=MUTED, anchor='lm')
        vw = tw(v, 800, vsize)
        d.text((CW - 18, y + 22), v, font=font(800, vsize), fill=WHITE, anchor='rm')
        d.line((CW - 18 - vw - 3, y + 22, CW - 15, y + 22), fill=ORANGE, width=3)
    if show_total:
        d.line((18, y + 4, CW - 18, y + 4), fill=(255, 255, 255, 40), width=1)
        struck(y + 4, *TOTAL, 20); y += 44
    if show_normal:
        struck(y, *NORMAL, 20); y += 38
    if show_price:
        d.text((CW / 2, y + 20), PRICE[0], font=font(600, 14), fill=MUTED, anchor='mm')
        d.text((CW / 2, y + 60), PRICE[1], font=font(800, 50), fill=WHITE, anchor='mm')
        d.rounded_rectangle((CW / 2 - 33, y + 90, CW / 2 + 33, y + 94), 2, fill=ORANGE)
    a = np.array(im).astype(np.float32)
    al = a[:, :, 3:4] / 255.0
    return a[:, :, :3] * al, al          # vormultipliziert


def build_ticket():
    """Zustaende: 1..4 Zeilen, +Gesamtwert (durchgestrichen), +Normalpreis (durchgestrichen), +Preis."""
    return [ticket_state(1, False, False, False), ticket_state(2, False, False, False), ticket_state(3, False, False, False),
            ticket_state(4, False, False, False), ticket_state(4, True, False, False), ticket_state(4, True, True, False),
            ticket_state(4, True, True, True)]


def blend_ticket(fr, states, times, f, f_end, x0=948, y0=28, fade=8):
    if f < times[0] or f >= f_end: return
    k = 0
    for i, t in enumerate(times):
        if f >= t: k = i
    P, A = states[k]
    if k > 0 and f - times[k] < fade:
        u = (f - times[k] + 1) / fade
        P0, A0 = states[k - 1]
        P = P0 * (1 - u) + P * u; A = A0 * (1 - u) + A * u
    m = 1.0
    if f - times[0] < fade: m = (f - times[0] + 1) / fade
    if f_end - f <= fade: m = min(m, (f_end - f) / fade)
    h, w = A.shape[:2]
    reg = fr[y0:y0 + h, x0:x0 + w].astype(np.float32)
    A = A * m; P = P * m
    fr[y0:y0 + h, x0:x0 + w] = (reg * (1 - A) + P[:, :, ::-1]).astype(np.uint8)
