from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

DATA_DIR = Path("ml/data/ml-1m")
ARTIFACT_DIR = Path("ml/artifacts/v1")


def main() -> None:
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)
    ratings = pd.read_csv(
        DATA_DIR / "ratings.dat",
        sep="::",
        engine="python",
        names=["user_raw_id", "item_raw_id", "rating", "ts"],
        encoding="latin-1",
    )
    ratings["implicit"] = (ratings["rating"] >= 4).astype(int)
    ratings.to_parquet(ARTIFACT_DIR / "interactions.parquet", index=False)

    user_ids = sorted(ratings["user_raw_id"].unique().tolist())
    item_ids = sorted(ratings["item_raw_id"].unique().tolist())
    user_id_map = {int(raw): idx for idx, raw in enumerate(user_ids)}
    item_id_map = {int(raw): idx for idx, raw in enumerate(item_ids)}

    (ARTIFACT_DIR / "user_id_map.json").write_text(json.dumps(user_id_map))
    (ARTIFACT_DIR / "item_id_map.json").write_text(json.dumps(item_id_map))

    ratings = ratings.sort_values(["user_raw_id", "ts"])
    ratings["rank_desc"] = ratings.groupby("user_raw_id")["ts"].rank(method="first", ascending=False)
    val = ratings[ratings["rank_desc"] <= 1].drop(columns=["rank_desc"])
    train = ratings[ratings["rank_desc"] > 1].drop(columns=["rank_desc"])
    train.to_parquet(ARTIFACT_DIR / "train.parquet", index=False)
    val.to_parquet(ARTIFACT_DIR / "val.parquet", index=False)

    print("Preprocess completed")


if __name__ == "__main__":
    main()
