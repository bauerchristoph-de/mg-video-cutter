# AI Video-Cutter — Plugin-Marketplace

Privates Plugin-Repository. Zugriff = Lizenz.

## Installation (einmalig)

Im Claude-Client (Cowork / Claude Code):

```
/plugin marketplace add bauerchristoph-de/mg-video-cutter
/plugin install ai-video-cutter@mg-video-cutter
```

Auto-Update aktivieren, damit Verbesserungen automatisch ankommen.

## Erster Start

Nach der Installation einfach sagen: **„Richte den Video-Cutter ein.“**
Das Plugin führt durch das Setup: CI, Kanäle, Marken-Analyse (Website + Social-Accounts + 3–7 Referenz-Videos) und legt den lokalen Kundenordner an. Danach: Rohvideo in den Ordner legen, sagen was gebraucht wird, fertiges Video zurückbekommen.

## Changelog

- **0.11.0** (25.09.2026) — Untertitel lesbar auf Weiß ohne Kontur: `build.py` kann Schicht-Schatten (Liste von Ebenen mit `spread`), neuer Default = Kontakt-Halo + weicher Fernschatten; Chip auf Versalhöhe zentriert („H" statt „Hg"); QC-Gate „Lesbarkeit" erkennt den Halo. Neue Regeln: Pausen mitten im Satz komplett raus, B-Roll im Talking-Head (erste 3 s Gesicht, max. 2 B-Rolls am Stück, 30–40 %), Serien-CTA „Folge für Teil n: <Thema>" mit Outro-Vorschau.
- **0.10.0** (15.09.2026) — Zweiter Auftragstyp „Clip-Montage mit Musik" (Trend-Reels aus Handyclips ohne Sprache): neue Reference `clip-montage.md` mit Look, Beat-Tempo, Musik-Regeln und Feedback-Kaskade; Skripte `montage_beatgrid.py` (Beat-Raster, Liedstelle der Vorlage, Beat-Dauern), `montage_build.py` (IG-native Overlays aus der Kunden-Config), `montage_render.py` (Stem-Mix ohne loudnorm, A/V-Gate). Neue Ton-Falle dokumentiert: `loudnorm` im Mix-Filtergraph schneidet das Ende der Tonspur ab.
- **0.9.0** (02.09.2026) — Der Skill steht wieder vollständig auf der eigenen ffmpeg-Pipeline: die optionale zweite Render-Engine ist entfernt, alle Regeln und Werte gelten unverändert weiter.
- **0.8.0** (02.09.2026) — Neues Gate für die wichtigste Regel des Systems: `pausen_scan.py` misst die Sprechpausen adaptiv (Rauschschwelle aus dem Material statt Konstante) und prüft jeden geplanten Schnitt dagegen — verschluckte Silben fallen jetzt vor dem Build auf, nicht beim Ansehen. Neue Referenzen: `animation-kurven.md` (alle Animationswerte als prüfbare Zahlen statt Prosa — Overshoot, Peak-Lage, Frame-Rundung, wahrnehmungsgerechte Skalierung), `loesungsbibliothek.md` (Einstieg über den Fall statt über die Dateiliste). QC erweitert um Abschnitt D (Gates 21–23).
- **0.4.1** (24.08.2026) — Interop: geteilter Kundenordner mit dem AI Post-Generator (kunden-config.yaml, marken-profil.md, assets/, fertig/).
- **0.4.0** (24.08.2026) — Erstes Release: Setup-Interview, Marken-Analyse (Texte + Videos), Karaoke-/Emphasis-Caption-System, Schnitt-/Audio-/Render-Regeln, QC-Gates, Learnings-System, Begleit-Content (Caption pro Kanal).
