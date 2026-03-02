from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np


class ModelStore:
    def __init__(self) -> None:
        self.loaded = False
        self.artifact_version = "unloaded"
        self._user_factors: np.ndarray | None = None
        self._item_factors: np.ndarray | None = None
        self._user_id_map: dict[int, int] = {}
        self._item_id_map: dict[int, int] = {}
        self._item_neighbors: dict[int, list[int]] = {}

    def load(self, artifact_path: str) -> None:
        base = Path(artifact_path)
        self._user_factors = np.load(base / "user_factors.npy")
        self._item_factors = np.load(base / "item_factors.npy")

        user_map_raw = json.loads((base / "user_id_map.json").read_text())
        item_map_raw = json.loads((base / "item_id_map.json").read_text())
        neighbors_raw = json.loads((base / "item_neighbors.json").read_text())

        self._user_id_map = {int(k): int(v) for k, v in user_map_raw.items()}
        self._item_id_map = {int(k): int(v) for k, v in item_map_raw.items()}
        self._item_neighbors = {int(k): [int(x) for x in v] for k, v in neighbors_raw.items()}

        config: dict[str, Any] = json.loads((base / "training_config.json").read_text())
        self.artifact_version = str(config.get("artifact_version", base.name))
        self.loaded = True

    def recommend_for_movielens_user(self, raw_user_id: int, k: int) -> list[int]:
        if not self.loaded or self._user_factors is None or self._item_factors is None:
            return []
        user_idx = self._user_id_map.get(raw_user_id)
        if user_idx is None:
            return []
        user_vector = self._user_factors[user_idx]
        scores = self._item_factors @ user_vector
        top_idx = np.argpartition(-scores, min(k, len(scores) - 1))[:k]
        top_sorted = top_idx[np.argsort(-scores[top_idx], kind="stable")]
        inv_item = {v: k for k, v in self._item_id_map.items()}
        return [inv_item[int(i)] for i in top_sorted if int(i) in inv_item]

    def similar_items_for_movielens_item(self, raw_item_id: int, k: int) -> list[int]:
        if not self.loaded:
            return []
        item_idx = self._item_id_map.get(raw_item_id)
        if item_idx is None:
            return []
        inv_item = {v: k for k, v in self._item_id_map.items()}
        neigh = self._item_neighbors.get(item_idx, [])[:k]
        return [inv_item[i] for i in neigh if i in inv_item]


model_store = ModelStore()
