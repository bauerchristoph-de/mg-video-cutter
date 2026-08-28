# -*- coding: utf-8 -*-
"""
AI Video-Cutter · make_sfx.py — SFX-Spur aus events.json.

Erzeugt EINE timeline-lange Mono-WAV mit synthetisierten Effekten:
  pop    90 ms  Sinus-Pitch-Drop 500→130 Hz   · auf jedes Emphasis-Landing
  boom   420 ms Sinus 120→48 Hz               · nur auf den größten Zahlen-Moment
  whoosh 340 ms Bandpass-Rauschen mit Hüllkurve · auf Snap-Transitions

Warum synthetisiert statt Sample-Bibliothek: lizenzfrei, reproduzierbar, und die
Peak-Lage ist exakt bekannt. Bei gelieferten Kunden-Sounds ist genau das das
Problem — eine 1,09-s-Datei kann nach 0,22 s stumm sein, dann liegt der hörbare
Peak fast eine Sekunde zu früh (real passiert). Deshalb: --check misst nach dem
Bau die tatsächlichen Peaks und vergleicht sie mit den Soll-Zeiten.

Aufruf
------
  python3 make_sfx.py --events build/events.json --duration 35.3 --out build/sfx.wav [--check]
"""
import json, math, struct, wave, argparse, os

SR = 48000
PEAK = 0.25          # ≈ −12 dB, wird später ~18 dB unter Sprache gemischt


def env(n, attack=0.005, release=None):
    """Hüllkurve: kurzer Anstieg, exponentieller Abfall — kein Klick."""
    a = max(1, int(SR * attack))
    out = []
    for i in range(n):
        if i < a:
            out.append(i / a)
        else:
            p = (i - a) / max(1, n - a)
            out.append(math.exp(-4.0 * p))
    return out


def sine_sweep(dur, f0, f1, amp=1.0):
    n = int(SR * dur)
    e = env(n)
    buf, phase = [], 0.0
    for i in range(n):
        p = i / max(1, n - 1)
        f = f0 * pow(f1 / f0, p)               # exponentiell klingt natürlicher
        phase += 2 * math.pi * f / SR
        buf.append(math.sin(phase) * e[i] * amp)
    return buf


def noise_sweep(dur, amp=1.0, seed=7, peak_at=0.86):
    """Rausch-Sweep, der auf seinen Peak ZULÄUFT (Whoosh vor einem Schnitt).

    Die Hüllkurve steigt bis peak_at der Dauer an und fällt dann steil ab —
    ein Whoosh mit Peak am Anfang klingt, als käme der Schnitt zu früh.
    """
    n = int(SR * dur)
    ip = max(1, int(n * peak_at))
    buf, lp, hp_prev, rnd = [], 0.0, 0.0, seed
    for i in range(n):
        rnd = (1103515245 * rnd + 12345) % (1 << 31)
        white = (rnd / (1 << 30)) - 1.0
        p = i / max(1, n - 1)
        cut = 400 + 5200 * math.sin(math.pi * p)      # Mitte am hellsten
        a = min(0.99, 2 * math.pi * cut / SR)
        lp += a * (white - lp)
        hp = lp - hp_prev
        hp_prev = lp
        e = (i / ip) ** 1.6 if i <= ip else max(0.0, 1.0 - (i - ip) / max(1, n - ip)) ** 1.2
        buf.append(hp * e * amp)
    return buf, ip / SR


def render(events, duration):
    track = [0.0] * int(SR * duration + SR)
    # Jedes Rezept liefert (samples, peak_offset) — der Start wird daraus
    # abgeleitet, nie geschätzt. So landet der hörbare Peak exakt auf dem Event.
    recipe = {
        "pop":    lambda: (sine_sweep(0.09, 500, 130, 0.9), 0.004),
        "boom":   lambda: (sine_sweep(0.42, 120, 48, 1.0), 0.006),
        "whoosh": lambda: noise_sweep(0.34, 0.8),
    }
    placed = []
    for kind, times in events.items():
        key = kind.split("_")[0]
        if key not in recipe:
            continue
        for t in times:
            s, peak_off = recipe[key]()
            start = t - peak_off
            i0 = int(SR * max(0.0, start))
            for j, v in enumerate(s):
                if i0 + j < len(track):
                    track[i0 + j] += v
            placed.append({"kind": key, "target": round(t, 3), "start": round(start, 3)})
    mx = max((abs(v) for v in track), default=0.0)
    if mx > 0:
        g = PEAK / mx
        track = [v * g for v in track]
    return track, placed


def write_wav(path, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1, min(1, v)) * 32767)) for v in samples))


def check_peaks(samples, placed, tol=0.04):
    """Gemessene Peak-Lage gegen Soll — nie nach Gehör, immer messen."""
    print("\nPeak-Abgleich:")
    ok = True
    for p in placed:
        c = int(SR * p["target"])
        w = int(SR * 0.25)
        lo, hi = max(0, c - w), min(len(samples), c + w)
        if lo >= hi:
            continue
        seg = samples[lo:hi]
        pk = max(range(len(seg)), key=lambda i: abs(seg[i]))
        actual = (lo + pk) / SR
        d = actual - p["target"]
        good = abs(d) <= tol
        ok &= good
        print(f"  [{'OK ' if good else 'ABW'}] {p['kind']:6s} Soll {p['target']:7.3f}s · "
              f"gemessen {actual:7.3f}s · Δ {d*1000:+6.0f} ms")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--events", required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()

    events = json.load(open(a.events, encoding="utf-8"))
    track, placed = render(events, a.duration)
    write_wav(a.out, track)
    n = len(placed)
    print(f"OK · {n} Effekt(e) · {a.duration:.2f}s · {os.path.basename(a.out)}")
    for p in placed:
        print(f"   {p['kind']:6s} @ {p['target']:.3f}s (Start {p['start']:.3f}s)")
    if a.check and n:
        if not check_peaks(track, placed):
            raise SystemExit("Peak-Abweichung über Toleranz — Events prüfen")


if __name__ == "__main__":
    main()
