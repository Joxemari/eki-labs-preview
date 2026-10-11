# Despliegue de ekilabs.com

Guía paso a paso para poner la web nueva en producción y retirar la de Framer. Está pensada para hacerla con Claude Code contra este repo. Los pasos de los paneles (GitHub, Cloudflare, Namecheap, Resend, Framer) los haces tú, porque piden tu sesión. Claude Code no introduce contraseñas ni claves.

Estado verificado el 11 oct 2026:

- **ekilabs.com:** registrado en Namecheap, DNS en Cloudflare. Por HTTPS, `@` y `www` redirigen con un 301 a ekiagrivoltaics.com, conservando la ruta. Por HTTP no hay redirección: responde un 404 de Vercel (`DEPLOYMENT_NOT_FOUND`), porque `@` y `www` siguen apuntando a Vercel, donde ya no hay web. Esos registros se borran en el paso 4. Correo en Google Workspace (`MX 1 smtp.google.com`, SPF de Google y verificación de Google en TXT): no se toca.
- **Repo:** privado. GitHub Pages está desactivado, así que la preview `joxemari.github.io/eki-labs-preview/` y las imágenes de las firmas antiguas dan 404 (ver paso 7).
- **ekiagrivoltaics.com:** DNS en Namecheap. La web está en Framer (`@` con A a Framer, `www` CNAME `sites.framer.app`). Tiene reenvío de correo de Namecheap (MX `eforward*`): no se toca.

---

## 0 · Antes de empezar: bloqueantes de contenido

Sin esto no se lanza:

- [ ] **Legal notice y Privacy** (`site/legal/`, `site/privacy/`): titular y responsable, Eki Labs Corp. (Delaware), con domicilio registral en su agente registrado. Datos de la ficha «Grupo societario y datos de referencia» de Notion. Falta completar: EIN (confirmar con la carta del IRS), representante en la UE (artículo 27 del RGPD, si procede), plazos de conservación, región y garantías de Resend, juzgados y fecha. Revisión de un abogado. Luego quitar el aviso «Draft pending legal review».
- [ ] **Texto PRTR** del pie: «[Programa, componente e inversión del PRTR y breve descripción del proyecto: pendiente]». Confirmar con el IDAE.
- [ ] **hola@ekilabs.com** recibe correo (buzón o grupo de Google). Es el destino del formulario y el email de toda la web.
- [ ] **Fotos:** se mantienen como están, por decisión tuya. Las que no son de eki.labs (la portada, entre otras) quedan públicas en ekilabs.com: confirma que hay licencia o permiso.
- [ ] **Recomendado, no bloqueante:** €3.5M de ingresos en 2027 sale en la película (/video) y no en el resto de la web (hub, TRA-04).

## 1 · Subir este paquete al repo

En Claude Code, con el repo `Joxemari/eki-labs-preview` clonado.

1. **Primero en GitHub:** Settings › Pages › Build and deployment › Source: **GitHub Actions**.
   - Hazlo antes del push: la web antigua sigue publicada hasta que termine el primer despliegue nuevo.
2. Sustituye el contenido del repo por el de este paquete. La raíz pasa a tener `site/`, `functions/`, `source/`, `.github/` y los `.md`.
   - Los archivos antiguos de la raíz (`index.html`, `assets/`, `decks/`, …) se borran: ahora viven en `site/`.
   - Un solo commit, por ejemplo «Production site: Cloudflare Pages + GitHub Pages from site/».
   - Prompt listo para pegar en Claude Code, abierto en el repo (`C:\Users\joxem\Downloads\eki-labs-preview`):

     > Sustituye el contenido de este repo por el de la carpeta `C:\Users\joxem\Downloads\Claude outputs\eki-labs-web`, incluidos `.github/` y `.gitignore`. Borra los archivos de la raíz que no estén en el paquete, salvo `.git/`. Lee CLAUDE.md y DEPLOY.md. Arranca `npx wrangler pages dev site` y comprueba que cargan `/`, `/legal/`, `/privacy/`, `/brand/` y una URL inexistente (404), y que `POST /api/contact` responde 503 `not_configured`. Prepara un único commit y enséñame el resumen del diff antes de hacer push.

