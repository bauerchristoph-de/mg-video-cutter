# Zweite Engine: Remotion

Die ffmpeg-Pipeline in `scripts/` ist und bleibt der **Standard**. Remotion ist
die zweite Engine für die Fälle, in denen ffmpeg strukturell schlechter ist —
nicht der Nachfolger.

Remotion baut Videos als React-Komponenten: jeder Frame wird aus Code gerendert,
`useCurrentFrame()` liefert die Framenummer, Animationen sind Funktionen der
Zeit. Der Unterschied zur bestehenden Pipeline ist nicht die Optik, sondern das
Modell — statt Overlays auf ein fertiges Video zu legen, wird das Bild pro Frame
komplett neu gezeichnet.

---

## 0 · Lizenz-Gate — VOR jedem Vorschlag klären

**Remotion ist nicht bedingungslos kostenlos.** Der Video-Cutter ist ein
verkauftes Produkt; ein Kunde, der wegen unserer Empfehlung lizenzpflichtig wird,
ohne es zu wissen, ist ein Produktfehler.

Stand der offiziellen Lizenz-FAQ (remotion.dev/docs/license/faq):

| Wer | Kostenlos? |
|---|---|
| Einzelperson, auch kommerziell | ja |
| Organisation/Team bis **3 Personen** | ja |
| Organisation ab **4 Personen** | **nein** — Company License nötig |
| Non-Profits, Evaluierung | ja |

Wichtig für unser Modell: Wenn **wir** das Remotion-Projekt betreiben und der
Kunde den Code nie erhält, nie ausführt und keinen Zugriff hat, zählt nur unsere
eigene Kopfzahl. Sobald der Kunde das Projekt selbst besitzt oder betreibt — und
genau das ist die Regel bei diesem Plugin, es läuft beim Kunden lokal —
**zählen beide Organisationen zusammen** auf die 4-Personen-Schwelle.

Preise laut derselben Quelle: „Remotion for Creators" 25 $ pro Seat und Monat,
„Remotion for Automators" 0,01 $ pro Render bei 100 $ Mindestumsatz pro Monat.

**Verbindlicher Ablauf:**

1. Remotion nie ungefragt einrichten. Erst prüfen, ob der Fall ihn wirklich
   braucht (Abschnitt 1) — in den meisten Fällen tut er das nicht.
2. Braucht er ihn: dem Kunden die Schwelle **in einem Satz** nennen, bevor
   irgendetwas installiert wird. Wörtlich brauchbar: „Für den Preview-Modus
   würden wir Remotion einsetzen — das ist bis drei Personen im Unternehmen
   kostenlos, ab vier braucht ihr eine eigene Lizenz. Soll ich das so aufsetzen
   oder bleiben wir bei der Standard-Pipeline?"
3. Antwort in `kunden-config.yaml` festhalten:
   ```yaml
   engine:
     remotion_erlaubt: false      # true erst nach ausdrücklicher Kundenfreigabe
     lizenz_geklaert_am: null     # Datum der Freigabe
     personen_im_unternehmen: null
   ```
4. Steht dort `false` oder `null`, wird **ausschließlich** mit der
   ffmpeg-Pipeline gearbeitet — auch dann, wenn Remotion technisch besser passen
   würde. Die Lizenzfrage wird nicht stillschweigend übergangen.

Die Lizenzbedingungen können sich ändern. Vor der ersten Einrichtung bei einem
neuen Kunden die FAQ einmal live prüfen, statt diese Tabelle zu zitieren.

---

## 1 · Wann welche Engine

| Fall | Engine | Begründung |
|---|---|---|
| Talking-Head-Reel, Standardfall | **ffmpeg** | schneller, keine Lizenzfrage, erprobt |
| Webinar-Longform mit Captions | **ffmpeg** | dito |
| Event-/Action-Schnitt | **ffmpeg** | dito |
| Kunde will vor dem Render sehen und mitentscheiden | **Remotion** | Studio/Player zeigt sofort, ffmpeg braucht 2–5 min pro Videominute |
| Viele Varianten aus einem Datensatz (10+ Ads mit gleichem Layout, getauschtem Text/Preis/Motiv) | **Remotion** | eine Komposition, n Props — in ffmpeg n Generatorläufe |
| Bewegte Info-Grafik, Zahlen-Animation, animierte Charts | **Remotion** | in ffmpeg nur als vorgerenderte PNG-Sequenz |
| Sehr lange Timeline mit vielen Segmentgrenzen | **Remotion** | löst die AAC-Priming-Drift strukturell (Abschnitt 6) |
| Kunde hat 4+ Mitarbeiter und keine Lizenz | **ffmpeg** | Lizenz-Gate, ohne Ausnahme |
| Schwache Kundenhardware, kein Node | **ffmpeg** | Remotion rendert über Headless-Chrome |

