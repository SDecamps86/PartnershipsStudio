"""Build a static, editable demo from fictional fixture files only. Never read sessions/env."""

import argparse
import json
import shutil
from pathlib import Path

from atelier.schemas import Studio
from atelier.store import PERSONAS, load_fixture

ROOT = Path(__file__).resolve().parent.parent


def build(destination: Path) -> None:
    assets = destination / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    data: dict[str, list[dict[str, object]]] = {}
    for variant in ("base", "sharpened"):
        studios = [load_fixture(persona, variant) for persona in PERSONAS]
        if not all(
            s.fictional and all(e.source_url.startswith("fixture://") for e in s.evidence)
            for s in studios
        ):
            raise ValueError("Publication accepts fictional fixtures only")
        data[variant] = [s.model_dump(mode="json") for s in studios]
    (assets / "data.json").write_text(json.dumps(data, ensure_ascii=False))
    (assets / "schema.json").write_text(json.dumps(Studio.model_json_schema()))
    shutil.copyfile(ROOT / "site/index.html", destination / "index.html")
    shutil.copyfile(ROOT / "app/static/styles.css", assets / "styles.css")
    for name in ("demo.css", "demo.js", "mini-demo.mp4", "demo.vtt", "video-poster.png"):
        source = ROOT / "site/assets" / name
        if source.exists():
            shutil.copyfile(source, assets / name)
    (destination / "_headers").write_text(
        "/*\n  X-Content-Type-Options: nosniff\n  Referrer-Policy: no-referrer\n"
        "  Permissions-Policy: camera=(), microphone=(), geolocation=()\n"
    )
    print(f"Built fictional demo: {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "site/dist")
    build(parser.parse_args().output)
