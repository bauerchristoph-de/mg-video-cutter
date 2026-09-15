#!/usr/bin/env python3
"""Beat-Raster, Beat-Dauern und Lied-Ausrichtung für Clip-Montagen (references/clip-montage.md).

  montage_beatgrid.py beats <musik>                       -> beats.npy neben der Musik, BPM
  montage_beatgrid.py plan  <montage-plan.json> <beats.npy> [--k0 N]
        Schreibt 'dauer' je Slide aus 'beats' und 'audio_offset' = beats[k0] in den Plan.
        k0 = Beat-Index, der auf Frame 0 liegt (Default: erster Beat mit vollem Pegel = Beat-Einsatz,
        gemessen als erster Beat, ab dem die Lautheit ≥ Median − 3 dB ist).
  montage_beatgrid.py align <vorlage_audio> <lied> [--von 11 --bis 31]
        Versatz delta (Lied-Zeit = Vorlage-Zeit + delta) per Onset-Kreuzkorrelation. Damit trifft die
        Montage dieselbe Liedstelle wie das Vorlagen-Reel, ohne den Vorlagen-Ton zu verwenden.
Abhängigkeiten: ffmpeg, numpy; für 'beats' zusätzlich librosa.
"""
import sys, json, argparse, subprocess, os
import numpy as np

def laden(f, sr=22050):
    raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-i', f, '-ac', '1', '-ar', str(sr), '-f', 'f32le', '-'])
    return np.frombuffer(raw, np.float32), sr

def onsets(x, hop=32):
    n = len(x) // hop
    e = np.log(np.sqrt((x[:n * hop].reshape(n, hop) ** 2).mean(1)) + 1e-6)
    return np.maximum(np.diff(e, prepend=e[0]), 0)

def cmd_beats(musik):
    import librosa
    y, sr = librosa.load(musik, sr=22050, mono=True)
    tempo, frames = librosa.beat.beat_track(y=y, sr=sr, units='frames')
    t = librosa.frames_to_time(frames, sr=sr)
    out = os.path.join(os.path.dirname(os.path.abspath(musik)), 'beats.npy'); np.save(out, t)
    # Pegel je Beat-Intervall -> Beat-Einsatz (erster Beat mit vollem Pegel)
    rms = [float(np.sqrt(np.mean(y[int(a * sr):int(b * sr)] ** 2) + 1e-12)) for a, b in zip(t[:-1], t[1:])]
    db = 20 * np.log10(np.array(rms) + 1e-9); voll = np.median(db) - 3
    k_ein = int(np.argmax(db >= voll))
    print(f'BPM {float(np.atleast_1d(tempo)[0]):.1f} · {len(t)} Beats · Beat-Einsatz Index {k_ein} = {t[k_ein]:.3f} s · {out}')

def cmd_plan(pfad, beatsdatei, k0):
    b = np.load(beatsdatei); p = json.load(open(pfad, encoding='utf-8'))
    if k0 is None:
        k0 = int(p.get('beat_einsatz', 0))
    k = k0; t = 0
    for s in p['slides']:
        n = int(s['beats']); s['dauer'] = round(float(b[k + n] - b[k]), 3); k += n; t += s['dauer']
        print(f"{s['id']:24s} {n} Beats  {s['dauer']:.3f} s  cut@{t:6.2f}  lied@{t + b[k0]:6.2f}")
    p['audio_offset'] = round(float(b[k0]), 3)
    json.dump(p, open(pfad, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)
    print(f'audio_offset {p["audio_offset"]} · gesamt {t:.2f} s')

def cmd_align(vorlage, lied, von, bis):
    r, sr = laden(vorlage); l, _ = laden(lied); hop = 32; vor = min(2.0, von)
    er = onsets(r[int(von * sr):int(bis * sr)], hop); el = onsets(l[int((von - vor) * sr):int((bis + 4) * sr)], hop)
    c = np.correlate(el, er, mode='valid'); k = int(np.argmax(c)); delta = k * hop / sr - vor
    print(f'delta = {delta:.4f} s (Lied-Zeit = Vorlage-Zeit + delta) · Peak/Median {c[k] / np.median(c):.1f} (>2 = eindeutig)')
    print('audio_offset für den Plan = (gewünschte Vorlage-Zeit bei Frame 0) + delta; danach mit beats.npy des LIEDS auf den nächsten Beat runden.')

if __name__ == '__main__':
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest='cmd', required=True)
    a = sub.add_parser('beats'); a.add_argument('musik')
    a = sub.add_parser('plan'); a.add_argument('plan'); a.add_argument('beats'); a.add_argument('--k0', type=int)
    a = sub.add_parser('align'); a.add_argument('vorlage'); a.add_argument('lied'); a.add_argument('--von', type=float, default=11.0); a.add_argument('--bis', type=float, default=31.0)
    x = ap.parse_args()
    {'beats': lambda: cmd_beats(x.musik), 'plan': lambda: cmd_plan(x.plan, x.beats, x.k0), 'align': lambda: cmd_align(x.vorlage, x.lied, x.von, x.bis)}[x.cmd]()
