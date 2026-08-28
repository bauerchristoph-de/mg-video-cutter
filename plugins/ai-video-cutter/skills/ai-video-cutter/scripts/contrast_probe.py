# -*- coding: utf-8 -*-
"""
AI Video-Cutter · contrast_probe.py — Kontrast-Gate VOR dem Rendern.

Misst im Quellvideo die Helligkeit genau dort, wo die Untertitel liegen werden,
und entscheidet daraus, ob ein Scrim (dunkle Fläche hinter der Zeile) nötig ist.

Warum
-----
Der häufigste Totalschaden ist ein Video, das jedes Timing-QC besteht und
trotzdem unlesbar ist: helle Schrift auf weißem Hemd. Nach dem Rendern fällt
das erst dem Kunden auf. Diese Messung dauert Sekunden und verhindert es.

Aufruf
------
  python3 contrast_probe.py --video cut.mp4 --plan cut-plan.json \\
      [--band-y-pct 0.66] [--apply]

Ohne --apply wird nur berichtet. Mit --apply wird die Empfehlung in den Plan
geschrieben (style.karaoke.scrim.alpha) — eine Quelle, kein zweiter Datenstand.

Entscheidung
------------
  YAVG > 140  → heller Hintergrund → Scrim Pflicht (Alpha 0,45)
  YAVG > 120  → grenzwertig        → Scrim empfohlen (Alpha 0,35)
  sonst       → Schatten reicht
Die Entscheidung gilt fürs GANZE Video (Konstanz schlägt Optimierung pro Karte).
"""
import json, subprocess, argparse, re, os, sys

THRESH_HARD, THRESH_SOFT = 140.0, 120.0
ALPHA_HARD, ALPHA_SOFT = 0.45, 0.35


def probe_luma(video, t, y0, y1, w):
    """Mittlere Luminanz im Textstreifen zum Zeitpunkt t (0-255)."""
    h = max(2, int(y1 - y0))
    cmd = ["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", video, "-frames:v", "1",
           "-vf", f"crop={w}:{h}:0:{int(y0)},signalstats,metadata=print:file=-",
           "-f", "null", "-"]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=30).stdout
    except (subprocess.TimeoutExpired, FileNotFoundError) as e:
        print(f"ffmpeg-Fehler bei t={t}: {e}", file=sys.stderr)
        return None
    m = re.search(r"lavfi\.signalstats\.YAVG=([\d.]+)", out)
    return float(m.group(1)) if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True, help="geschnittenes Video (vor Overlay)")
    ap.add_argument("--plan", required=True)
    ap.add_argument("--band-y-pct", type=float, default=0.66)
    ap.add_argument("--width", type=int, default=1080)
    ap.add_argument("--height", type=int, default=1920)
    ap.add_argument("--line-height", type=int, default=86)
    ap.add_argument("--samples", type=int, default=12, help="Anzahl Messpunkte")
    ap.add_argument("--apply", action="store_true", help="Empfehlung in den Plan schreiben")
    a = ap.parse_args()

    plan = json.load(open(a.plan, encoding="utf-8"))
    end = float(plan["timeline"]["end"])

    # Messpunkte: bevorzugt Kartenmitten aus einem vorhandenen Build-Report,
    # sonst gleichmäßig über die Laufzeit verteilt.
    report_path = os.path.join(os.path.dirname(a.plan), "build-report.json")
    times = []
    if os.path.exists(report_path):
        cards = json.load(open(report_path, encoding="utf-8")).get("cards", [])
        times = [(c["s"] + c["e"]) / 2 for c in cards]
    if not times:
        step = end / (a.samples + 1)
        times = [step * (i + 1) for i in range(a.samples)]
    if len(times) > a.samples:                      # gleichmäßig ausdünnen
        k = len(times) / a.samples
        times = [times[int(i * k)] for i in range(a.samples)]

    band_y = a.height * a.band_y_pct
    y0, y1 = band_y - a.line_height, band_y + a.line_height

    vals = []
    for t in times:
        v = probe_luma(a.video, t, y0, y1, a.width)
        if v is not None:
            vals.append((round(t, 2), round(v, 1)))

    assert vals, "Keine Messwerte — Video oder ffmpeg prüfen"
    ys = [v for _, v in vals]
    avg, mx = sum(ys) / len(ys), max(ys)
    bright = [t for t, v in vals if v > THRESH_HARD]

    if avg > THRESH_HARD or len(bright) >= max(2, len(vals) // 3):
        verdict, alpha = "SCRIM PFLICHT", ALPHA_HARD
    elif avg > THRESH_SOFT:
        verdict, alpha = "SCRIM EMPFOHLEN", ALPHA_SOFT
    else:
        verdict, alpha = "Schatten reicht", 0.0

    print(f"Textzone y {int(y0)}–{int(y1)} · {len(vals)} Messpunkte")
    print(f"  Mittel {avg:.1f} · Max {mx:.1f} · über {THRESH_HARD:.0f}: {len(bright)} Stellen")
    print(f"  → {verdict}" + (f" (Scrim-Alpha {alpha})" if alpha else ""))
    if bright[:6]:
        print(f"  helle Stellen bei s: {bright[:6]}")

    if a.apply and alpha > 0:
        plan.setdefault("style", {}).setdefault("karaoke", {}).setdefault("scrim", {})["alpha"] = alpha
        plan["style"]["karaoke"]["scrim"].setdefault("radius", 14)
        json.dump(plan, open(a.plan, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print(f"  Plan aktualisiert: style.karaoke.scrim.alpha = {alpha}")
    elif a.apply:
        print("  Plan unverändert (kein Scrim nötig)")


if __name__ == "__main__":
    main()
