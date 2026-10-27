# Editable static demo

`index.html` and `assets/demo.js` provide the four-tab browser demo. Build with `PYTHONPATH=. uv run python scripts/build_demo.py`. Generated `dist/` is ignored and contains only fictional fixture data, its schema, local assets and the 45-second captioned walkthrough.

The demo keeps visitor edits in browser memory and offers JSON export/import. It has no owner-system or AI endpoint. See `docs/PUBLISH_STATUS.md` for the blocked publication state.
