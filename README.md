# eki.labs · ekilabs.com

Web pública de eki.labs. *Farming soil & sun, together*

| Carpeta | Qué hay |
|---|---|
| `site/` | La web publicada: HTML estático, assets, fuentes, kit de marca y decks cifrados. |
| `functions/` | Cloudflare Pages Functions: `api/contact.js`, el formulario de contacto (Resend). |
| `source/` | Fuentes de referencia (lienzos, kit de marca, scripts de producción). No se publican. |
| `.github/workflows/pages.yml` | Publica `site/` en GitHub Pages (preview y firmas antiguas). |

- **Producción:** Cloudflare Pages, con salida `site` y sin comando de build.
- **Ver en local:** `npx wrangler pages dev site` (incluye el formulario), o `python3 -m http.server -d site 8080` (solo estático).
- **Desplegar:** [DEPLOY.md](DEPLOY.md).
- **Reglas de marca, contenido y edición:** [CLAUDE.md](CLAUDE.md).

© Eki Agrivoltaic, S.L.U. Las tipografías (Zilla Slab, Work Sans, Geist Mono) están bajo SIL Open Font License 1.1.
