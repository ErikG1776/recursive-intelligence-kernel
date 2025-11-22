#!/usr/bin/env python3
"""
download_kaggle_invoices.py | Download real invoice PDFs from Kaggle
------------------------------------------------------------
Downloads invoice datasets for OCR demo.

Setup:
1. pip install kaggle
2. Get API key from kaggle.com/account
3. Place kaggle.json in ~/.kaggle/
4. Run this script
"""

import os
import subprocess
import sys
from pathlib import Path

SAMPLES_DIR = Path(__file__).parent.parent / "samples" / "real_invoices"


def check_kaggle_setup():
    """Check if Kaggle CLI is configured."""
    kaggle_json = Path.home() / ".kaggle" / "kaggle.json"

    if not kaggle_json.exists():
        print("❌ Kaggle API not configured.")
        print("\nSetup instructions:")
        print("1. Go to kaggle.com/account")
        print("2. Click 'Create New Token' under API section")
        print("3. Move downloaded kaggle.json to ~/.kaggle/")
        print("4. chmod 600 ~/.kaggle/kaggle.json")
        return False

    return True


def download_dataset(dataset_name: str, output_dir: Path):
    """Download a Kaggle dataset."""
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n📥 Downloading {dataset_name}...")

    try:
        result = subprocess.run(
            ["kaggle", "datasets", "download", "-d", dataset_name, "-p", str(output_dir), "--unzip"],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"✅ Downloaded to {output_dir}")
            return True
        else:
            print(f"❌ Error: {result.stderr}")
            return False

    except FileNotFoundError:
        print("❌ Kaggle CLI not installed. Run: pip install kaggle")
        return False


def list_downloaded_files(directory: Path):
    """List downloaded invoice files."""
    if not directory.exists():
        return []

    files = list(directory.glob("**/*.pdf")) + list(directory.glob("**/*.jpg")) + list(directory.glob("**/*.png"))
    return files


def main():
    print("="*60)
    print("  Kaggle Invoice Dataset Downloader")
    print("="*60)

    if not check_kaggle_setup():
        sys.exit(1)

    # Available datasets
    datasets = [
        ("ahtisham225/invoices-dataset", "General invoices (recommended)"),
        ("jpmiller/layoutlm-invoices", "LayoutLM annotated invoices"),
    ]

    print("\nAvailable datasets:")
    for i, (name, desc) in enumerate(datasets, 1):
        print(f"  {i}. {name}")
        print(f"     {desc}")

    # Download first dataset by default
    print(f"\nDownloading: {datasets[0][0]}")

    success = download_dataset(datasets[0][0], SAMPLES_DIR)

    if success:
        files = list_downloaded_files(SAMPLES_DIR)
        print(f"\n✅ Downloaded {len(files)} invoice files")

        if files:
            print("\nSample files:")
            for f in files[:5]:
                print(f"  - {f.name}")
            if len(files) > 5:
                print(f"  ... and {len(files) - 5} more")

        print(f"\nFiles saved to: {SAMPLES_DIR}")
        print("\nNext: Run the OCR demo with:")
        print("  python demos/ocr_invoice_demo.py")


if __name__ == "__main__":
    main()