3. Push a la rama principal.
4. Comprueba:
   - Actions › «GitHub Pages (preview)» en verde.
   - `https://joxemari.github.io/eki-labs-preview/` carga.
   - `https://joxemari.github.io/eki-labs-preview/signature/eki-labs-logo.png` existe (lo usan las firmas actuales).

## 2 · Proyecto en Cloudflare Pages

Cloudflare › Workers & Pages › Create › Pages › **Connect to Git** › el repo.

| Ajuste | Valor |
|---|---|
| Production branch | la rama principal (`main`) |
| Framework preset | None |
| Build command | vacío |
| Build output directory | `site` |
| Root directory | vacío (la raíz del repo; ahí está `functions/`) |

- Deploy. Comprueba en la URL `*.pages.dev`:
  - las páginas cargan;
  - `/legal/` y `/privacy/` cargan;
  - `/deck` redirige a `/decks/`;
  - una URL inexistente da el 404 propio.
- Usa Connect to Git, no Direct Upload: un proyecto creado por subida directa no se puede pasar luego a Git.
- El repo es privado: al conectar, autoriza a la app de Cloudflare en GitHub a ver `Joxemari/eki-labs-preview`.
- No actives **Web Analytics** en el proyecto ni en la zona: inyecta un script de `static.cloudflareinsights.com`, una petición a terceros que la política de privacidad dice que no hay.

## 3 · Formulario de contacto (Resend)

1. Cuenta en resend.com. El plan gratuito da 3.000 emails al mes y 100 al día.
2. Domains › Add domain: **`notify.ekilabs.com`**. Resend recomienda enviar desde un subdominio.
3. DNS: botón «Sign in to Cloudflare» (los añade solo) o a mano en Cloudflare › ekilabs.com › DNS, copiando nombre y valor exactamente como los muestre Resend:
   - un MX y un TXT (SPF) bajo un nombre que empieza por `send`;
   - un TXT DKIM bajo `resend._domainkey…`, en modo **DNS only**.
   - No toques el MX ni el SPF raíz de Google.
4. Cuando el dominio salga Verified: API Keys › Create, con permiso de envío y restringida a ese dominio.
5. Cloudflare › el proyecto de Pages › Settings › Variables and secrets (Production):
   - `RESEND_API_KEY` = la clave (tipo **Secret**);
   - `CONTACT_FROM` = `eki.labs web <web@notify.ekilabs.com>`;
   - `CONTACT_TO` = `hola@ekilabs.com` (varias, separadas por comas).
6. Redespliega (las variables se aplican a despliegues nuevos). Prueba el formulario en `*.pages.dev`: debe decir «Thank you…» y llegar el correo, con Reply-To al remitente.

## 4 · ekilabs.com apunta a la web nueva

En Cloudflare › zona ekilabs.com:

1. Localiza y **desactiva** la redirección actual a ekiagrivoltaics.com. Puede ser una Redirect Rule, una Page Rule o una Bulk Redirect; mira en Rules.
2. Borra los registros A/AAAA de `@` y `www` que solo servían para esa redirección.
   - No toques MX, SPF ni `google-site-verification`.
3. Proyecto de Pages › Custom domains › Set up a domain: `ekilabs.com`, y después `www.ekilabs.com`. Cloudflare crea los registros solo.
4. Redirige `www` a `ekilabs.com` con 301 (guía de Cloudflare «Redirecting www to domain apex», con Bulk Redirects). Las páginas ya declaran `ekilabs.com` como canónica.
5. Comprueba:
   - `https://ekilabs.com` y `https://www.ekilabs.com` responden;
   - el formulario funciona en el dominio;
   - un correo de prueba a hola@ekilabs.com sigue llegando a Google.
6. Opcional: redirige `*.pages.dev` a `ekilabs.com` (Bulk Redirects) para no tener la web duplicada.

## 5 · ekiagrivoltaics.com → ekilabs.com y baja de Framer

