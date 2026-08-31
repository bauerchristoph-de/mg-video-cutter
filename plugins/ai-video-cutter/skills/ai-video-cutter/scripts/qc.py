# -*- coding: utf-8 -*-
"""
AI Video-Cutter · qc.py — alle Pflicht-Gates gegen das fertige Video.

Aufruf
------
  python3 qc.py --video fertig/xyz.mp4 --build build/ [--plan cut-plan.json]

Ausgabe: Klartext-Report + qc-report.json + einen Kontaktbogen (qc-frames.jpg)
mit Frames an den Kartenmitten. Exit-Code 1, wenn ein hartes Gate reißt.

Warum als Skript und nicht als Checkliste
------------------------------------------
Eine Checkliste in Prosa wird beim dritten Video überflogen. Diese Gates haben
alle schon reale Fehler gefangen — deshalb laufen sie, statt gelesen zu werden.
Der Kontaktbogen ist Absicht: Zahlen allein erkennen nicht, dass weiße Schrift
auf einem weißen Polohemd liegt. Das Bild MUSS angesehen werden.
"""
import json, subprocess, argparse, re, os, sys, math

GATES = []

NUM_RE = re.compile(r"\d[\d.,]*")


def load_config(path):
    """kunden-config.yaml laden. Fehlt PyYAML, wird laut abgebrochen statt still
    weiterzulaufen — ein uebersprungenes Gate ist schlimmer als ein Fehler."""
    if not path:
        return {}
    assert os.path.exists(path), f"Config nicht gefunden: {path}"
    try:
        import yaml
    except ImportError:
        sys.exit("PyYAML fehlt (pip install pyyaml) — Inhalts-Gates koennen nicht laufen.")
    return yaml.safe_load(open(path, encoding="utf-8")) or {}


def to_num(tok):
    """'2.046' -> 2046.0 · '0,25' -> 0.25 · sonst None."""
    t = tok.strip().strip(".,!?;:()")
    if not re.fullmatch(r"\d{1,3}(\.\d{3})+(,\d+)?|\d+(,\d+)?", t):
        return None
    try:
        return float(t.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def numbers_in(text):
    """Alle Zahlwerte eines Textes, in Reihenfolge, mit Token-Index."""
    out = []
    for i, tok in enumerate(text.split()):
        m = NUM_RE.search(tok)
        if m:
            v = to_num(m.group())
            if v is not None:
                out.append((i, v))
    return out


def rechen_pruefung(text, window=45, tol=0.02):
    """Prueft Prozentrechnungen im Text: Basis x Prozent / 100 == Ergebnis.

    Whisper vertippt sich bei Betraegen HOCHKONFIDENT (gemessen: falsche Zahlen mit
    p=0,94 bis 0,98) — die Konfidenz taugt deshalb NICHT als Detektor. Die Arithmetik
    schon: 2046 x 40 % = 818, gesagt wurde 1056 — also war die Basis 2640.

    Nur wo neben der Prozentangabe ueberhaupt zwei Zahlen stehen, wird geprueft;
    rhetorische Prozente ('zu 100 Prozent') haben keine Rechnung und werden
    uebersprungen.
    """
    toks = text.split()
    nums = numbers_in(text)
    treffer = []
    for pi, p in nums:
        umfeld = " ".join(toks[pi:pi + 2]).lower()
        ist_prozent = "%" in toks[pi] or umfeld.startswith(toks[pi].lower() + " prozent") \
            or "prozent" in umfeld
        if not ist_prozent or not (0 < p <= 100):
            continue
        cand = [(i, v) for i, v in nums if abs(i - pi) <= window and v != p and v > 0]
        if len({v for _, v in cand}) < 2:
            continue                      # keine Rechnung im Umfeld -> nichts zu pruefen
        stimmig = None
        for i, basis in cand:
            for j, ergebnis in cand:
                if j <= i or basis <= ergebnis:
                    continue
                if abs(basis * p / 100 - ergebnis) <= max(1.0, tol * ergebnis):
                    stimmig = (basis, p, ergebnis)
        treffer.append({"prozent": p, "stimmig": stimmig,
                        "zahlen": sorted({v for _, v in cand})[:10]})
    return treffer


def sh(cmd, timeout=180):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)


