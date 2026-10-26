# Data and privacy

M1 makes no AI calls and uses no analytics or database. All included examples are fictional. A random HttpOnly, SameSite session cookie identifies the current studio. HTTPS deployments also set Secure.

Imported JSON stays in process memory, isolated by session token. It is unavailable after 30 idle minutes; a cleanup task removes expired sessions within a further 30 seconds even without another request. Clear session removes data immediately. Restarting the app removes all sessions. A limit of 200 sessions bounds memory; capacity pressure may evict the oldest session sooner.

Browser localStorage stores only a theme preference. Studio data is not automatically backed up there. JSON/Markdown downloads remain on the device until deleted by the user. Avoid sensitive personal information, confidential briefs or unlicensed material in imports. Stakeholders are represented by professional roles in the shipped fixtures.

The supplied uvicorn command disables access logs. The application does not log input/output content. Hosting infrastructure may have separate metadata logging; review it before deployment.

Not yet implemented: public research, moderation, triage for private individuals/minors, access codes, per-code limits, budget enforcement and public static showcase. Configure a real private removal-contact email before live deployment. The demo must not be exposed as a public live playground.
