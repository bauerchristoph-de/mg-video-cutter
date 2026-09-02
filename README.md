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

- **0.9.0** (02.09.2026) — Der Skill steht wieder vollständig auf der eigenen ffmpeg-Pipeline: die optionale zweite Render-Engine ist entfernt, alle Regeln und Werte gelten unverändert weiter.
- **0.8.0** (02.09.2026) — Neues Gate für die wichtigste Regel des Systems: `pausen_scan.py` misst die Sprechpausen adaptiv (Rauschschwelle aus dem Material statt Konstante) und prüft jeden geplanten Schnitt dagegen — verschluckte Silben fallen jetzt vor dem Build auf, nicht beim Ansehen. Neue Referenzen: `animation-kurven.md` (alle Animationswerte als prüfbare Zahlen statt Prosa — Overshoot, Peak-Lage, Frame-Rundung, wahrnehmungsgerechte Skalierung), `loesungsbibliothek.md` (Einstieg über den Fall statt über die Dateiliste). QC erweitert um Abschnitt D (Gates 21–23).
- **0.4.1** (24.08.2026) — Interop: geteilter Kundenordner mit dem AI Post-Generator (kunden-config.yaml, marken-profil.md, assets/, fertig/).
- **0.4.0** (24.08.2026) — Erstes Release: Setup-Interview, Marken-Analyse (Texte + Videos), Karaoke-/Emphasis-Caption-System, Schnitt-/Audio-/Render-Regeln, QC-Gates, Learnings-System, Begleit-Content (Caption pro Kanal).
