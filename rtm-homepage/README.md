# Recovery Through Music — V5 homepage prototype

Local-only HTML/CSS/vanilla JavaScript. No deployment or live-site changes.

Open index.html directly, or serve this directory with a local HTTP server.

## Files
- index.html: homepage content and semantic structure
- style.css: visual design and responsive layouts
- app.js: mobile menu and native audio rendering
- assets/reference.png: supplied design reference
- assets/logo, assets/photos, assets/audio: reserved for original supplied media

## Still required
Original RTM logo, bass photograph and community photos; approved recordings with titles; confirmed contact email; privacy and safeguarding content. Current imagery is cropped from the reference and is clearly identified as temporary. No audio titles or durations have been invented. Add approved recordings to the recordings array in app.js as { title, src }; native HTML audio players will replace the pending notice.

## Verification
Desktop and 390px mobile screenshots reviewed; no horizontal overflow observed. Mobile menu opens, and choosing Our Music closes it and navigates correctly. All internal anchor targets and local asset paths checked. Semantic landmarks, image labels, skip link, visible focus styling, reduced-motion support and native keyboard controls provided. Audio playback cannot be checked until actual files are supplied. Contact is a marked placeholder.

Web fonts use Google Fonts with local system fallbacks. No analytics, forms, payment collection or data storage.
