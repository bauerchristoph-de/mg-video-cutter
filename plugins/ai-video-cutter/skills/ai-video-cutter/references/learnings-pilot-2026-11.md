# Allgemeine Learnings aus dem Pilot-Reel (Webinar-Handyaufnahme, 17.11.2026)

Gesammelt aus vier Feedback-Runden (v1→v4). Gilt für jeden Kunden.

## Schnitt / Luft am Satzende
- Sprachenden **messen**, nicht aus Whisper-Wortzeiten ableiten: Whisper-End liegt oft 0,2–0,4 s vor dem echten Ende (Silbe „…gearbeitet habe“ wurde abgeschnitten).
- Verfahren: 30-ms-RMS-Hüllkurve, Schwelle = max(0,010; 0,10 × P90), Energie muss 0,12 s anhalten → Sprachende. Danach **mindestens 0,24 s Luft**, auf ein Energietal einrasten.
- Letztes Segment: zusätzlich +0,25 s und 0,35 s Audio-Fade-out (sonst wirkt das Reel-Ende abgeschnitten).
- Schnittstarts per Tal-Suche (−0,2 s … +0,03 s) vor dem Wortanfang.
- Überlappende Quellbereiche aufeinanderfolgender Segmente zusammenführen (sonst Wiederholung von 0,2–0,4 s Material).
- Semantik: nach Aufzählungen, vor Pointen und bei Sätzen, die in der Luft hängen, mehr Luft lassen.

## Farbe
- Gelbstich kommt bei Handy-/Indoor-Material meist aus **Haut und Wänden**, nicht aus Weißflächen: nicht am Hemd neutralisieren, an Haut-Verhältnissen messen (G/R ≈ 0,70–0,75, B/R ≈ 0,55–0,60 war zu orange; Ziel B/R > 0,60).
- Rezept (ffmpeg): `curves` (leichter S-Kontrast, Schwarz bei 0,012), `colortemperature=5900`, `colorbalance` (Mitten/Lichter Richtung Blau), `selectivecolor` (Weiß/Gelb/Rot Gelb-Anteil senken), danach `vignette`/`unsharp` dosiert.
- Farbkorrektur immer ungefragt, immer vor dem Render messen.

## Sound-Design
- Subtil heißt: **Peak ≈ −29 dBFS** für Ticks/Swishes, Thud 44–80 Hz nur am Hook, keine Riser, nichts Tonales.
- High-Pass 80–100 Hz, lieber schneiden als boosten, SFX-Peak auf den Bild-Impact legen, Crossfades 100–500 ms.
- Kundenwort „kindlich/zu viel“ = Pegel runter und Anzahl halbieren, nicht Klangfarbe tauschen.

## Layout
- Webinar-Aufnahmen: Sprecher groß in der oberen Bildhälfte, Visualisierung in der unteren. Keine Folien einblenden — alles als eigene Animation.
- Hook = Highlight-Satz oder Sprecher groß, nie eine Folie.
