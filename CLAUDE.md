# Eki.Labs web · brief for Claude Code

Goal: turn this preview into the production website of Eki.Labs (agrivoltaics: bifacial solar rows facing east and west, with 10–18 m between rows, on working farmland).

## Pages
- `/` Home: hero «Farming soil and sun, together.», the problem (food or energy), the breakthrough, how it works, impact, team, origins, contact.
- `/technology`: single-use vs dual-use land, aligned with demand (one day hour by hour), field tests in Zamora, the farm plan.
- `/model`: value for farmers, three steps, three ways to work with us, the farm, data centers.
- `/video`: the film, shareable on its own.

## Must keep
- Brand in text: **Eki.Labs**; logo: **eki.labs**; company: **Eki Labs Corp.**
- Never write «vertical» for the panels: say «bifacial panels in rows facing east and west».
- Type: Zilla Slab (headlines), Work Sans (text), Geist Mono (data and labels).
- Colors: arena `#f4f2ec`, piedra `#ebe6d8`, noche `#0a100c`, yerba `#58e9ae` (action on dark) / `#056c4a` (action on light), sol `#ffd54a` (energy), tierra `#cf8166`, bosque `#0a281a`, tierra honda `#311d16`.
- Performance figures always with their base: «−95% space, +10% energy, +13% revenue, measured over one year in our field test in Zamora».
- No confidential figures on the public site: round terms, IRR, capital structure, €/kWh.
- Funding block (IDAE, PRTR, NextGenerationEU logos) on every page.
- Photos: only Eki's own or licensed ones. Replace every «Foto provisional».

## Build
- Static site (Astro or plain HTML/CSS), responsive from 360 px, `prefers-reduced-motion` respected.
- Animations (photon hero, counters, plan views, day simulation) as small vanilla JS or canvas modules; the preview uses recorded clips for some of them.
- Deploy: GitHub Pages for previews; production host to decide (Cloudflare Pages supports private repos on the free plan).