**Im Zweifel ffmpeg.** Die Engine zu wechseln ist eine Entscheidung mit
Folgekosten (Node-Umgebung, Lizenz, zweite Fehlerquelle), nicht eine
Geschmacksfrage.

---

## 2 · Was auch mit Remotion bei ffmpeg bleibt

Remotion hat **kein Loudness-Handling** — kein LUFS, kein True Peak, keinen
Limiter, keinen dokumentierten Mixdown-Algorithmus. Die komplette Master-Kette
aus `audio.md` bleibt unverändert und läuft **nach** dem Remotion-Render:

1. Remotion rendert das Bild inklusive Overlays und O-Ton.
2. Audio extrahieren, Master-Kette fahren (Highpass → Kompressor → SFX-Mix →
   lineare Normalisierung auf −14 LUFS, Limiter auf −1,2 dBTP).
3. Gemasterten Ton unter das Remotion-Video muxen.
4. `scripts/qc.py` wie immer — **alle** Gates gelten unverändert.

Ebenfalls bei ffmpeg/Python: Onset-Audit gegen die RMS-Hüllkurve, Freeze-Scan,
A/V-Dauer-Abgleich, SFX-Synthese, Kontrast-Messung, `pausen_scan.py`, alle
Inhalts-Gates. Remotion ersetzt davon nichts.

ffmpeg und ffprobe liegen Remotion bei (`npx remotion ffmpeg`,
`npx remotion ffprobe`) — beim Kunden muss dafür also nichts zusätzlich
installiert werden.

---

## 3 · Setup

```bash
npx create-video@latest --yes --blank --no-tailwind kunde-video
cd kunde-video
npm i
npx remotion add @remotion/captions @remotion/media @remotion/layout-utils
```

- Assets kommen nach `public/` und werden mit `staticFile("name.mp4")`
  referenziert. **`public/` nie in einen OneDrive-/Dropbox-Ordner legen** — die
  bekannten stillen Lese-Stalls treffen hier härter als bei ffmpeg, weil der
  Render dann hängt statt zu scheitern.
- **Alle `@remotion/*`-Pakete müssen exakt dieselbe Version haben**, plus eine
  dazu kompatible `mediabunny`-Version. Deshalb immer `npx remotion add <paket>`
  statt `npm i <paket>` — `add` wählt die passende Version. Upgrade nur über
  `npx remotion upgrade`, Kontrolle mit `npx remotion versions`.

---

## 4 · Untertitel: das Token-Modell

Remotion bringt für Untertitel ein typisiertes Format mit, das exakt unser
Karaoke-Modell trifft:

```ts
type Caption = {
  text: string;
  startMs: number;
  endMs: number;
  timestampMs: number | null;
  confidence: number | null;
  pageBreakAfter?: boolean;
};
```

Karten entstehen mit `createTikTokStyleCaptions({ captions, combineTokensWithinMilliseconds })`,
das aktive Wort ergibt sich pro Frame aus:

```tsx
const isActive = token.fromMs <= absoluteTimeMs && token.toMs > absoluteTimeMs;
```

**Das ist unsere halboffene Intervall-Regel, eingebaut** — `<=` auf der Unter-,
`>` auf der Obergrenze. Die ganze Fehlerklasse „Doppel-Highlight am Grenzframe /
Leerframe beim Zeilenwechsel" existiert in dieser Engine nicht mehr, weil jeder
Frame genau einmal ausgewertet wird.

**Was trotzdem von uns kommen muss** — Remotion liefert das nicht:

- **Wort-Timings nach Onset-Audit**, nicht roh aus Whisper. Der Import ist
  derselbe wie bei der ffmpeg-Pipeline: das korrigierte `words`-Array aus dem
  `cut-plan.json` nach `Caption[]` umrechnen (`s`/`e` in Sekunden → `startMs`/
  `endMs`), nicht Remotions eigenen Transkriptionsweg nutzen.
- **Anzeige-Vorlauf 0,10 s**: beim Umrechnen auf `startMs` abziehen, wie in der
  ffmpeg-Pipeline. Er steckt nicht im Format.
