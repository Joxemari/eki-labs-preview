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

Resultado: `out/eki-labs-brand-kit/` (193 archivos) y los zips.

Después, desde la raíz del repo, `python3 source/brand-kit/build_download.py`: descomprime el kit en `site/brand/kit/files/` (descarga archivo a archivo) y regenera `/brand/download/`, el creador de logos.

Y por último `python3 source/brand-kit/site_logos.py`: escribe los logos de la web (`site/assets`), favicons, iconos, la imagen de enlace (copiada del kit ya descomprimido), las imágenes de la firma de correo, y aplica el logo en degradado completo al dibujado en las páginas y en los lienzos de `source/canvas`.

Los vídeos del logo de `/brand` (`site/assets/clip-logo*.mp4` y sus `still-logo*.jpg`) se graban de los lienzos `source/canvas/Logo*.dc.html` con el grabador de clips (`08-sesion-cowork/pipeline/clips/rec.mjs` del repo de marca), sirviendo los lienzos con el runtime de Claude Design como `support.js`.

Playwright se importa como módulo ES: si `render_svgs.mjs` no lo encuentra, enlaza la instalación global en esta carpeta (`ln -s "$(npm root -g)" node_modules`) y bórrala al terminar.

## Qué es cada archivo

- `masters/`: los originales en curvas del logo anterior. `logos.py` toma de ellos la geometría del símbolo y la posición del lema; el nombre y el lema se dibujan ahora desde las fuentes.
- `wordmark.py`: dibuja el nombre en curvas desde Geist: «eki.» en 600 y el apellido en 400.
- `logos.py`: el símbolo con el degradado del sol, el nombre, el lema en curvas (Zilla Slab) y las firmas; recorta cada marca al dibujo y la exporta en day, night, black y white, en SVG, PDF y PNG. Los colores de los degradados están en `SUN_STOPS` (el sol) y `FULL_STOPS` (la opción del degradado completo).
- `site_logos.py`: los logos que la web usa fuera del kit (cabecera, pie, favicons, iconos, firma de correo) y el logo dibujado en las páginas.
- `social.py`: las plantillas de redes en SVG (avatares, LinkedIn, YouTube, Instagram, posts y la imagen de enlace).
- `build_kit.py`: monta el kit entero (logos, colores, tipografías, redes, README y SIZES) y los zips.
- `render_svgs.mjs`: pasa los SVG a PNG con Chromium.
- `README.md` y `SOCIAL-SIZES.md`: la documentación que va dentro del kit. Las medidas de redes se verificaron en octubre de 2026; revísalas antes de una campaña.
