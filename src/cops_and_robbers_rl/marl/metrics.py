"""Dependency-free training metrics and honest SVG plots."""

import json
from dataclasses import asdict, dataclass
from html import escape
from pathlib import Path


@dataclass(frozen=True, slots=True)
class EpisodeMetric:
    episode: int
    cop_return: float
    thief_return: float
    cop_loss: float
    thief_loss: float
    moves: int
    winner: str


def save_metrics(metrics: list[EpisodeMetric], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps([asdict(metric) for metric in metrics], indent=2) + "\n", encoding="utf-8"
    )
    return destination


def save_line_plot(values: list[float], path: str | Path, *, title: str, y_label: str) -> Path:
    """Write a compact standards-compliant SVG line chart."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    width, height, margin = 720, 420, 55
    low, high = min(values, default=0.0), max(values, default=1.0)
    span = high - low or 1.0
    points = []
    for index, value in enumerate(values):
        x = margin + index * (width - 2 * margin) / max(len(values) - 1, 1)
        y = height - margin - (value - low) * (height - 2 * margin) / span
        points.append(f"{x:.1f},{y:.1f}")
    svg = _svg_frame(width, height, title, y_label)
    svg += f'<polyline points="{" ".join(points)}" fill="none" stroke="#2563eb" stroke-width="2"/>'
    svg += f'<text x="{margin}" y="{height - 14}" font-size="12">Episodes</text></svg>\n'
    destination.write_text(svg, encoding="utf-8")
    return destination


def save_comparison_plot(values: dict[str, float], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    width, height, margin = 720, 420, 55
    ceiling = max(values.values(), default=1.0) or 1.0
    svg = _svg_frame(width, height, "Baseline comparison", "Role wins in 6 games")
    bar_width = (width - 2 * margin) / max(len(values), 1) * 0.55
    for index, (label, value) in enumerate(values.items()):
        x = margin + (index + 0.25) * (width - 2 * margin) / max(len(values), 1)
        bar_height = value / ceiling * (height - 2 * margin)
        y = height - margin - bar_height
        svg += (
            f'<rect x="{x:.1f}" y="{y:.1f}" width="{bar_width:.1f}" '
            f'height="{bar_height:.1f}" fill="#0f766e"/>'
        )
        svg += f'<text x="{x:.1f}" y="{height - 18}" font-size="12">{escape(label)}</text>'
    destination.write_text(svg + "</svg>\n", encoding="utf-8")
    return destination


def _svg_frame(width: int, height: int, title: str, y_label: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>'
        f'<text x="55" y="28" font-size="18">{escape(title)}</text>'
        f'<text x="8" y="55" font-size="12">{escape(y_label)}</text>'
        f'<path d="M55 55V365H665" fill="none" stroke="#334155"/>'
    )
