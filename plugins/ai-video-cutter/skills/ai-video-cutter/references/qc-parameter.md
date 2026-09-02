# QC — alle Parameter am Ende

Die Qualitätskontrolle ist kein Blick aufs Ergebnis, sondern eine **vollständige
Parameterprüfung**. Jedes Video läuft am Ende durch dieselbe Liste — technisch,
inhaltlich, markenbezogen, rechtlich. Kein Video geht raus, bevor alle Gates stehen.

`scripts/qc.py` prüft die maschinellen Gates und beendet sich mit Fehlercode, wenn eines
reißt. Die Gates mit dem Vermerk **Auge** kann kein Skript ersetzen.

```bash
python3 scripts/qc.py --video final.mp4 --build build/ --plan cut-plan.json \
        --config kunden-config.yaml --format reel
```

Ohne `--config` laufen die technischen Gates plus die beiden Zahlen-Gates — die brauchen
keine Config. Es fehlen dann Glossar, Pflichtphrasen, CTA-Kanaltreue, Sprechtempo und
Formatvorgaben. **Die Config gehört immer mit dazu.**

---

## A · Technik

| # | Parameter | Sollwert | Messung | Bei Abweichung |
|---|---|---|---|---|
| 1 | A/V-Dauer | Δ < 0,1 s | `ffprobe` beide Streams | Stopp |
| 2 | Freeze-Scan | 0 Treffer | `freezedetect=n=-60dB:d=0.5` | Stopp |
| 3 | Loudness | −14 LUFS ±0,5 | `ebur128` | Auto-Korrektur |
| 4 | True Peak | ≤ −1,2 dBTP | `ebur128 peak=true` | Auto-Korrektur |
| 5 | Sprach-Lautheit über Fremdquellen | ≤ 2 dB Differenz | pro Quelle messen | Stopp |
| 6 | Auflösung | laut `formate.<format>.aufloesung` | `ffprobe` | Stopp |
| 7 | Laufzeit | in `ziel_dauer_s` | `ffprobe` | Stopp |

## B · Untertitel und Bild

| # | Parameter | Sollwert | Messung | Bei Abweichung |
|---|---|---|---|---|
| 8 | Karten-Kontinuität | keine Mikro-Lücke < 0,2 s, keine Überlappung | Kartenliste | Stopp |
| 9 | Vollständigkeit | jedes Transkript-Wort sichtbar | Abgleich Plan ↔ Karten | Stopp |
| 10 | Onset-Genauigkeit | 3–5 Stichproben nach Pausen | gegen RMS-Hüllkurve | Stopp |
| 11 | Lesbarkeit | Textzone nicht durchgehend hell ohne Scrim | `signalstats` YAVG + **Auge** | Stopp |
| 12 | Kollision | kein Text über Gesicht, Händen, Logo, Bildschrift | **Auge** (Kontaktbogen) | Stopp |
| 13 | SFX-Peaks | auf Animations-Onsets | `make_sfx.py --check` | Stopp |

## C · Inhalt — hier entstehen die teuren Fehler

| # | Parameter | Sollwert | Messung | Bei Abweichung |
|---|---|---|---|---|
| 14 | **Zahlen-Rechenprüfung** | jede Prozentrechnung geht auf | `rechen_pruefung()` | Stopp |
| 15 | **Zahlen-Deckung** | jede angezeigte Zahl wurde gesprochen | Mengenabgleich | Stopp |
| 16 | **Glossar** | kein bekannter Transkriptionsfehler im Endtext | Fehlerliste aus der Config | Stopp |
| 17 | **Pflichtphrasen** | rechtliche Weichmacher überlebt | Config `pflicht_phrasen` | Stopp |
| 18 | CTA-Kanaltreue | Longform mit, Reel ohne CTA-Block | Config `cta_marker` | Stopp |
| 19 | Sprechtempo | Profil-WPM ± Toleranz | Wörter / Laufzeit | Warnung |
| 20 | Regie-Kommentare | keine im Schnitt verblieben | **Auge** + Suchliste | Warnung |

## D · Schnitt und Animation (seit v0.8.0)

| # | Parameter | Sollwert | Messung | Bei Abweichung |
|---|---|---|---|---|
| 21 | **Schnitt in der Sprechpause** | jeder Cut im erlaubten Fenster | `pausen_scan.py --plan` | Stopp |
| 22 | Font-Identität | gemessen == gerendert, kein Fallback-Font | `build.py` (Assert) | Stopp |
| 23 | Engine-Vertragswerte | die sechs Werte aus `animation-kurven.md` §5 | Standards-Echo | Stopp |

