import json
from typing import Any

from atelier.schemas import Studio
from atelier.scoring import rank_use_cases


def markdown_export(studio: Studio) -> str:
    """Export every stored field as readable Markdown; preserve provenance and context."""
    lines = [
        f"# {studio.name}",
        "",
        "AI draft — verify before outreach.",
        "Fictional example." if studio.fictional else "Imported draft; unverified.",
        "",
    ]
    lines += ["## Ranked use cases (exported weights)", ""]
    for index, (case, score) in enumerate(
        rank_use_cases(studio.use_cases, studio.scoring_weights), 1
    ):
        lines.append(f"{index}. {case.title} — {score:.1f}/100")
    lines.append("")

    def walk(value: Any, depth: int = 2) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                lines.append(f"{'#' * min(depth, 6)} {key.replace('_', ' ').title()}")
                lines.append("")
                walk(child, depth + 1)
        elif isinstance(value, list):
            for child in value:
                if isinstance(child, (dict, list)):
                    walk(child, depth)
                    lines.append("---")
                else:
                    lines.append(f"- {child}")
            lines.append("")
        else:
            lines.extend([str(value) if value is not None else "Not supplied", ""])

    walk(json.loads(studio.model_dump_json()))
    return "\n".join(lines)
