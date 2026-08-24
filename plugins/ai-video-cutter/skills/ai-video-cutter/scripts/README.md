# Scripts — Stand v0.1

Noch leer — bewusst. Die validierte Referenz-Implementierung ist `build_cut.py` aus dem Mehr-Geschäft-Webinar-Projekt (Kunden\Mehr Geschäft\2026-08 Webinar). Sie enthält bereits alle Regeln aus den references (halboffene Enables, ONSET_FIX mit asserts, Emphasis-Renderer ohne Underline, events.json-Export, Zeilenwechsel-Handoff).

**Nächster Schritt für v0.2 (vor dem Pilotkunden):** build_cut.py generalisieren zu
- `build.py` — liest `kunden-config.yaml` + `schnittplan.yaml` (SEGS, Emphasis, Format) statt hartkodierter Werte
- `make_sfx.py` — SFX-Synthese aus events.json (Pop/Boom/Whoosh, Planned→Container-Remap)
- `qc.py` — alle QC-Gates aus render-technik.md als ein Aufruf (Freeze, A/V-Länge, Loudness, Sub-Kontiguität, Ton-Sync, SFX-Sync)
- `onset_audit.py` — Hüllkurven-Export + Wort-Onset-Prüfung mit Report

Erst generalisieren, wenn der Entwurf inhaltlich festgemacht ist — sonst zweimal Arbeit.
