// POST /api/contact · the contact form on the home page.
// Sends the message by email through Resend (https://resend.com). Configure in Cloudflare Pages
// › Settings › Variables and secrets:
//   RESEND_API_KEY  (secret)  API key from Resend
//   CONTACT_FROM              sender on a domain verified in Resend, e.g. "eki.labs web <web@notify.ekilabs.com>"
//   CONTACT_TO                where messages go (comma-separated), default hola@ekilabs.com
const json = (body, status = 200) =>
  new Response(JSON.stringify(body), { status, headers: { 'content-type': 'application/json; charset=utf-8', 'cache-control': 'no-store' } });

export async function onRequestPost({ request, env }) {
  let d;
  try {
    const type = request.headers.get('content-type') || '';
    d = type.includes('application/json') ? await request.json() : Object.fromEntries(await request.formData());
  } catch {
    return json({ ok: false, error: 'bad_request' }, 400);
  }
  if (d.website) return json({ ok: true }); // honeypot: bots fill it, people never see it
  const clean = (v, n) => String(v ?? '').replace(/[\r\n]+/g, ' ').trim().slice(0, n);
  const name = clean(d.name, 200);
  const email = clean(d.email, 200);
  const profile = clean(d.profile, 60);
  const message = String(d.message ?? '').trim().slice(0, 5000);
  const consent = d.privacy === 'on' || d.privacy === true || d.privacy === 'true';
  if (!name || !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email) || !consent) return json({ ok: false, error: 'invalid' }, 422);
  if (!env.RESEND_API_KEY || !env.CONTACT_FROM) return json({ ok: false, error: 'not_configured' }, 503);
  const r = await fetch('https://api.resend.com/emails', {
    method: 'POST',
    headers: { Authorization: `Bearer ${env.RESEND_API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({
      from: env.CONTACT_FROM,
      to: (env.CONTACT_TO || 'hola@ekilabs.com').split(',').map((s) => s.trim()).filter(Boolean),
      reply_to: email,
      subject: `ekilabs.com · ${profile || 'Contact'} · ${name}`,
      text: `Name: ${name}\nEmail: ${email}\nI am: ${profile || '—'}\n\n${message || '(no message)'}\n\n— Sent from the contact form at ekilabs.com`,
    }),
  });
  if (!r.ok) return json({ ok: false, error: 'send_failed' }, 502);
  return json({ ok: true });
}

export const onRequest = () => new Response('Method not allowed', { status: 405, headers: { Allow: 'POST' } });
