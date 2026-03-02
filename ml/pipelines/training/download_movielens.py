from __future__ import annotations

import io
import zipfile
from pathlib import Path

import requests

URL = "https://files.grouplens.org/datasets/movielens/ml-1m.zip"
TARGET_DIR = Path("ml/data")


def main() -> None:
    TARGET_DIR.mkdir(parents=True, exist_ok=True)
    response = requests.get(URL, timeout=120)
    response.raise_for_status()

    with zipfile.ZipFile(io.BytesIO(response.content)) as zf:
        zf.extractall(TARGET_DIR)

    print(f"Downloaded and extracted to {TARGET_DIR / 'ml-1m'}")


if __name__ == "__main__":
    main()
