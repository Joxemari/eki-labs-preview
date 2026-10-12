# eki.labs · web (ekilabs.com)

Instrucciones para Claude Code en este repo. Léelas enteras antes de tocar nada.

## Qué es

La web pública de eki.labs: HTML estático en `site/`, una función para el formulario de contacto en `functions/` y, en `source/`, las fuentes de referencia.

- **Producción:** Cloudflare Pages conectado a este repo. Cada push a la rama principal publica `site/` en ekilabs.com.
- **Preview:** GitHub Actions publica el mismo `site/` en `joxemari.github.io/eki-labs-preview/` (workflow `.github/workflows/pages.yml`). Ahí siguen el enlace de preview antiguo y las imágenes de las firmas de correo hechas antes del lanzamiento.
- **Despliegue paso a paso:** `DEPLOY.md`.

## Cómo trabajamos (reglas del equipo)

1. **El conocimiento es uno y los soportes cambian.** Textos y cifras salen del hub de contenidos, el doc «eki-contenidos-hub» del proyecto Eki Labs en Claude. El diseño sale del lienzo «eki.labs · Web». Si cambias algo aquí, dilo al terminar para que se replique en el hub y en el lienzo. Web, decks y película tienen que decir lo mismo.
2. **Nunca implementes un cambio no pedido sin alinearlo.** Puedes proponer mejoras, pero cada cambio que no se haya pedido se deja escrito y se avisa a Jox antes de hacerlo.
3. **Comprueba, no supongas.** Revisa los logs y la página renderizada antes de dar algo por bueno.
4. Para hablar con Jox: en castellano, conciso, punto por punto.

## Reglas de marca y contenido (públicas, se aplican a todo lo visible)

- **Nombre:** siempre **eki.labs**, en minúscula y en la tipografía del texto que lo rodea. Nunca «Eki.Labs», «Eki Labs» ni en mayúsculas, tampoco dentro de una etiqueta en mayúsculas: envuélvelo en un `<span style="text-transform:none">`. Empresa visible en la web (contacto, pie, ejemplos de marca): **Eki Labs Corp.** Titular legal de la web: **Eki Agrivoltaic, S.L.U.**, solo en el aviso legal, la privacidad y el «©» del pie.
- **Logo:** el símbolo (sol sobre tres filas) va entero en el degradado del sol: naranja `#FF8F00` arriba, sol `#FFD54A` en el horizonte y la primera fila, yerba `#58E9AE` abajo. El nombre: «eki.» en Geist 600 y el apellido en Geist 400 (eki.labs). El kit trae eki.labs y eki.; cualquier otra terminación sale del creador de logos de `/brand/download`. Versiones de una tinta (black, white) para grabado y prensa.
- **Firma de marca:** logo + «Farming soil & sun, together» (con «&», con coma y sin punto) en un solo bloque, como viene en los archivos del logo. El lema es siempre el mismo y siempre del mismo tamaño: tan ancho como el logo eki.labs. No se rehace con texto vivo.
- **Lemas:** «Farming soil & sun, together» (firma) · «One acre. Two harvests.» (idea).
- **Tecnología:** «bifacial panels in rows, facing east and west», 10–18 m entre filas. Nunca «vertical».
- **Cifras públicas:** −95% land · +10% energy · +13% revenue, siempre con su base: «measured over one year in our field test in Zamora». Respaldo: «Backed by Harvard and MIT». Ronda: «€18M raised». Cartera: 33 MWp ready to build + 20 MWh. Potencia en MWp, nunca «35 MW».
- **Nunca en la web:** términos financieros (rentabilidad, estructura de capital, precio de la energía, condiciones de la ronda más allá de «€18M raised», importes de subvenciones) ni datos que solo viven en los decks. Si dudas de si una cifra es pública, pregunta.
- **No añadas** referencias a empresas, marcas o proyectos que no estén ya en la web.
- **Idioma:** todo lo visible en inglés. Excepciones: el texto legal de financiación (IDAE, PRTR) y la versión en castellano de Legal notice y Privacy.
- **Data centers** (inglés de EE. UU.). «agrivoltaics» en texto.

## Sistema visual

- **Color** (16 tokens, cada uno con un trabajo): sol `#FFD54A` (energía, la cifra clave, nunca botón ni texto) · yerba `#58E9AE` (cultivo, y el color de acción sobre oscuro) · tierra `#CF8166` · noche `#0A100C` (nuestro negro) · yerba honda `#056C4A` (yerba como texto sobre claro) · tierra honda `#964A2F` · origen `#311D16` · bosque `#0A281A` · arena `#F4F2EC` (fondo) · piedra `#EBE6D8` · línea `#D6D1C3` · pizarra `#555A52` · grafito `#141B16` · acero `#2B332D` · niebla `#A1A69F` · blanco `#FFFFFF` (solo en superficies ajenas: email, documentos). Sol y yerba nunca juntos, salvo fundidos dentro del degradado del logo. El degradado es solo del logo y del sol del horizonte (naranja a sol): no es un color de la paleta.
- **Tipografía:** Zilla Slab 400 para titulares (tracking ajustado, frase con punto final) · Work Sans 400/500 para texto · Geist Mono 500 para etiquetas en mayúsculas (tracking 8%) y 400 para cifras. Las fuentes se sirven desde `site/fonts/`: no vuelvas a enlazar Google Fonts, porque la política de privacidad dice que no hay peticiones a terceros.
- La guía completa está en `/brand` (`site/brand/index.html`) y el kit descargable en `site/brand/kit/`.

