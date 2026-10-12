# source/

Fuentes de referencia de la web. No se publican y no hacen falta para desplegar: Cloudflare sirve `site/` tal cual.

## canvas/

Los lienzos de diseño (`.dc.html`) de las páginas públicas y de las animaciones que se ven en ellas: How it works (`Capas`), los dos planos (`Comparativa`, `GranjaPlano`) y los clips del logo de `/brand`.

- El original vivo es el lienzo «eki.labs · Web» en Claude Design: https://claude.ai/artifact/HoiQgjcoVVYM5db66e5MBT. Estos archivos son su copia, con las rutas `/_blob/…` de ese lienzo.
- Estos archivos usan huecos de plantilla (`{{p.*}}`) y rutas `/_blob/…` del lienzo: no se abren solos en un navegador.
- Sirven para leer cómo está hecha cada pieza: estructura, textos y lógica de las animaciones.
- Cuando un cambio de diseño se rehace en el lienzo, Cowork regenera `site/` y sustituye estos archivos.

## brand-kit/

Genera el kit de marca descargable (logos en 4 colores × SVG/PDF/PNG, colores ASE/CSS/JSON, tipografías y plantillas para redes). Instrucciones en `brand-kit/BUILD.md`.

## pipeline/

- `responsive.py`: la capa responsiva (clases `r-*`, cortes en 639, 1023 y 1279 px, selector de vídeo por formato).
- `prod.py`: el paso de la preview a producción: metadatos, fuentes locales, favicons, legales, formulario, vídeos diferidos, `_headers`, `_redirects`, robots y sitemap.

Los dos dependen del entorno de Cowork donde se construye la preview (rutas y capturas del lienzo). Aquí quedan como documentación exacta de cada transformación, no como build ejecutable.

El build de los decks no está en el repo, porque trabaja con las fuentes en claro de las presentaciones.
