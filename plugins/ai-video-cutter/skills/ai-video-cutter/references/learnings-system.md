# Learnings-System — das Produkt verbessert sich mit jedem Video

Zwei Wissensebenen, strikt getrennt. Diese Trennung ist die Produkt-Architektur — nicht verhandelbar.

## Ebene 1: Plugin (allgemein — zentral gepflegt, für den Nutzer READ-ONLY)

Alles, was für JEDEN Kunden gilt: Schnitt-Regeln, Caption-System, Ton-Pipeline, Render-Technik, QC-Gates. Wird ausschließlich zentral im Plugin-Repository gepflegt und erreicht alle Kunden per Plugin-Update. **Niemals Plugin-Dateien lokal editieren oder kopieren-und-anpassen** — lokale Kopien veralten still und koppeln den Kunden von Verbesserungen ab.

## Ebene 2: Kundenordner (spezifisch — lebt beim Kunden)

Im Arbeitsordner des Kunden, **vom Skill beim ersten Einsatz automatisch angelegt** und bei JEDER Aktivierung gelesen (Pflicht-Lesereihenfolge im SKILL.md):

```
<kundenordner>/
├── kunden-config.yaml      # CI, Fonts, Kanäle, Intensität (Setup-Interview)
├── marken-profil.md        # angelernte Brand Voice (Marken-Analyse, references/marken-analyse.md)
├── kunden-learnings.md     # kundenspezifische Learnings, wächst mit jedem Video
├── assets/                 # Fonts, Logo
├── brand-referenz/         # 3-7 typische Kunden-Videos für die Stil-Analyse
├── rohmaterial/
├── fertig/
└── projekte/<video>/       # Transkripte, Schnittpläne, Builds pro Video
```

Fehlen diese Dateien beim Aktivieren des Skills: anlegen (Config über das Setup-Interview, `kunden-learnings.md` leer mit Kopfzeile). Nie ohne sie arbeiten.

**Interop mit anderen Paketen (z. B. AI Post-Generator):** `kunden-config.yaml`, `marken-profil.md`, `assets/` und `fertig/` sind GETEILTER Bestand — existieren sie bereits (von einem anderen Paket angelegt), übernehmen statt neu erheben; nie doppelt anlegen oder umbenennen. Änderungen an geteilten Dateien konservativ (ergänzen statt umbauen — das andere Paket liest mit). Learnings schreibt jedes Paket nur in seine eigene Datei (`kunden-learnings.md` gehört dem Video-Cutter).

## Der Abschluss-Ritus (Pflicht nach jedem gelieferten Video)

Nach der finalen Abnahme — nicht vorher, nicht überspringen:

1. **Feedback durchgehen:** Alle Korrekturen des Kunden aus den Feedbackrunden sammeln (auch scheinbar kleine: „Untertitel eine Idee höher", „weniger SFX").
2. **Kategorisieren — die eine entscheidende Frage: Gilt das nur für DIESEN Kunden oder für JEDEN?**
   - **Kundenspezifisch** (Geschmack, CI, Sprechweise dieses Sprechers, Kanal-Präferenzen) → in `kunden-learnings.md` anhängen, mit Datum und Ein-Satz-Kontext. Betrifft es einen Config-Wert (Intensität, Position, Farben, Caption-Stil) → direkt die `kunden-config.yaml` ändern, nicht nur notieren.
   - **Allgemeingültig** (ein Fehler, den das System bei jedem Kunden machen würde; eine Regel, die überall gilt) → NICHT in Kundendateien ablegen. Solche Beobachtungen gehören in die zentrale Plugin-Pflege; der Plugin-Betreiber sammelt sie im direkten Kontakt ein. Im Abschluss-Satz der Lieferung kurz benennen („Beobachtung fürs Grundsystem: …") — mehr nicht.
3. **Kunde sieht den Fortschritt:** Im Abschluss-Satz kurz nennen, was das System aus diesem Video für ihn gelernt hat („Ab jetzt weiß das System, dass eure Untertitel höher sitzen sollen"). Das macht den Wert des Systems sichtbar.

## Format der Einträge in kunden-learnings.md

```
## 2026-08-23 — Untertitel-Position
**Kontext:** Feedback nach Video 3 (Webinar-Ausschnitt)
**Learning:** Captions bei diesem Kunden auf 60 % Höhe statt 66 % — Logo-Einblendung unten kollidiert sonst.
**Umsetzung:** kunden-config.yaml band_9zu16 auf '58-62%' gesetzt.
```

Kompakt, konkret, mit Umsetzung. Ein Learning ohne Umsetzungsnotiz ist nur eine Beobachtung.

## Warum das wichtig ist

Ein Video-Cutter, der denselben Fehler zweimal macht, ist ein Tool. Einer, der nach jedem Video besser wird, ist ein System. Der Abschluss-Ritus ist der Mechanismus, der aus Feedbackrunden Produktwert macht.
