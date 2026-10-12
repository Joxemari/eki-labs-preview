# eki.labs · brand kit

Everything you need to put eki.labs on a page, a screen or a post: logos, colour, type and ready-made social formats. The full guidelines live at **ekilabs.com/brand**.

Version: October 2026 · Questions: hola@ekilabs.com

---

## What is inside

```
01-logo/
  logo/                     eki.labs: symbol and name, the everyday logo
  eki/                      eki.: the base of the name, on its own
  symbol/                   the sun over three rows, on its own
  symbol-small/             two rows, for 16–31 px (favicons, tiny icons); from 32 px, the symbol
  signature/                eki.labs and tagline, one block
  signature-vertical/       eki.labs and tagline, stacked
02-colour/              ASE (Adobe), CSS, JSON and a swatch card
03-type/                Zilla Slab, Work Sans and Geist Mono, with their licences
04-social/              avatars, LinkedIn, Instagram, YouTube, posts and the web preview image
```

Every logo comes in four colourways and three formats:

| Colourway | Use it on |
|---|---|
| `day` | light grounds: arena, piedra, white. The sun in its gradient; rows and letters in noche. **The main logo.** |
| `night` | dark grounds: noche, bosque, origen, photos with a veil. The sun in its gradient; rows and letters in arena. |
| `day-full` | option on light grounds: the whole symbol in the full gradient (orange, sol, yerba); letters in noche. |
| `night-full` | option on dark grounds: the whole symbol in the full gradient; letters in arena. |
| `black` | one-ink printing on light grounds (stamps, engraving, fax, forms) |
| `white` | one-ink on dark or saturated grounds |

| Format | Use it for |
|---|---|
| `.svg` | web, apps and any design tool. The first choice. |
| `.pdf` | print and documents (vector) |
| `.png` | slides, Office and anywhere SVG is not accepted. Transparent ground. |

All logo files are cropped tight to the artwork. The space around them is yours to keep (below).

---

## Logo rules

- **The symbol.** One circle: the sun above the horizon and three rows below. The sun goes from an orange crown `#FF8F00` to sol `#FFD54A` on the horizon, a nod to the first eki logo; the rows take the ink of the letters. As an option, the full gradient runs through the whole symbol, from orange through sol to yerba `#58E9AE` at the foot (`day-full`, `night-full`). The gradients live only in the logo and in the sun of the horizon: they are not palette colours.
- **The name.** «eki.» in Geist 600 and the second name in Geist 400, both in the ink of the logo: **eki.labs**. The kit has eki.labs and eki.; any other ending is built at ekilabs.com/brand/download, in the same curves.
- **Clear space.** Keep a quarter of the symbol's diameter free on every side.
- **Minimum size.** Full logo 96 px wide. Symbol 16 px. Below 32 px use `symbol-small`.
- **In text.** Always **eki.labs**, in lowercase, in the typeface of the text around it. Never capitalised, never set in capitals. Legal name: Eki Labs Corp.
- **Signature.** Logo and tagline travel together as one block. The tagline is always the same, «Farming soil & sun, together», and always the same size: as wide as the eki.labs logo, a quarter of the symbol below it, aligned left (or centred when stacked). The kit signs with eki.labs; the logo builder can add it to another ending when a piece needs it. eki. on its own goes without it. Never rebuild it with live text.
- **Never:** another colour or gradient for the sun · separating sun and rows · rotating the mark · placing it on yerba or on sol · shadows, glows or outlines · stretching or condensing.

---

## Colour

Four colours with a fixed meaning, four deep tones and a quiet base. Colour only where it means something.

