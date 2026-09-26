#!/usr/bin/env python3
"""Render für Clip-Montagen (references/clip-montage.md): Segmente → Concat → Stem-Mix → Master + Web + QC.

  montage_render.py --plan montage-plan.json [--ov ov/] [--seg seg/]

Je Slide: die letzten `dauer` Sekunden des Clips (oder ab `start`), 1080×1920, Push-in 100→105 %,
Grade, Overlay-Pop-in (3 PNG-Frames + tpad-Hold), Titel-Fade auf dem Slide mit "titel": true.
Segmente werden nur neu gerendert, wenn sich Slide, Grade, Weißabgleich oder Overlay-PNGs geändert haben
(Schlüssel in seg/<id>.key) — früher blieb nach einer Textänderung der alte Text im Video (Katzer 09/2026).
Gates (Kunden-Feedback 09/2026, jeweils Abbruch statt Warnung):
- Color Grading ist Pflicht: ein Plan-"grade" ohne curves/Sättigung wird abgelehnt (Mini-Grades wie
  nur eq=contrast=1.04 sind durchgerutscht). Ohne "grade" gilt GRADE_STD.
- Automatischer Weißabgleich je Slide aus neutralen Pixeln (Laborlicht grün/blau), gedeckelt ±6 %;
  abschaltbar mit "weissabgleich": false im Plan oder je Slide.
- Zwei Slides aus derselben Quelle dürfen sich zeitlich nicht überlappen (sonst Rückwärtssprung im Bild).
Ton-Regel (zweimal teuer gelernt): KEIN loudnorm im Mix-Filtergraph — es schneidet ~3 s vom Ende ab.
Stattdessen Stems auf Videolänge padden, LUFS messen, per volume auf Ziel, amix, Limiter, kein Fade,
danach linear auf −14 LUFS mastern (audio.md). Am Ende wird die Ton- gegen die Bildlänge geprüft;
Abweichung > 0,1 s = FEHLER, nicht liefern.
"""
import argparse, hashlib, json, os, re, subprocess, sys
import numpy as np
GRADE_STD = "curves=all='0/0 0.22/0.30 0.55/0.63 1/1',eq=contrast=1.05:saturation=1.14:gamma=1.04,unsharp=5:5:0.4"