Namecheap › Domain List › ekiagrivoltaics.com › Manage › Advanced DNS:

1. Borra los A de `@` (Framer) y el CNAME de `www` (`sites.framer.app`).
2. Añade **URL Redirect Record** para `@` → `https://ekilabs.com/`, tipo **Permanent (301)**. Lo mismo para `www`.
3. **No toques** los MX ni el TXT del reenvío de correo.
4. Comprueba que `https://ekiagrivoltaics.com` y `https://www.ekiagrivoltaics.com` llegan a ekilabs.com. Puede tardar lo que tarde la propagación DNS.
5. Framer: quita el dominio del proyecto y, cuando la redirección funcione, cancela el plan.

## 6 · Firmas de correo

Con ekilabs.com en marcha, cada persona regenera su firma en `https://ekilabs.com/signature/`. Las imágenes pasan a servirse desde ekilabs.com. Las firmas antiguas siguen funcionando mientras exista la preview de GitHub.

## 7 · Renombrar el repo (solo al final)

GitHub no redirige las URL de GitHub Pages de un repo renombrado. Renombra solo cuando todo el equipo tenga la firma nueva (paso 6); si no, las imágenes de las firmas antiguas se rompen. Después, comprueba en Cloudflare Pages › Settings › Builds que el repo sigue conectado.

Lo mismo si el repo pasa a **privado**: GitHub Pages en repos privados exige un plan de pago (Pro, Team o Enterprise). Sin él, la preview y las imágenes de las firmas antiguas dejan de servirse. Cloudflare Pages sí funciona con repos privados.

## 8 · Opcional: acceso privado a /decks

Los decks ya van cifrados con contraseña. Si quieres además login por email:

1. Cloudflare Zero Trust (plan gratuito) › Access › Applications › Add › Self-hosted.
2. Dominio `ekilabs.com`, path `decks`. Las subrutas heredan la regla; no uses `decks/*`, que no cubre `/decks`.
3. Política: Allow, emails del equipo o terminados en `@ekilabs.com`. Login con One-time PIN.

## 9 · ekilabs.com/lab (herramienta de evaluación)

La herramienta de evaluación de proyectos (repo privado, acceso para Jox, José y Delia) no está en este repo. Cloudflare Pages sirve todo ekilabs.com desde `site/`, así que /lab necesita una decisión antes de montarla:

- un subdominio (`lab.ekilabs.com`) con su propio proyecto y Cloudflare Access;
- o servirla bajo `/lab` desde este proyecto, con una regla de Access para ese path.

`robots.txt` ya excluye `/lab/`.

## Checklist de lanzamiento

- [ ] Bloqueantes del paso 0 resueltos.
- [ ] Preview de GitHub publicada desde Actions.
- [ ] Pages en `*.pages.dev` correcto.
- [ ] Formulario probado de punta a punta.
- [ ] ekilabs.com y www con HTTPS.
- [ ] Correo de Google intacto.
- [ ] ekiagrivoltaics.com redirige y el reenvío de correo sigue.
- [ ] Framer dado de baja.
- [ ] Firmas regeneradas.
- [ ] Hub de contenidos y lienzo actualizados con lo que haya cambiado.

## Qué cambia respecto a la preview

- Páginas indexables: título, descripción, canónica y Open Graph por página, imagen de enlace y favicons. La firma y los decks siguen sin indexar.
- Fuentes servidas desde la web, sin Google Fonts. Sin Feedbucket. Sin las etiquetas internas «Foto de referencia/provisional».
- Vídeos que se cargan y reproducen solo cerca de la pantalla, y nunca con «reducir movimiento».
- Páginas nuevas: `legal/`, `privacy/` (en inglés y castellano, borradores) y `404`. Enlaces Legal notice · Privacy en el pie.
- Formulario real (`/api/contact`) con consentimiento obligatorio, enlace a la política y antispam.
- `_headers` (seguridad y caché), `_redirects` (/deck, /slides, /careers, /film), `robots.txt` y `sitemap.xml`.
- Retirado el duplicado de la película en 16:9 que no se usaba (`eki-film-16x9.mp4` y su póster).