def gate(name, ok, detail):
    GATES.append({"gate": name, "ok": bool(ok), "detail": detail})
    print(f"  [{'OK ' if ok else 'FAIL'}] {name}: {detail}")
    return ok


def probe(video, entries, stream="v:0"):
    r = sh(["ffprobe", "-v", "error", "-select_streams", stream,
            "-show_entries", entries, "-of", "json", video])
    return json.loads(r.stdout or "{}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--video", required=True)
    ap.add_argument("--build", required=True, help="Ordner mit build-report.json / events.json")
    ap.add_argument("--plan", help="cut-plan.json (für Wort-Vollständigkeit)")
    ap.add_argument("--target-lufs", type=float, default=-14.0)
    ap.add_argument("--config", help="kunden-config.yaml — schaltet die Inhalts-Gates frei")
    ap.add_argument("--transcript", help="Whisper-JSON (fuer Sprechtempo)")
    ap.add_argument("--format", choices=["reel", "longform"], help="Zielformat (CTA-Kanaltreue)")
    a = ap.parse_args()

    assert os.path.exists(a.video), f"Video nicht gefunden: {a.video}"
    report_path = os.path.join(a.build, "build-report.json")
    assert os.path.exists(report_path), f"build-report.json fehlt in {a.build}"
    br = json.load(open(report_path, encoding="utf-8"))
    cards = br.get("cards", [])
    W = br["canvas"]["w"]
    band_y = br["band_y"]
    lh = br["style_used"]["karaoke"]["line_height"]
    scrim_alpha = br["style_used"]["karaoke"].get("scrim", {}).get("alpha", 0)

    cfg = load_config(a.config)
    emph_lines = (br.get("emphasis") or {}).get("lines", [])
    shown_text = " ".join([c["txt"] for c in cards] +
                          [" ".join(l) for l in emph_lines])

    print(f"\nQC · {os.path.basename(a.video)}")
    print("-" * 60)

    # 1 --------------------------------------------------- Streamdauern
    v = probe(a.video, "stream=duration")["streams"][0]
    aud = probe(a.video, "stream=duration", "a:0")
    vd = float(v.get("duration", 0))
    ad = float(aud["streams"][0]["duration"]) if aud.get("streams") else 0.0
    gate("A/V-Dauer", abs(vd - ad) < 0.1, f"Video {vd:.3f}s · Audio {ad:.3f}s · Δ {abs(vd-ad):.3f}s")

    # 2 --------------------------------------------------- Freeze-Scan
    r = sh(["ffmpeg", "-v", "info", "-i", a.video, "-vf", "freezedetect=n=-60dB:d=0.5",
            "-map", "0:v:0", "-f", "null", "-"])
    freezes = len(re.findall(r"freeze_start", r.stderr))
    gate("Freeze-Scan", freezes == 0, f"{freezes} Treffer")

    # 3 --------------------------------------------------- Loudness / True Peak
    r = sh(["ffmpeg", "-v", "info", "-i", a.video, "-af", "ebur128=peak=true",
            "-f", "null", "-"])
    tail = r.stderr[-2500:]
    mi = re.search(r"I:\s*(-?[\d.]+)\s*LUFS", tail)
    mp = re.search(r"Peak:\s*(-?[\d.]+)\s*dBFS", tail)
    lufs = float(mi.group(1)) if mi else None
    peak = float(mp.group(1)) if mp else None
    if lufs is not None:
        gate("Loudness", abs(lufs - a.target_lufs) <= 0.5,
             f"{lufs:.2f} LUFS (Ziel {a.target_lufs} ±0,5)")
    if peak is not None:
        gate("True Peak", peak <= -1.2, f"{peak:.2f} dBTP (Grenze −1,2)")

    # 4 --------------------------------------------------- Karten-Kontinuität
    micro = [(cards[i]["e"], cards[i + 1]["s"]) for i in range(len(cards) - 1)
             if 0 < cards[i + 1]["s"] - cards[i]["e"] < 0.2]
    over = [(cards[i]["e"], cards[i + 1]["s"]) for i in range(len(cards) - 1)
            if cards[i + 1]["s"] < cards[i]["e"] - 1e-6]
    gate("Karten-Kontinuität", not micro and not over,
         f"{len(micro)} Mikro-Lücken · {len(over)} Überlappungen")

    # 5 --------------------------------------------------- Vollständigkeit
    if a.plan and os.path.exists(a.plan):
        plan = json.load(open(a.plan, encoding="utf-8"))
        spoken = [w["w"].strip(".,?!").lower() for w in plan.get("words", [])]
        low = shown_text.lower()
        missing = [w for w in spoken if w and w not in low]
        gate("Vollständigkeit", not missing,
             "alle Wörter sichtbar" if not missing else f"{len(missing)} fehlen: {missing[:8]}")

    # 6 --------------------------------------------------- Lesbarkeit (Kontrast)
    # Gemessen wird die Helligkeit der Textzone im FERTIGEN Bild. Liegt helle
    # Schrift auf hellem Grund, ist der Streifen durchgehend hell und flau.
    probes, bright = [], 0
    step = max(1, len(cards) // 8)
    for c in cards[::step][:8]:
        t = (c["s"] + c["e"]) / 2
        rr = sh(["ffmpeg", "-v", "error", "-ss", f"{t:.3f}", "-i", a.video, "-frames:v", "1",
                 "-vf", f"crop={W}:{lh*2}:0:{max(0,int(band_y-lh))},signalstats,metadata=print:file=-",
                 "-f", "null", "-"], timeout=60)
        m = re.search(r"lavfi\.signalstats\.YAVG=([\d.]+)", rr.stdout)
        if m:
            y = float(m.group(1))
            probes.append((round(t, 2), round(y, 1)))
            if y > 140:
                bright += 1
    if probes:
        avg = sum(y for _, y in probes) / len(probes)
        ok = bright == 0 or scrim_alpha > 0
        gate("Lesbarkeit", ok,
             f"Textzone Ø {avg:.0f} · {bright}/{len(probes)} hell" +
             (f" · Scrim aktiv ({scrim_alpha})" if scrim_alpha else " · KEIN Scrim"))

    # 7 --------------------------------------------------- SFX-Peaks
    ev_path = os.path.join(a.build, "events.json")
    if os.path.exists(ev_path):
        ev = json.load(open(ev_path, encoding="utf-8"))
        n_ev = sum(len(v) for v in ev.values())
        gate("SFX-Events", True, f"{n_ev} Events geplant (Peak-Abgleich in make_sfx.py --check)")

    # 8 --------------------------------------------------- Glossar
    # Bekannte Transkriptionsfehler des Kunden duerfen im Endtext nicht stehen.
    glossar = (cfg.get("glossar") or {})
    fehlerpaare = list(glossar.get("fachbegriffe") or []) + list(glossar.get("phrasen") or [])
    if fehlerpaare:
        low = shown_text.lower()
        drin = [falsch for falsch, _ in fehlerpaare if falsch.lower() in low]
        gate("Glossar", not drin,
             "keine bekannten Fehler" if not drin else f"{len(drin)} unkorrigiert: {drin[:5]}")

    # 9 --------------------------------------------------- Zahlen: Rechenpruefung
    # Die Zahl ist bei zahlengetriebenen Kunden die Kernbotschaft. Whisper vertippt
    # sich dabei HOCHKONFIDENT — nur die Arithmetik deckt das auf.
    if cfg.get("qc_zahlen", True) and cards:
        treffer = rechen_pruefung(shown_text)
        unstimmig = [t for t in treffer if not t["stimmig"]]
        gate("Zahlen-Rechenpruefung", not unstimmig,
             f"{len(treffer)} Prozentrechnung(en) geprueft" if not unstimmig
             else f"{len(unstimmig)} nicht nachvollziehbar: " +
                  "; ".join(f"{t['prozent']:g}% mit {t['zahlen']}" for t in unstimmig[:3]))

    # 10 -------------------------------------------------- Zahlen: Deckung
    # Jede angezeigte Zahl muss auch gesprochen worden sein (faengt Tippfehler
    # im Untertitel, die die Rechenpruefung nicht sieht).
    if a.plan and os.path.exists(a.plan):
        gesprochen = {v for _, v in numbers_in(
            " ".join(w["w"] for w in json.load(open(a.plan, encoding="utf-8")).get("words", [])))}
        erfunden = sorted({v for _, v in numbers_in(shown_text)} - gesprochen)
        gate("Zahlen-Deckung", not erfunden,
             "alle angezeigten Zahlen gesprochen" if not erfunden
             else f"{len(erfunden)} nicht im Transkript: {erfunden[:6]}")

    # 11 -------------------------------------------------- Pflichtphrasen
    # Rechtliche/berufsrechtliche Weichmacher ("in der Regel", "meine Erfahrung")
    # duerfen beim Kuerzen nicht wegfallen — sonst aendert sich das Aussage-Niveau.
    pflicht = cfg.get("pflicht_phrasen") or []
    if pflicht:
        low = shown_text.lower()
        fehlen = [p for p in pflicht if p.lower() not in low]
        gate("Pflichtphrasen", not fehlen,
             "alle vorhanden" if not fehlen else f"fehlen: {fehlen[:4]}")

    # 12 -------------------------------------------------- Sprechtempo
    prof = cfg.get("sprechprofil") or {}
    ziel = prof.get(f"wpm_{a.format}") if a.format else None
    if ziel and vd > 0:
        wpm = len(shown_text.split()) / vd * 60
        tol = prof.get("wpm_toleranz", 25)
        gate("Sprechtempo", abs(wpm - ziel) <= tol,
             f"{wpm:.0f} WPM (Profil {ziel} ±{tol})")

    # 13 -------------------------------------------------- CTA-Kanaltreue
    # Longform traegt den CTA-Block, Reels enden nach dem Abbinder. Nie vertauschen.
    cta = cfg.get("cta_marker") or []
    if cta and a.format:
        low = shown_text.lower()
        hat = any(m.lower() in low for m in cta)
        soll = bool(((cfg.get("formate") or {}).get(a.format) or {}).get("hat_cta_block"))
        gate("CTA-Kanaltreue", hat == soll,
             f"{a.format}: CTA {'vorhanden' if hat else 'fehlt'}, erwartet "
             f"{'vorhanden' if soll else 'keiner'}")

    # 14 -------------------------------------------------- Formatvorgaben
    fmt = ((cfg.get("formate") or {}).get(a.format) or {}) if a.format else {}
    if fmt:
        vs = probe(a.video, "stream=width,height")["streams"][0]
        soll_res = fmt.get("aufloesung")
        if soll_res:
            gate("Aufloesung", [vs["width"], vs["height"]] == list(soll_res),
                 f"{vs['width']}x{vs['height']} (Soll {soll_res[0]}x{soll_res[1]})")
        spanne = fmt.get("ziel_dauer_s")
        if spanne:
            gate("Laufzeit", spanne[0] <= vd <= spanne[1],
                 f"{vd:.1f}s (Ziel {spanne[0]}–{spanne[1]}s)")

    # 15 -------------------------------------------------- Kontaktbogen
    strip = os.path.join(a.build, "qc-frames.jpg")
    picks = cards[::max(1, len(cards) // 6)][:6]
    if picks:
        parts = []
        for i, c in enumerate(picks):
            t = (c["s"] + c["e"]) / 2
            p = os.path.join(a.build, f"_qc{i}.png")
            sh(["ffmpeg", "-y", "-v", "error", "-ss", f"{t:.3f}", "-i", a.video,
                "-frames:v", "1", "-vf", "scale=360:-2", p], timeout=60)
            if os.path.exists(p):
                parts.append(p)
        if parts:
            sh(["ffmpeg", "-y", "-v", "error"] +
               sum([["-i", p] for p in parts], []) +
               ["-filter_complex", f"hstack=inputs={len(parts)}", strip], timeout=90)
            for p in parts:
                os.remove(p)
            print(f"\n  Kontaktbogen: {strip}")
            print("  → PFLICHT: dieses Bild ANSEHEN. Zahlen erkennen keine")
            print("    weiße Schrift auf weißem Hemd und keinen Text über einem Logo.")

    # ---------------------------------------------------- Fazit
    failed = [g for g in GATES if not g["ok"]]
    json.dump({"video": a.video, "gates": GATES, "luma_probes": probes},
              open(os.path.join(a.build, "qc-report.json"), "w"), ensure_ascii=False, indent=1)
    print("-" * 60)
    if failed:
        print(f"DURCHGEFALLEN · {len(failed)} Gate(s): {', '.join(g['gate'] for g in failed)}")
        print("NICHT ausliefern.")
        sys.exit(1)
    print(f"BESTANDEN · {len(GATES)} Gates · Kontaktbogen trotzdem ansehen.")


if __name__ == "__main__":
    main()