**Zu 21 — warum das ein eigenes Gate wurde.** „Schnitte gehören in die
Sprechpause" ist die wichtigste Regel des Systems und war bis v0.8.0 die einzige
zentrale Regel ohne maschinelle Prüfung. Verschluckte Silben („Zweitens" →
„weitens") fielen deshalb erst beim Ansehen des fertigen Renders auf — also nach
dem teuersten Schritt. Der Scan misst die Rauschschwelle des Materials selbst
(`loudnorm input_thresh` → `silencedetect`), funktioniert damit auch bei leisen
Aufnahmen, und läuft zweimal: einmal **vor** dem Schnittplan als Vorschlagsliste,
einmal **nach** dem Schnittplan als Gate.

Bei getrimmten Schnitten mit `--vorlauf 0.25` fahren: Plosive (D, Z, K, B)
beginnen real bis 0,2 s vor dem Whisper-Onset.

**Zu 22.** Ein still auf einen Ersatz-Font zurückgefallener Text wird gegen
falsche Metriken vermessen. Die Chips sitzen dann systematisch daneben, das Video
besteht jedes Timing-Gate und sieht trotzdem falsch aus. Der Ladefehler muss laut
scheitern.

**Zu 23.** Wird für ein Video die zweite Engine benutzt (`engine-remotion.md`),
müssen die sechs Vertragswerte im Standards-Echo ausdrücklich genannt werden —
sonst wird die Engine-Wahl unbemerkt zur Stil-Änderung.

---

## Warum die Zahlenprüfung nicht über die Konfidenz läuft

Der naheliegende Ansatz — „markiere alle Zahlen, bei denen Whisper unsicher war" —
**funktioniert nicht.** Nachgemessen an 117 Zahl-Tokens aus 10 Videos:

| Falsche Zahl | Whisper-Konfidenz |
|---|---|
| `2046` (richtig 2.640) | **0,943** |
| `1056` in derselben Rechnung | **0,972** |
| `84` (richtig 480) | **0,983** |
| `888` (richtig 168) | 0,417 |
| `230` (richtig 2030) | 0,622 |

Whisper vertippt sich **hochkonfident**. Nur 3 von 10 bekannten Fehlern lagen unter 0,7 —
während korrekte Zahlen regelmäßig bei 0,42 bis 0,65 liegen. Ein Konfidenz-Gate würde die
meisten Fehler durchlassen und dabei richtige Zahlen anschlagen.

**Was funktioniert, ist die Arithmetik.** 2046 × 40 % = 818, gesagt wurde 1056 — also war
die Basis 2640. Die Rechnung deckt den Fehler auf, den die Konfidenz verschweigt.

Gemessen an denselben 10 Videos: **4 Treffer, alle mit echten Fehlern, keine Fehlalarme.**
Zwei korrekte Rechnungen wurden als stimmig bestätigt, vier Videos ohne Rechnung
übersprungen.

Damit rhetorische Prozentangaben („zu 100 Prozent zufrieden") nicht anschlagen, prüft das
Gate nur dort, wo neben der Prozentangabe **mindestens zwei verschiedene Zahlen** stehen —
also eine Rechnung überhaupt vorhanden sein kann.

### Drei Rechenformen, nicht eine

Die erste Fassung prüfte nur den Anteil (`Basis × p/100`). Die Negativkontrolle am
31.08.2026 zeigte, dass das bei jedem Zuschlag und jeder Steigerung falsch anschlägt:

| Satz | erste Fassung |
|---|---|
| „25 % Zuschlag auf 32 Euro, also 40 Euro" | **Fehlalarm** (32 × 1,25 = 40) |
| „stieg um 30 %, von 120 auf 156" | **Fehlalarm** (120 × 1,3 = 156) |

Ein Gate, das bei einem Sicherheitsdienst jeden Nachtzuschlag anschlägt, wird nach dem
zweiten Video abgeschaltet. Deshalb gelten drei Formen als stimmig:

```
Anteil     Basis × p/100          „40 % von 3000 sind 1200"
Aufschlag  Basis × (1 + p/100)    „25 % Zuschlag auf 32 Euro, also 40 Euro"
Abschlag   Basis × (1 − p/100)    „30 % Rabatt auf 200 Euro, also 140 Euro"
```

Dazu eine Sperre gegen Scheintreffer: Basis und Ergebnis müssen sich messbar
unterscheiden. Ohne sie wäre bei kleinen Prozentsätzen `x ≈ x × (1 + p/100)` trivial
„stimmig" — real aufgetreten bei „0,24 Prozent … bis 230 … bis 230", wo das Gate dadurch
einen echten Fehler übersah.

**Nachgemessen nach der Korrektur: 0 Fehlalarme in 9 Kontrollsätzen aus drei Branchen,
0 Abweichungen bei den 10 echten Videos.**

---

## Was das Gate nicht kann

**Zahlendreher ohne Rechnung** bleiben unentdeckt. Sagt jemand „25.250 Euro
Bruttolistenpreis", wo 25.000 gemeint sind, und folgt keine Prozentrechnung darauf, sieht
das kein Skript. Solche Stellen gehen als Liste an den Kunden zurück — das ist ein eigener
Ausgabekanal des Prozesses, kein Fehlerfall.

**Der Kontaktbogen bleibt Pflicht.** Zahlen erkennen nicht, dass weiße Schrift auf einem
weißen Hemd liegt oder ein Untertitel über einem Logo steht.

---

## Config-Felder, die die Inhalts-Gates speisen

```yaml
glossar:
  fachbegriffe:  [ [ "Wertesabschaff", "Bewertungsabschlag" ] ]   # falsch -> richtig
  phrasen:       [ [ "damit du stolz warst", "damit du Steuern sparst" ] ]
  schutzliste:   [ Bilanzierer, Rückstellung ]                    # nie "korrigieren"

pflicht_phrasen: [ "in der Regel", "meine Erfahrung", "Steuerberater" ]
cta_marker:      [ "abonnieren", "Link in der Beschreibung" ]

sprechprofil:
  wpm_reel: 166
  wpm_longform: 158
  wpm_toleranz: 25

formate:
  reel:     { aufloesung: [1080, 1920], ziel_dauer_s: [45, 90],   hat_cta_block: false }
  longform: { aufloesung: [1920, 1080], ziel_dauer_s: [210, 420], hat_cta_block: true }
```

**Die Gates gelten unabhängig vom Freigabemodus.** Wird die manuelle Freigabe nach zehn
sauberen Durchläufen abgeschaltet, bleiben die maschinellen Gates an — sie sind der Ersatz
für das Augenpaar, nicht dessen Beifahrer.
