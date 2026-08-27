# Hook-Overlays — der Titel, der zum Bleiben zwingt

Der Hook ist die Text-Einblendung in den ersten Sekunden. Er entscheidet über die Hold-Rate —
und er ist die Stelle, an der „automatisch generiert" am schnellsten auffällt. Zwei Fehlerbilder
aus echten Builds, beide vom Kunden reklamiert: (1) Hook als zentrierte weiße Sticker-Box →
wirkt wie ein UI-Element, „corporate statt Instagram". (2) Hook in der oberen Bildmitte →
liegt im 9:16-Crop mitten auf dem Gesicht.

## Stil (Creator-Standard)

- **Gleiche Typografie wie die Untertitel** — derselbe Font, derselbe schwerste Schnitt, dasselbe
  Off-White, derselbe Schatten. Der Hook hat KEINE eigene Design-Sprache; genau das macht ihn
  „typisch Instagram".
- Fette VERSALIEN, max. 2 Zeilen, kurz („WANN SOLLTEST DU DIE SECURITY HOLEN?").
- **Ein Keyword auf Akzent-Chip** (gleiche Chip-Logik wie Karaoke) — nicht mehr.
- Weicher Schatten statt Box; keine weißen iOS-Sticker-Boxen, keine Rahmen.
- Einsatz mit Pop-In (gleiche Snap-Pop-Mechanik wie Emphasis, dezenter skaliert).

## Position

- **Reaction-/Split-Screen-Format:** Der Hook sitzt AN DER NAHT zwischen den beiden Videos —
  das ist die Dead Zone, und es ist die Konvention, die Zuschauer aus dem Format kennen.
  Nie in die obere Bildmitte (dort sitzt im 9:16-Crop das Gesicht des oberen Sprechers).
- **Talking-Head 9:16:** obere Zone, aber unterhalb der Plattform-UI (oben 250 px meiden) und
  NIE über dem Gesicht — vor dem Render einen Frame prüfen. Liegt das Gesicht hoch, Hook auf
  Brusthöhe unterhalb des Kinns.
- Kontrast-Gate aus `captions.md` gilt auch für den Hook (heller Hintergrund → Scrim/Position).

## Copy

- Hook-Text kommt aus dem `marken-profil.md` (Hook-Muster des Kunden) oder wird dem Kunden als
  2–3 Varianten zur Wahl gestellt — nie ungefragt eine „neutrale" Formulierung setzen.
- Frage-Hooks und offene Loops schlagen Aussagen; konkrete Zahl schlägt runde Formulierung.
- Kunden-Hook-Templates (falls im Kundenordner vorhanden) sind verbindliche Presets.