## Estructura de `site/`

```
index.html               Home
technology/ model/ video/ brand/ signature/   páginas
legal/ privacy/ 404.html  páginas legales (borradores, ver abajo)
decks/                   presentaciones CIFRADAS (no editar a mano)
assets/                  imágenes, vídeos y SVG de las páginas
fonts/                   woff2 + fonts.css
brand/kit/               zips del kit de marca
_headers _redirects      configuración de Cloudflare Pages
robots.txt sitemap.xml site.webmanifest favicon.* icon-*.png social-preview.png
```

- Las páginas salen del lienzo de diseño: HTML con estilos en línea. Para un cambio de texto, edita el HTML directamente y avisa (regla 1). Para un cambio de diseño, se rehace en el lienzo y se regenera `site/` desde Cowork.
- **Responsivo:** clases `r-*` con puntos de corte en 639, 1023 y 1279 px. El CSS está al principio de cada página. Brand y Email signature son de escritorio.
- **Vídeos:** los carga y reproduce el script del final de cada página, y solo cuando están cerca de la pantalla. Con `prefers-reduced-motion` no se reproducen.
  - Un vídeo con versiones por formato lleva `data-src-d`, `data-src-t` y `data-src-m` (+ `data-poster-*` y `data-ar-*`).
  - Un vídeo simple lleva `data-lazy="ruta.mp4"` y `poster`.
  - No pongas `src` directo en un `<video>` en bucle.
- **Formulario de contacto** (Home): `form[data-contact]` → `POST /api/contact` → `functions/api/contact.js` → email con Resend. Variables en Cloudflare: `RESEND_API_KEY` (secreto), `CONTACT_FROM`, `CONTACT_TO`. Sin variables responde 503 y la página ofrece el email.
- **Firma de correo** (`site/signature/`): el generador usa `var BASE = 'https://ekilabs.com/signature/'` para las imágenes. Las fotos del equipo están en esa carpeta.
- **Decks** (`site/decks/`): `bundle.enc.json` va cifrado y se abre con una contraseña que el equipo tiene. Las fuentes en claro de los decks y la contraseña nunca entran en este repo. Para cambiar un deck, se rehace en Cowork.

## Pendiente antes del lanzamiento (bloqueante)

- `legal/` y `privacy/`: completar los `[...]` (resaltados en amarillo) y que los revise un abogado. Después, quitar el aviso «Draft pending legal review» y poner la fecha.
- Pie de todas las páginas: completar «[Programa, componente e inversión del PRTR y breve descripción del proyecto: pendiente]».
- Ver la lista completa en `DEPLOY.md`.

## Antes de cada push

1. Previsualiza en local: `npx wrangler pages dev site`, desde la raíz del repo; también sirve la función. Si solo quieres ver el estático: `python3 -m http.server -d site 8080`.
2. Mira la página cambiada a 390 px y a 1440 px y revisa que la consola no tenga errores.
3. Ningún archivo puede pasar de 25 MiB (límite de Cloudflare Pages).
4. Ninguna petición a dominios de terceros (fuentes, scripts, analítica). Si alguna vez hace falta una, primero hay que actualizar la política de privacidad.
5. Mensaje de commit claro. Al terminar, resume a Jox qué cambió y qué hay que replicar en el hub o en el lienzo.

## Hoja de ruta (pendiente, no hecho)

- **Microsite de decks** en `decks.ekilabs.com`, con control de acceso, cada slide en HTML 16:9 y selector ES/EN en cada deck. Hoy los decks viven cifrados en `/decks/`.
- **Versión en castellano** de la web.
- **/lab**, la herramienta privada de evaluación de proyectos: falta decidir cómo se sirve (DEPLOY.md, sección 9).
- **Fotos propias** de eki.labs para sustituir las de referencia. De momento se mantienen por decisión de Jox.

Esta versión sustituye a la brief anterior del repo. Esa brief pedía «Eki.Labs» en texto; la regla vigente es **eki.labs** siempre en minúscula.

## `source/`

Fuentes de referencia. No se publican y no forman parte del build: lienzos de las páginas, scripts del kit de marca y del paso a producción. Ver `source/README.md`.
