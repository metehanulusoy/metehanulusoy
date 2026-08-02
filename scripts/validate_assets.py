#!/usr/bin/env python3
"""Validate README-local assets and repository-native SVG files."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parent.parent
README = ROOT / "README.md"
MAX_SVG_BYTES = 120_000
SMIL_TAGS = {"animate", "animateMotion", "animateTransform", "set"}

HTML_ASSET = re.compile(r"(?:src|srcset)=\"([^\"]+)\"")
MARKDOWN_ASSET = re.compile(r"!\[[^\]]*\]\(([^)]+)\)")


def local_path(reference: str) -> Path | None:
    reference = reference.strip().split()[0]
    parsed = urlsplit(reference)
    if parsed.scheme or parsed.netloc or reference.startswith("#"):
        return None
    return ROOT / unquote(parsed.path.lstrip("/"))


def validate_svg(path: Path) -> list[str]:
    errors: list[str] = []
    relative = path.relative_to(ROOT)
    size = path.stat().st_size
    if size > MAX_SVG_BYTES:
        errors.append(f"{relative}: {size} bytes exceeds {MAX_SVG_BYTES}")
    try:
        root = ElementTree.parse(path).getroot()
    except ElementTree.ParseError as exc:
        return [f"{relative}: invalid XML ({exc})"]
    if "viewBox" not in root.attrib:
        errors.append(f"{relative}: missing viewBox")
    source = path.read_text(encoding="utf-8").lower()
    if "<script" in source or "javascript:" in source:
        errors.append(f"{relative}: executable script content is not allowed")
    has_motion = "@keyframes" in source or "<animate" in source
    if has_motion and "prefers-reduced-motion" not in source:
        errors.append(f"{relative}: animated asset lacks reduced-motion handling")

    def check_smil(element: ElementTree.Element, motion_parent: bool = False) -> None:
        classes = element.attrib.get("class", "").split()
        hidden_for_reduced_motion = motion_parent or "motion" in classes
        tag = element.tag.rsplit("}", 1)[-1]
        if tag in SMIL_TAGS and not hidden_for_reduced_motion:
            errors.append(
                f"{relative}: <{tag}> must be inside an element with class 'motion'"
            )
        for child in element:
            check_smil(child, hidden_for_reduced_motion)

    check_smil(root)
    return errors


def main() -> int:
    errors: list[str] = []
    svg_paths = sorted((ROOT / "assets").rglob("*.svg"))
    if not svg_paths:
        errors.append("no SVG assets found")
    for path in svg_paths:
        errors.extend(validate_svg(path))

    readme = README.read_text(encoding="utf-8")
    references = HTML_ASSET.findall(readme) + MARKDOWN_ASSET.findall(readme)
    for reference in references:
        path = local_path(reference)
        if path is not None and not path.is_file():
            errors.append(f"README references missing local asset: {reference}")

    if errors:
        for error in errors:
            print(f"[error] {error}", file=sys.stderr)
        return 1

    print(
        f"[ok] validated {len(svg_paths)} SVG files and "
        f"{len(references)} README asset references"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
