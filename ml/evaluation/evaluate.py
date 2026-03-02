from pathlib import Path
import json

ARTIFACT_DIR = Path("ml/artifacts/v1")


def main() -> None:
    metrics = json.loads((ARTIFACT_DIR / "metrics.json").read_text())
    print("Offline metrics:", metrics)


if __name__ == "__main__":
    main()
