from __future__ import annotations

import json
from pathlib import Path

import numpy as np

ARTIFACT_DIR = Path("ml/artifacts/v1")


def main() -> None:
    item_factors = np.load(ARTIFACT_DIR / "item_factors.npy")
    norms = np.linalg.norm(item_factors, axis=1, keepdims=True) + 1e-12
    normalized = item_factors / norms

    neighbors: dict[int, list[int]] = {}
    for idx in range(normalized.shape[0]):
        sims = normalized @ normalized[idx]
        sims[idx] = -1.0
        top = np.argpartition(-sims, 50)[:50]
        top = top[np.argsort(-sims[top], kind="stable")]
        neighbors[int(idx)] = [int(i) for i in top]

    (ARTIFACT_DIR / "item_neighbors.json").write_text(json.dumps(neighbors))
    print("item_neighbors.json written")


if __name__ == "__main__":
    main()