- **Alle Werte aus `captions.md`**: Off-White `#F0F0F0`, schwerster Schnitt,
  Schatten Blur 7 / Alpha 0,72 / dy 4, Chip-Padding 13/7, Radius 11, max. 3
  Wörter pro Karte, max. 860 px Zeilenbreite im 1080er-Raster.
- **Die Ink-Box-Regel.** Remotions `measureText()` liefert `{ width, height }`;
  **es ist nicht dokumentiert, ob `height` die Ink-Box oder die Ascender-Box
  ist.** Nicht annehmen, dass das Problem gelöst ist: Chip-Position einmal an
  einem Referenzstring („Hg") gegenprüfen, bevor die erste Karte rausgeht.

**Zwei Pflicht-Absicherungen beim Messen:**

```tsx
const { fontFamily, waitUntilDone } = loadFont("normal", { weights: ["800"], subsets: ["latin"] });
await waitUntilDone();                       // erst danach messen
measureText({ text, fontFamily, fontSize, letterSpacing, validateFontIsLoaded: true });
```

Ohne `waitUntilDone()` wird gegen den Fallback-Font gemessen — die Chips sitzen
dann systematisch falsch, und kein Timing-Gate schlägt an. `validateFontIsLoaded:
true` macht aus dem stillen Fehler einen lauten. Und: **`letterSpacing` muss beim
Messen und beim Rendern identisch gesetzt sein**; es wird beim Messen fast immer
vergessen und verschiebt jede Chip-Breite.

---

## 5 · Vorschau in den Freigabeschleifen — mit ehrlicher Einschränkung

Das ist der Hauptgrund, diese Engine überhaupt zu haben: Der Kunde sieht das
Ergebnis sofort statt nach 2–5 Minuten Renderzeit pro Videominute.

```bash
npx remotion studio --no-open     # gibt die URL aus, Direktsprung über /<composition-id>
```

Das Studio kann laut Doku: Elemente per Klick selektieren, verschieben,
skalieren, drehen, CSS-Styles sowie Keyframes und Easing-Werte editieren — und
schreibt Änderungen in den Quellcode zurück. Mit einem Zod-Schema an der
Komposition wird zusätzlich jeder Parameter in der Sidebar editierbar,
Farbfelder über `zColor()` als echter Color-Picker.

**Die Einschränkung, die niemand überspringen darf:** Diese Interaktivität ist
nicht automatisch da, sie hängt an der Code-Struktur. Wörtlich aus der Doku:
*„If the markup is too complex for the Studio to make it interactive, then the
values become grayed out."* Konkret verlangt sie hartkodierte Werte, inline
`interpolate()`-Aufrufe, inline Style-Objekte, keine ausgelagerten Konstanten —
und **keine per `.map()` erzeugten Clips**.

Das steht in direktem Widerspruch zu generiertem Code. Deshalb die Festlegung:

- **Freigabe-Vorschau für den Kunden:** hartkodiertes JSX generieren (der
  Generator schreibt die Zahlen aus, statt sie zur Laufzeit zu rechnen). Dann
  funktioniert das Direct-Manipulation-Editing, und der Kunde kann eine
  Textposition selbst korrigieren, statt sie zu beschreiben.
- **Varianten-Produktion:** `.map()` und berechnete Werte sind richtig, die
  Studio-Interaktivität wird bewusst aufgegeben. Der Kunde bekommt dann den
  Props-Editor und die Wiedergabe, nicht das Klick-Editing.
- **Beides gleichzeitig geht nicht.** Vor dem Aufsetzen entscheiden, welcher der
  beiden Modi der Fall ist, und es dem Kunden sagen.

Für eine reine Vorschau im Browser (ohne Editing) reicht `@remotion/player`.
Wichtig dabei: Der Player wertet `calculateMetadata()` **nicht** automatisch aus
— bei variabler Videolänge muss `durationInFrames` selbst berechnet und übergeben
werden, sonst schneidet die Vorschau das Ende ab.

---

## 6 · Was Remotion strukturell besser löst

**Die AAC-Priming-Drift.** In der ffmpeg-Pipeline addiert jede Segmentgrenze
10–27 ms auf, kumulativ bis 0,5–0,8 s pro 100 s; `audio.md` löst das mit der
aufwendigen WAV-Zwischenstufe. In Remotion existiert das Problem nicht: die
Segmente sind `<Sequence>`-Bereiche **innerhalb einer** Komposition, es gibt
keine Per-Segment-Container, deren Padding sich summiert. Bei sehr langen
Timelines mit vielen Schnitten ist das ein echtes Argument.

**Datengetriebene Varianten.** Eine Komposition, ein Zod-Schema, n Props-Objekte.
`calculateMetadata()` rechnet die Dauer aus den Daten und setzt pro Variante den
Ausgabenamen:

```tsx
const calculateMetadata: CalculateMetadataFunction<Props> = async ({ props }) => {
  const sekunden = await getVideoDuration(props.videoSrc);
  return {
    durationInFrames: Math.ceil(sekunden * 30),
    defaultOutName: `ad-${props.variante}`,
  };
};
```

`Math.ceil` — Dauern immer aufrunden, sonst fehlt am Ende ein Teilframe.

---

## 7 · Rendern

```bash
npx remotion render <composition-id> out/video.mp4
npx remotion still  <composition-id> --frame=30 --scale=0.25   # schneller Layout-Check
```

`--frame` ist **nullbasiert**: bei 30 fps ist `--frame=30` die 1-Sekunden-Marke.

**Pflichtflags, sobald Effekte im Spiel sind** (Blur, Glow, Light-Leak, alles
WebGL2-basierte):

```bash
npx remotion render <composition-id> out/video.mp4 --gl=angle --concurrency=1 --timeout=180000
```

Ohne `--gl=angle` meldet der Render „WebGL2 unavailable" oder fällt still auf
Software-Rendering zurück. `--concurrency=1` ist bei WebGL-Inhalten kein
Geschwindigkeits-, sondern ein Stabilitätsparameter.

Alternativ dauerhaft in `remotion.config.ts` (Studio danach neu starten):

```ts
import { Config } from "@remotion/cli/config";
Config.setChromiumOpenGlRenderer("angle");
```

CRF, Bitrate und Frame-Bereiche stehen nicht in der Plugin-Doku — bei Bedarf
`https://www.remotion.dev/docs/cli/render.md` abrufen (an jede Remotion-Doku-URL
`.md` anhängen ergibt den Markdown-Quelltext).

---

## 8 · Bekannte Fallen

- **Headless-Chrome ist die Laufzeit.** Alle GPU-Eigenheiten des Kundenrechners
  schlagen durch. Deterministisch wie ffmpeg ist das nicht.
- **CSS `transition`, CSS `animation` und Tailwind-`animate-*`/`transition-*`
  rendern nicht korrekt.** Jede Animation läuft über `useCurrentFrame()`.
- **`toneFrequency` (Pitch) wirkt nur beim serverseitigen Rendern**, nicht im
  Studio und nicht im Player — die Vorschau klingt anders als das Ergebnis.
- **Zwei Trim-Semantiken nebeneinander:** in Remotion sind `trimBefore`/
  `trimAfter` **Frames** und nicht-destruktiv; die ffmpeg-CLI schneidet mit
  Zeitangaben und **muss re-encodieren** (`-c:v libx264 -c:a aac`), sonst stehen
  eingefrorene Frames am Anfang. Beim Nebeneinanderbetrieb leicht zu verwechseln.
  (Die Remotion-Doku behauptet an einer Stelle „values are in seconds" — das ist
  ein Doku-Fehler, der Code daneben rechnet mit Frames.)
- **`<AnimatedImage>` läuft nur in Chrome und Firefox** — betrifft die
  Player-Vorschau beim Kunden.
- **`<HtmlInCanvas>` braucht Chrome 149+ mit gesetztem Flag** und ist für
  Kundenbetrieb nicht einsetzbar.
- **Änderungen an `remotion.config.ts` erfordern einen Studio-Neustart** —
  während einer Live-Freigabe mit dem Kunden am Bildschirm merkbar.
- **Die Plugin-Doku nennt keine Node-Mindestversion und beschreibt den
  Chrome-Download nicht.** Beim ersten Setup auf einem Kundenrechner Zeit
  einplanen und nicht in einen Kundentermin legen.

---

## 9 · Der Vertrag mit der Standard-Engine

Ein mit Remotion gebautes Video muss dieselben Werte einhalten wie ein
ffmpeg-Video. Die sechs verbindlichen Größen stehen in `animation-kurven.md`
Abschnitt 5 (Overshoot 8,0 % · Pop 0,20 s / Exit 0,15 s · Vorlauf 0,10 s ·
SFX auf Peak + 0,04 s · Zoomstufen 100/112/125 · max. 3 Emphasis pro Minute).
Sie gehören beim Engine-Wechsel ausdrücklich ins Standards-Echo.
