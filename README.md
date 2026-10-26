# PartnershipsStudio

Thoughtful creative partner onboarding, grounded in what matters to the partner.

**M0: scaffold for review.** This repository currently runs a responsive demo shell. It does not generate studios, research people, or call an AI service. Fictional examples establish the intended direction.

```sh
uv sync --frozen
make check
make run
```

Open http://127.0.0.1:8000. Python 3.12+ and uv required; no API key needed.

The intended product turns evidence into authentic use cases, a tailored demo, a five-stage journey and a practical 90-day plan. Evidence, assumptions and unknowns stay visible. Public showcase, full demo and private live generation will share schemas in later milestones.

See [the milestone plan](docs/PLAN.md), [decisions](docs/DECISIONS.md), [architecture](docs/ARCHITECTURE.md), [principle mapping](docs/PRINCIPLES.md), [privacy](docs/PRIVACY.md) and [run/deployment instructions](docs/DEPLOY.md).

Checks: Ruff lint and formatting, strict mypy, route/security tests and offline scaffold evals. M1 will add studio-specific evals; M2 verifies current official API documentation before integration. Portfolio media, live deployment, static showcase and API safeguards are not yet implemented. No affiliation or endorsement is implied.

MIT licensed.
