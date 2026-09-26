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
- **Satzschreibung statt Versalien** (Standard seit 0.12.0, Kunden-Feedback 09/2026: „cooler, nicht all caps"): fett, max. 2 Zeilen, kurz („Wann solltest du die Security holen?"). Versalien nur, wenn die Kunden-CI sie ausdrücklich verlangt.
- **Clean-Standard: Akzentfarbe NUR auf dem aktiven Untertitel-Wort.** Hook, Zwischenhook, Teaser und Emphasis sind weiß mit Schicht-Schatten, ohne Chip. Ein Keyword-Chip im Hook nur, wenn die Kunden-Config es will (`hook.keyword`) — sonst wirkt das Video bunt statt hochwertig.
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

## Serien-Teaser & CTA am Ende (Learnings 25.09.2026)

Kunden-Feedback: ein nacktes „TEIL 2" am Ende ist zu wenig — der Zuschauer braucht eine Handlung.
Recherche (fluxnote, influencers-time, clipcreator): Serien-CTA mit **Handlung + konkretem Nutzen**
schlägt generisches „Folge mir"; in den letzten 3–5 s; 5–7 Wörter; als Text (läuft stumm).

- **Formel:** `FOLGE FÜR TEIL <n>: <Thema des nächsten Teils>` — Chip auf **FOLGE** (die Handlung),
  z. B. „FOLGE FÜR TEIL 2: AUS GIPS WIRD 3D".
- **Einsatz** mit dem letzten gesprochenen Überleitungssatz („Das zeige ich euch jetzt auch"),
  Stil und Position wie der Hook (oben, gleiche Typografie).
- **Outro-Vorschau:** 1–2 s stummes B-Roll aus dem NÄCHSTEN Teil unter dem CTA (Musik im Outro
  +6…9 dB hochziehen), damit der CTA ≥ 2 s stehen bleibt, ohne dass die Person schweigend in die
  Kamera schaut.
- Der nächste Teil beantwortet den offenen Loop in den ersten 5 s und bringt in den ersten 3 s
  Kontext („Teil 2 · Implantat-Serie"), damit er auch allein funktioniert.
