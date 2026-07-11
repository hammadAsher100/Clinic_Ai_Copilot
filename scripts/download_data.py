"""
Dataset download helper for the Clinical AI Co-Pilot.

Downloads all 3 required datasets:
1. Chest X-Ray Pneumonia (Kaggle) → data/raw/xray/
2. UCI Heart Disease → data/raw/tabular/heart.csv
3. Symptom2Disease (Kaggle) → data/raw/text/Symptom2Disease.csv

Usage:
    python scripts/download_data.py

Requirements:
    - kaggle CLI: pip install kaggle
    - Kaggle API credentials: ~/.kaggle/kaggle.json
    - For UCI dataset: no credentials needed (direct HTTP download)
"""
from __future__ import annotations

import os
import sys
import shutil
import subprocess
import urllib.request
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def download_uci_heart_disease() -> None:
    """Download the UCI Heart Disease Cleveland dataset (no API key needed)."""
    dest_dir = PROJECT_ROOT / "data" / "raw" / "tabular"
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest_file = dest_dir / "heart.csv"

    if dest_file.exists():
        print(f"[✓] Heart disease data already exists: {dest_file}")
        return

    # UCI ML Repository direct download (Cleveland subset)
    url = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease/processed.cleveland.data"
    print(f"[↓] Downloading UCI Heart Disease from {url}...")

    try:
        urllib.request.urlretrieve(url, str(dest_file))
        print(f"[✓] Saved to {dest_file}")
    except Exception as e:
        print(f"[✗] Download failed: {e}")
        print("    Manual download: https://archive.ics.uci.edu/dataset/45/heart+disease")
        print(f"    Save as: {dest_file}")


def download_kaggle_dataset(dataset: str, dest_dir: Path) -> None:
    """Download a Kaggle dataset using the kaggle CLI."""
    dest_dir.mkdir(parents=True, exist_ok=True)

    # Check if data already exists
    if any(dest_dir.iterdir()):
        print(f"[✓] Data already exists in {dest_dir}")
        return

    print(f"[↓] Downloading Kaggle dataset: {dataset}...")

    try:
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d", dataset, "-p", str(dest_dir), "--unzip"],
            capture_output=True, text=True, timeout=300,
        )
        if result.returncode == 0:
            print(f"[✓] Downloaded to {dest_dir}")
        else:
            print(f"[✗] Kaggle download failed: {result.stderr}")
            print(f"    Manual download: https://www.kaggle.com/datasets/{dataset}")
            print(f"    Extract to: {dest_dir}")
    except FileNotFoundError:
        print("[✗] 'kaggle' CLI not found. Install with: pip install kaggle")
        print(f"    Then run: kaggle datasets download -d {dataset} -p {dest_dir} --unzip")
        print(f"    Or manually download from: https://www.kaggle.com/datasets/{dataset}")
    except subprocess.TimeoutExpired:
        print("[✗] Download timed out — try manually or check your internet connection")


def download_xray_data() -> None:
    """Download the Chest X-Ray Pneumonia dataset from Kaggle."""
    dest_dir = PROJECT_ROOT / "data" / "raw" / "xray"
    download_kaggle_dataset("paultimothymooney/chest-xray-pneumonia", dest_dir)

    # The Kaggle dataset extracts with an extra 'chest_xray' subdirectory
    # Move contents up if needed
    nested = dest_dir / "chest_xray"
    if nested.exists():
        for item in nested.iterdir():
            target = dest_dir / item.name
            if not target.exists():
                shutil.move(str(item), str(target))
        shutil.rmtree(str(nested), ignore_errors=True)
        print("[✓] Restructured X-ray directory layout")


def download_symptom_data() -> None:
    """Download the Symptom2Disease dataset from Kaggle."""
    dest_dir = PROJECT_ROOT / "data" / "raw" / "text"
    download_kaggle_dataset("niyarrbarman/symptom2disease", dest_dir)


def verify_data() -> None:
    """Print a summary of available data."""
    print("\n" + "=" * 60)
    print("DATA VERIFICATION")
    print("=" * 60)

    checks = [
        ("Heart Disease CSV", PROJECT_ROOT / "data" / "raw" / "tabular" / "heart.csv"),
        ("X-Ray Train Dir", PROJECT_ROOT / "data" / "raw" / "xray" / "train"),
        ("X-Ray Test Dir", PROJECT_ROOT / "data" / "raw" / "xray" / "test"),
        ("Symptom2Disease CSV", PROJECT_ROOT / "data" / "raw" / "text" / "Symptom2Disease.csv"),
    ]

    all_ok = True
    for name, path in checks:
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"  [{status}] {name}: {path}")
        if not exists:
            all_ok = False

    if all_ok:
        print("\n[✓] All datasets are ready!")
    else:
        print("\n[!] Some datasets are missing — see instructions above")


def main() -> None:
    print("Clinical AI Co-Pilot — Dataset Download")
    print("=" * 50)

    download_uci_heart_disease()
    download_xray_data()
    download_symptom_data()
    verify_data()


if __name__ == "__main__":
    main()
