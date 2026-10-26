# Decisions

1. Use PartnershipsStudio, matching the supplied repository; retain `atelier` as the requested internal core package.
2. Default to the demo scaffold. Even APP_MODE=live cannot enable generation in M0.
3. Keep all assets local under a restrictive content security policy; no external font, script or analytics requests.
4. Use hand-authored CSS tokens for the initial shell. Add locally compiled Tailwind and vendored interaction libraries with M1 components.
5. Defer sessions, browser backups and all input endpoints until needed. Default uvicorn commands disable access logs.
6. Defer OpenAI integration and API documentation verification to M2, when an actual integration is implemented.
7. Never publish a fabricated support email. Configure a private removal contact before live release.
8. Stop after each milestone, per the supplied working agreement. No remote push or hosting changes during M0.

## M1 decisions

9. The primary surface is an internal preparation tool. Remove the promotional hero, taglines and decorative persona graphics; use task labels, compact UI type and practical context instead.
10. Ship six hand-authored JSON fixtures through the same strict Pydantic schema. `fixture://` sources are explicitly fictional, never presented as web research. All score dimensions have rationale and every candidate has a risk and mitigation.
11. Normalize custom weights to 100 so arbitrary slider totals produce comparable scores. Reject all-zero exports and retain the last valid on-screen ranking. Tie-break by safety, days to value, then ID. Export/import preserves current weights. Reweighting does not silently rewrite a prepared demo.
12. M1's sample-context drawer switches between complete precomputed variants. Arbitrary layer input, incremental recompute and inline edits remain M3; do not imply they work yet.
13. Use native, locally served JavaScript for weights, clipboard, dialog, printing and import. HTMX/Alpine and compiled Tailwind are deferred until they add a concrete benefit; there is no JavaScript build toolchain or external runtime dependency in M1.
14. Store studios in bounded process-local sessions with HttpOnly SameSite cookies and idle cleanup. Activity renews the session; an unattended tab does not keep it alive indefinitely. The cleanup task runs every 30 seconds and expired data is unavailable immediately on access. Use one worker. Capacity is 200 sessions; oldest session may be evicted at the limit.
15. Do not silently back up imported notes or people in localStorage. This resolves the brief's browser-backup versus short-retention conflict through explicit JSON export/import. Only the theme preference persists in browser storage.
16. Same-origin POST checks, bounded JSON imports, strict schemas, safe source links, Jinja autoescaping and restrictive CSP apply to the demo. No mutation endpoint logs request bodies or validation values.
