# ML Pipeline v1 (MovieLens 1M + Implicit ALS)

This folder contains an end-to-end collaborative filtering pipeline and artifacts used by the API.

## Pipeline layout

- `pipelines/training/download_movielens.py`
- `pipelines/training/preprocess_movielens.py`
- `pipelines/training/train_als.py`
- `pipelines/inference/build_item_neighbors.py`
- `evaluation/evaluate.py`

## Run end-to-end

```bash
python ml/pipelines/training/download_movielens.py
python ml/pipelines/training/preprocess_movielens.py
python ml/pipelines/training/train_als.py
python ml/pipelines/inference/build_item_neighbors.py
python ml/evaluation/evaluate.py
```

## Artifacts

All artifacts are written to `ml/artifacts/v1`:

- `interactions.parquet`
- `train.parquet`
- `val.parquet`
- `user_id_map.json`
- `item_id_map.json`
- `user_factors.npy`
- `item_factors.npy`
- `item_neighbors.json`
- `training_config.json`
- `metrics.json`
