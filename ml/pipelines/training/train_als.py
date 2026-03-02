from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from implicit.als import AlternatingLeastSquares
from scipy.sparse import csr_matrix

ARTIFACT_DIR = Path("ml/artifacts/v1")


def recall_at_k(model: AlternatingLeastSquares, train: csr_matrix, val_items: dict[int, set[int]], k: int = 10) -> float:
    recalls: list[float] = []
    for user_idx, gt_items in val_items.items():
        recs, _ = model.recommend(user_idx, train[user_idx], N=k, filter_already_liked_items=True)
        hit = len(set(recs.tolist()) & gt_items)
        recalls.append(hit / max(len(gt_items), 1))
    return float(np.mean(recalls)) if recalls else 0.0


def ndcg_at_k(model: AlternatingLeastSquares, train: csr_matrix, val_items: dict[int, set[int]], k: int = 10) -> float:
    scores = []
    for user_idx, gt_items in val_items.items():
        recs, _ = model.recommend(user_idx, train[user_idx], N=k, filter_already_liked_items=True)
        dcg = 0.0
        for rank, item_idx in enumerate(recs.tolist(), start=1):
            if item_idx in gt_items:
                dcg += 1.0 / np.log2(rank + 1)
        idcg = sum(1.0 / np.log2(i + 1) for i in range(1, min(len(gt_items), k) + 1))
        scores.append(dcg / idcg if idcg > 0 else 0.0)
    return float(np.mean(scores)) if scores else 0.0


def main() -> None:
    train_df = pd.read_parquet(ARTIFACT_DIR / "train.parquet")
    val_df = pd.read_parquet(ARTIFACT_DIR / "val.parquet")
    user_map = {int(k): int(v) for k, v in json.loads((ARTIFACT_DIR / "user_id_map.json").read_text()).items()}
    item_map = {int(k): int(v) for k, v in json.loads((ARTIFACT_DIR / "item_id_map.json").read_text()).items()}

    train_df = train_df[train_df["implicit"] == 1].copy()
    train_df["user_idx"] = train_df["user_raw_id"].map(user_map)
    train_df["item_idx"] = train_df["item_raw_id"].map(item_map)

    num_users = len(user_map)
    num_items = len(item_map)
    mat = csr_matrix((np.ones(len(train_df)), (train_df["item_idx"], train_df["user_idx"])), shape=(num_items, num_users))

    model = AlternatingLeastSquares(factors=64, regularization=0.02, iterations=20, random_state=42)
    model.fit(mat)

    np.save(ARTIFACT_DIR / "user_factors.npy", model.user_factors)
    np.save(ARTIFACT_DIR / "item_factors.npy", model.item_factors)

    val_df = val_df[val_df["implicit"] == 1].copy()
    val_df["user_idx"] = val_df["user_raw_id"].map(user_map)
    val_df["item_idx"] = val_df["item_raw_id"].map(item_map)
    val_items: dict[int, set[int]] = {}
    for _, row in val_df.iterrows():
        if pd.isna(row["user_idx"]) or pd.isna(row["item_idx"]):
            continue
        val_items.setdefault(int(row["user_idx"]), set()).add(int(row["item_idx"]))

    recall = recall_at_k(model, mat.T.tocsr(), val_items, k=10)
    ndcg = ndcg_at_k(model, mat.T.tocsr(), val_items, k=10)

    (ARTIFACT_DIR / "training_config.json").write_text(json.dumps({"factors": 64, "iterations": 20, "artifact_version": "v1"}))
    (ARTIFACT_DIR / "metrics.json").write_text(json.dumps({"recall@10": recall, "ndcg@10": ndcg}))
    print({"recall@10": recall, "ndcg@10": ndcg})


if __name__ == "__main__":
    main()