def run(cmd): subprocess.run(cmd, check=True)
def dur(f): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', f]).decode().strip().strip(','))
def stream_dur(f, sel): return float(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', sel, '-show_entries', 'stream=duration', '-of', 'csv=p=0', f]).decode().strip().strip(','))
def lufs(f):
    out = subprocess.run(['ffmpeg', '-i', f, '-af', 'ebur128', '-f', 'null', '-'], capture_output=True, text=True).stderr
    return float(re.findall(r'I:\s+(-?[\d.]+) LUFS', out)[-1])

def weissabgleich(f, t):
    """Gains aus nahezu neutralen Pixeln (geringe Sättigung, mittlere bis helle Werte) eines Mittel-Frames.
    Grauwelt über das ganze Bild würde orange Modelle/Haut 'neutralisieren' — deshalb nur neutrale Pixel."""
    try:
        raw = subprocess.check_output(['ffmpeg', '-v', 'error', '-ss', f'{t:.2f}', '-i', f, '-frames:v', '1', '-vf', 'scale=160:-2',
                                       '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'])
        px = np.frombuffer(raw, np.uint8).reshape(-1, 3).astype(float)
    except Exception:
        return None
    mx, mn = px.max(1), px.min(1); lum = px.mean(1)
    m = ((mx - mn) < 0.12 * np.maximum(mx, 1)) & (lum > 70) & (lum < 245)
    if m.mean() < 0.05: return None
    mean = px[m].mean(0); g = np.clip(mean.mean() / mean, 0.94, 1.06)
    if np.abs(g - 1).max() < 0.01: return None
    return f"colorchannelmixer=rr={g[0]:.3f}:gg={g[1]:.3f}:bb={g[2]:.3f}"

def grade_gate(grade):
    g = grade.replace(' ', '')
    if 'curves' not in g or not re.search(r'saturation=|vibrance', g):
        sys.exit('Plan-"grade" zu schwach — Color Grading ist Pflicht (curves + Sättigung/Vibrance, idealerweise Schärfe). '
                 '"grade" weglassen = GRADE_STD, oder vollständigen Grade angeben.')

def overlap_gate(slides):
    seen = {}
    for s in slides:
        if 'start' not in s: continue
        a, b = float(s['start']), float(s['start']) + float(s['dauer'])
        for sid, (a2, b2) in seen.get(s['src'], []):
            if a < b2 and a2 < b:
                sys.exit(f"Slides {sid} und {s['id']} überlappen in {s['src']} ({a2:.2f}–{b2:.2f} / {a:.2f}–{b:.2f}) — Rückwärtssprung. Startpunkte verschieben.")
        seen.setdefault(s['src'], []).append((s['id'], (a, b)))

def seg_key(s, grade, wb, ovdir):
    h = hashlib.sha1(json.dumps(s, sort_keys=True).encode() + grade.encode() + (wb or '').encode())
    for d in (os.path.join(ovdir, s['id']), os.path.join(ovdir, 'titel') if s.get('titel') else None):
        if d and os.path.isdir(d):
            for n in sorted(os.listdir(d)): h.update(n.encode()); h.update(open(os.path.join(d, n), 'rb').read())
    return h.hexdigest()

def quelle(src_dir, name):
    for ext in ('', '.mov', '.MOV', '.mp4', '.MP4'):
        p = os.path.join(src_dir, name + ext)
        if os.path.isfile(p): return p
    sys.exit(f'Quelle fehlt: {name} in {src_dir}')

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('--plan', required=True); ap.add_argument('--ov', default='ov'); ap.add_argument('--seg', default='seg'); ap.add_argument('--work', default='build')
    a = ap.parse_args(); cfg = json.load(open(a.plan, encoding='utf-8'))
    OFF = float(cfg['audio_offset']); L = cfg.get('lautheit', {}); L_MUS = L.get('musik', -16.5); L_AMB = L.get('ambiente', -24)
    GRADE = cfg.get('grade', GRADE_STD); OUT = cfg.get('output', 'montage'); os.makedirs(a.seg, exist_ok=True); os.makedirs(a.work, exist_ok=True)
    if 'grade' in cfg: grade_gate(GRADE)
    overlap_gate(cfg['slides'])
    os.makedirs(os.path.dirname(OUT) or '.', exist_ok=True); liste = []
    for s in cfg['slides']:
        if 'dauer' not in s: sys.exit(f"Slide {s['id']} hat keine 'dauer' — erst montage_beatgrid.py plan ausführen.")
        f = quelle(cfg['src_dir'], s['src']); d = dur(f); D = float(s['dauer']); start = float(s['start']) if 'start' in s else max(0.0, d - D)
        out = os.path.join(a.seg, f"{s['id']}.mp4"); liste.append(out)
        wb = weissabgleich(f, start + D / 2) if s.get('weissabgleich', cfg.get('weissabgleich', True)) else None
        key = seg_key(s, GRADE, wb, a.ov); kf = out[:-4] + '.key'
        if os.path.exists(out) and os.path.getsize(out) > 0 and os.path.exists(kf) and open(kf).read() == key: continue
        if wb: print(f"Weißabgleich {s['id']}: {wb}")
        hold = f'tpad=stop_mode=clone:stop_duration={D + 1:.2f}'
        inputs = ['-ss', f'{start:.3f}', '-t', f'{D:.3f}', '-i', f, '-framerate', '30', '-i', os.path.join(a.ov, s['id'], 'f%02d.png')]
        fc = (f"[0:v]fps=30,setpts=PTS-STARTPTS,scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,setsar=1,"
              f"zoompan=z='1+0.05*on/{int(D * 30)}':d=1:x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps=30,"
              f"format=yuv420p,{(wb + ',') if wb else ''}{GRADE}[v0];[1:v]format=rgba,{hold}[bb];[v0][bb]overlay=0:0:format=auto:shortest=1[v1]")
        last = 'v1'
        if s.get('titel'):
            inputs += ['-framerate', '30', '-i', os.path.join(a.ov, 'titel', 'f%02d.png')]
            fc += f";[2:v]format=rgba,{hold},fade=out:st={D - 0.35:.2f}:d=0.3:alpha=1[tt];[v1][tt]overlay=0:0:format=auto:shortest=1[v2]"; last = 'v2'
        run(['ffmpeg', '-v', 'error', '-y'] + inputs + ['-filter_complex', fc, '-map', f'[{last}]', '-map', '0:a?', '-t', f'{D:.3f}',
             '-c:v', 'libx264', '-preset', 'veryfast', '-crf', '19', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-ac', '2', out])
        open(kf, 'w').write(key); print('Segment', out, f'{dur(out):.2f}s')
    concat = os.path.join(a.work, 'concat.txt'); raw = os.path.join(a.work, 'concat_raw.mp4')
    open(concat, 'w').write(''.join(f"file '{os.path.abspath(p)}'\n" for p in liste))
    run(['ffmpeg', '-v', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', concat, '-c', 'copy', raw]); d = dur(raw)
    amb, mus, mix = (os.path.join(a.work, n) for n in ('amb.wav', 'mus.wav', 'mix.wav'))
    run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-vn', '-af', f'apad,atrim=0:{d:.4f}', '-ar', '48000', '-ac', '2', amb])
    run(['ffmpeg', '-v', 'error', '-y', '-ss', f'{OFF:.3f}', '-i', cfg['musik'], '-vn', '-af', f'apad,atrim=0:{d:.4f}', '-ar', '48000', '-ac', '2', mus])
    ga = L_AMB - lufs(amb); gm = L_MUS - lufs(mus)
    af = f"[0:a]volume={ga:.2f}dB[a0];[1:a]volume={gm:.2f}dB[a1];[a0][a1]amix=inputs=2:duration=first:normalize=0,alimiter=limit=0.94:attack=5:release=50[a]"
    run(['ffmpeg', '-v', 'error', '-y', '-i', amb, '-i', mus, '-filter_complex', af, '-map', '[a]', mix])
    # Linear mastern wie in audio.md: messen, volume, Limiter -> -14 LUFS, kein loudnorm
    master = os.path.join(a.work, 'master.wav'); gmaster = -14.0 - lufs(mix)
    run(['ffmpeg', '-v', 'error', '-y', '-i', mix, '-af', f'volume={gmaster:.2f}dB,alimiter=limit=0.81:level=false', master]); mix = master
    run(['ffmpeg', '-v', 'error', '-y', '-i', raw, '-i', mix, '-map', '0:v', '-map', '1:a', '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-shortest', '-movflags', '+faststart', f'{OUT}_master.mp4'])
    run(['ffmpeg', '-v', 'error', '-y', '-i', f'{OUT}_master.mp4', '-c:v', 'libx264', '-preset', 'slow', '-crf', '25', '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', f'{OUT}.mp4'])
    vd, ad = stream_dur(f'{OUT}.mp4', 'v'), stream_dur(f'{OUT}.mp4', 'a'); ok = abs(vd - ad) < 0.1
    print(f'FERTIG {OUT}.mp4 · Bild {vd:.2f} s · Ton {ad:.2f} s · Summe {lufs(f"{OUT}.mp4"):.1f} LUFS · QC {"OK" if ok else "FEHLER: Ton ≠ Bild — nicht liefern"}')
    sys.exit(0 if ok else 1)

if __name__ == '__main__': main()
