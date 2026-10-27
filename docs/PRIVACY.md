# Data and privacy

M1 makes no AI calls and uses no analytics or database. All included examples are fictional. A random HttpOnly, SameSite session cookie identifies the current studio. HTTPS deployments also set Secure.

Imported JSON stays in process memory, isolated by session token. It is unavailable after 30 idle minutes; a cleanup task removes expired sessions within a further 30 seconds even without another request. Clear session removes data immediately. Restarting the app removes all sessions. A limit of 200 sessions bounds memory; capacity pressure may evict the oldest session sooner.

Browser localStorage stores only a theme preference. Studio data is not automatically backed up there. JSON/Markdown downloads remain on the device until deleted by the user. Avoid sensitive personal information, confidential briefs or unlicensed material in imports. Stakeholders are represented by professional roles in the shipped fixtures.

The supplied uvicorn command disables access logs. The application does not log input/output content. Hosting infrastructure may have separate metadata logging; review it before deployment.

Not yet implemented: public research, moderation, triage for private individuals/minors, access codes, per-code limits, budget enforcement and public static showcase. Configure a real private removal-contact email before live deployment. The demo must not be exposed as a public live playground.

## Partner pipeline

The current session holds a small portfolio rather than a single partner. Checklist completion, lead stage/maturity, invitation status and manually entered metric counts stay in that same session. The seeded operational figures and event plans are fictional. No live calendar, email, CRM or product telemetry is connected.

The workspace is limited to 12 partners and 3 MB, with at most 100 sessions in one server process. Clearing the workspace removes all its records; a new demo workspace is seeded from immutable fictional fixtures. Export/import preserves one selected partner at a time, including tracking. Switching partners does not erase earlier edits. Switching sample-context variants preserves tracking and weights.

## Current static demo surface

The current root UI and static publication candidate use browser-memory records, not the Python server session store. No entered or imported value is sent to the owner or another server. Reloading/closing the tab discards changes. Exported files persist on the user's device. Only the theme preference is stored in localStorage.

The owner-environment statement is provided by the owner. No owner data, live app link, credentials, real customer record, guest data or production service is packaged. Team names and operating counts are fictional. Hosting request metadata is separate from application data; there is no analytics or telemetry collection.
