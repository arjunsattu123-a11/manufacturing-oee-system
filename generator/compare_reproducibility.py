
import csv
import hashlib
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw"
MANIFEST_FILE = (
    BASE_DIR / "data" / "processed" / "reproducibility_manifest.json"
)


def checksum(path):
    digest = hashlib.sha256()

    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)

    return digest.hexdigest()


def row_count(path):
    with path.open("r", newline="", encoding="utf-8") as file:
        return sum(1 for _ in csv.DictReader(file))


def main():
    if not MANIFEST_FILE.exists():
        raise FileNotFoundError(
            "Manifest not found. Run "
            "'python -m generator.check_reproducibility' first."
        )

    manifest = json.loads(MANIFEST_FILE.read_text(encoding="utf-8"))
    differences = []

    for filename, expected in manifest.items():
        path = RAW_DIR / filename

        if not path.exists():
            differences.append(f"{filename}: file is missing")
            continue

        actual_rows = row_count(path)
        actual_checksum = checksum(path)

        if actual_rows != expected.get("rows"):
            differences.append(
                f"{filename}: row count changed "
                f"({expected.get('rows')} -> {actual_rows})"
            )

        if actual_checksum != expected.get("sha256"):
            differences.append(f"{filename}: checksum changed")

    print("===== REPRODUCIBILITY MANIFEST COMPARISON =====")

    if differences:
        print("Differences found:")
        for difference in differences:
            print("-", difference)
        print("Current data differs from the saved baseline.")
    else:
        print("All tracked CSV row counts and checksums match the baseline.")
        print("Note: this checks unchanged files, not regeneration determinism.")


if __name__ == "__main__":
    main()
