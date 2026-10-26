# Decisions

1. Use PartnershipsStudio, matching the supplied repository; retain `atelier` as the requested internal core package.
2. Default to the demo scaffold. Even APP_MODE=live cannot enable generation in M0.
3. Keep all assets local under a restrictive content security policy; no external font, script or analytics requests.
4. Use hand-authored CSS tokens for the initial shell. Add locally compiled Tailwind and vendored interaction libraries with M1 components.
5. Defer sessions, browser backups and all input endpoints until needed. Default uvicorn commands disable access logs.
6. Defer OpenAI integration and API documentation verification to M2, when an actual integration is implemented.
7. Never publish a fabricated support email. Configure a private removal contact before live release.
8. Stop after each milestone, per the supplied working agreement. No remote push or hosting changes during M0.
