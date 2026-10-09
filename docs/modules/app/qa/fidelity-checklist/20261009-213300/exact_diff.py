"""Fidelity finder scratch script (read-only on the product).

Re-reads the six harness captures and measures them more strictly than the gate does: the gate counts a pixel
only when its normalised RGB distance is above 0.1; this script counts every pixel that differs by even one
channel level, and records the largest channel delta and the box that holds the differing pixels.
It writes only exact_diff.json next to itself.
"""
import hashlib
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

QA = Path(sys.argv[1])
OUT = Path(sys.argv[2])
RUNS = [
    "fidelity-today-390x844",
    "fidelity-today-1280x800",
    "fidelity-today-empty-390x844",
    "fidelity-today-empty-1280x800",
    "fidelity-delete-dialog-390x844",
    "fidelity-delete-dialog-1280x800",
]
result = {}
for name in RUNS:
    folders = sorted(p for p in (QA / name).iterdir() if p.is_dir())
    folder = folders[-1]
    g = np.asarray(Image.open(folder / "golden.png").convert("RGBA"), dtype=np.int32)
    c = np.asarray(Image.open(folder / "candidate.png").convert("RGBA"), dtype=np.int32)
    entry = {
        "folder": str(folder.relative_to(QA)).replace("\\", "/"),
        "golden_shape": list(g.shape),
        "candidate_shape": list(c.shape),
        "golden_sha256": hashlib.sha256((folder / "golden.png").read_bytes()).hexdigest()[:16],
        "candidate_sha256": hashlib.sha256((folder / "candidate.png").read_bytes()).hexdigest()[:16],
    }
    if g.shape == c.shape:
        delta = np.abs(g - c).max(axis=2)
        ys, xs = np.nonzero(delta)
        entry["pixels_differing_at_any_level"] = int((delta > 0).sum())
        entry["max_channel_delta"] = int(delta.max())
        entry["differing_box"] = (
            [int(xs.min()), int(ys.min()), int(xs.max()), int(ys.max())] if len(xs) else None
        )
        entry["distinct_colours_in_candidate"] = int(len({tuple(p) for p in c.reshape(-1, 4)[::7]}))
    result[name] = entry
OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
