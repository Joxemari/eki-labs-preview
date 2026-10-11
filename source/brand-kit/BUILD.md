# Regenerar el kit de marca

El kit publicado vive en `site/brand/kit/`: `eki-labs-brand-kit.zip`, más un zip por parte (logos, colours, type, social). Las tarjetas de `/brand` muestran el tamaño de cada zip: si cambian, actualízalo en `site/brand/index.html`.

## Requisitos

- Python 3 con `pillow` y `cairosvg`: `pip install pillow cairosvg`.
- Node 18 o superior con Playwright: `npm i playwright`, y después `npx playwright install chromium`.
- Las fuentes de `fonts_dl/` instaladas en el sistema. Las plantillas de redes llevan texto vivo, y Chromium lo dibuja con las fuentes instaladas.

## Generar

```bash
cd source/brand-kit
python3 build_kit.py out
cp out/eki-labs-brand-kit.zip out/eki-labs-logos.zip out/eki-labs-colours.zip out/eki-labs-type.zip out/eki-labs-social.zip ../../site/brand/kit/
```

Resultado: `out/eki-labs-brand-kit/` (136 archivos) y los zips.

## Qué es cada archivo

- `masters/`: los originales en curvas. `eki-labs-dia.svg` lleva el símbolo y el wordmark; los dos `lockup-firma-*` llevan el logo con el lema, en horizontal y en vertical.
- `logos.py`: recorta cada marca al dibujo y la exporta en los colores day, night, black y white, en SVG, PDF y PNG.
- `social.py`: las plantillas de redes en SVG (avatares, LinkedIn, YouTube, Instagram, posts y la imagen de enlace).
- `build_kit.py`: monta el kit entero (logos, colores, tipografías, redes, README y SIZES) y los zips.
- `render_svgs.mjs`: pasa los SVG a PNG con Chromium.
- `README.md` y `SOCIAL-SIZES.md`: la documentación que va dentro del kit. Las medidas de redes se verificaron en octubre de 2026; revísalas antes de una campaña.