| Token | HEX | RGB | Job |
|---|---|---|---|
| sol | `#FFD54A` | 255 213 74 | Energy. The key figure, and the horizon of the logo's sun gradient. Never a button or text. |
| yerba | `#58E9AE` | 88 233 174 | Crops, and actions on dark: the one colour you can press. |
| tierra | `#CF8166` | 207 129 102 | Land and rural life, on dark grounds. |
| noche | `#0A100C` | 10 16 12 | Ink, infrastructure and dark chapters. Our black. |
| yerba honda | `#056C4A` | 5 108 74 | Yerba as text and labels on light grounds. |
| tierra honda | `#964A2F` | 150 74 47 | Tierra as text and data on light grounds. |
| origen | `#311D16` | 49 29 22 | Deep ground for origins and farmers. |
| bosque | `#0A281A` | 10 40 26 | Deep green ground for food and crops. |
| arena | `#F4F2EC` | 244 242 236 | Page background: the open field. |
| piedra | `#EBE6D8` | 235 230 216 | Surfaces, cards and bands. |
| linea | `#D6D1C3` | 214 209 195 | Rules and borders on light grounds. |
| pizarra | `#555A52` | 85 90 82 | Secondary text on light grounds. |
| grafito | `#141B16` | 20 27 22 | Surfaces on dark grounds. |
| acero | `#2B332D` | 43 51 45 | Rules and borders on dark grounds. |
| niebla | `#A1A69F` | 161 166 159 | Secondary text on dark grounds. |
| blanco | `#FFFFFF` | 255 255 255 | Only inside other people's surfaces (email, documents). |

- Sol and yerba have almost the same lightness: never put them side by side. The one exception is the full gradient of the logo, where they meet as a blend, never as an edge.
- **Logo gradients** (logo and horizon sun only): the sun, `#FF8F00` → `#FFD54A`; the full gradient option, `#FF8F00` → `#FFD54A` → `#58E9AE`, top to bottom of the circle.
- Text on light grounds is noche; secondary text pizarra; green text yerba honda.
- `02-colour/eki-labs-colours.ase` loads the palette into Illustrator, InDesign and Photoshop (Swatches › Import).

---

## Type

| Family | Role | Weights |
|---|---|---|
| **Zilla Slab** | Headlines and the tagline | 400 (tight tracking, sentence case, full stop) |
| **Work Sans** | Text | 400 and 500 |
| **Geist Mono** | Data, figures and labels | 500 for labels in capitals with 8 % tracking; 400 for figures |

- The wordmark is drawn in Geist («eki.» in 600, the second name in 400) and lives only in the logo files and the logo builder: never retype it.
- All three are free under the SIL Open Font License (`OFL.txt` in each folder). Install them, or load them from Google Fonts on the web.
- In Office documents without these fonts, fall back to Georgia (headlines) and Arial (text).

---

## Social formats

`04-social/` has finished PNGs and the editable SVG of each one (live text, so install the fonts first; the SVGs open in Figma, Illustrator and Affinity). Sizes and safe areas per network are in `04-social/SIZES.md`.

| Folder | What |
|---|---|
| `avatars/` | The symbol for profile pictures: night (default) and day. 400, 800 and 1080 px. |
| `linkedin/` | Company page cover (1512 × 256) and a profile banner for the team (1584 × 396). |
| `instagram/` | Story (1080 × 1920). |
| `youtube/` | Channel banner (2560 × 1440) and video thumbnail (1280 × 720). |
| `posts/` | Feed templates for LinkedIn and Instagram: statement, figures and a carousel (cover and page), in 4:5 and 1:1. |
| `web/` | The link preview image (1200 × 630). |

How the templates work:

- **The landscape.** A horizon, the sun on it and the rows below: 2 px lines every 40 px (the 5 % rule). The sun sits to the right, like the end of the day, in the upper half of the logo's gradient: orange at the top, sol on the horizon.
- **One message per piece.** Eyebrow in Geist Mono capitals, headline in Zilla Slab, the logo small.
- **Figures always with their base:** «Versus conventional solar. Measured over one year in our field test in Zamora.»

---

## Licence

The logos, the symbol and the signature are eki.labs brand assets. Use them to refer to eki.labs, as they come in this kit, and not in ways that suggest a partnership or endorsement that does not exist. The fonts keep their own licence (SIL OFL 1.1).
