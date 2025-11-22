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
            error_msg = result.stderr.lower()
            if "403" in error_msg or "forbidden" in error_msg:
                print(f"❌ 403 Forbidden - Dataset requires license acceptance or is private")
                print(f"   Visit: https://www.kaggle.com/datasets/{dataset_name}")
                print(f"   Accept the license, then retry")
            elif "404" in error_msg:
                print(f"❌ Dataset not found: {dataset_name}")
            else:
                print(f"❌ Error: {result.stderr}")
            return False

    except FileNotFoundError:
        print("❌ Kaggle CLI not installed. Run: pip install kaggle")
        return False


def create_sample_invoices(output_dir: Path):
    """Create sample invoice PDFs as fallback when Kaggle fails."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        print("❌ PyMuPDF not installed. Run: pip install pymupdf")
        return False

    output_dir.mkdir(parents=True, exist_ok=True)

    # Sample invoice data
    invoices = [
        {
            "number": "INV-2024-001",
            "vendor": "ACME Corporation",
            "date": "January 15, 2024",
            "items": [("Widget Type A", 100, 12.50), ("Widget Type B", 50, 25.00)],
            "total": 2575.00,
        },
        {
            "number": "INV-2024-002",
            "vendor": "TechSupply Inc",
            "date": "January 18, 2024",
            "items": [("Server Maintenance", 1, 5000.00), ("Software License", 10, 150.00)],
            "total": 6500.00,
        },
        {
            "number": "INV-2024-003",
            "vendor": "GlobalTech Solutions",
            "date": "January 20, 2024",
            "items": [("Cloud Setup", 1, 3500.00), ("Configuration", 5, 150.00)],
            "total": 4250.00,
        },
    ]

    print(f"\n📄 Creating {len(invoices)} sample invoice PDFs...")

    for inv in invoices:
        doc = fitz.open()
        page = doc.new_page()

        # Header
        page.insert_text((50, 50), inv["vendor"], fontsize=20, fontname="helv")
        page.insert_text((50, 80), f"Invoice #{inv['number']}", fontsize=14)
        page.insert_text((50, 100), f"Date: {inv['date']}", fontsize=10)

        # Items
        y = 150
        page.insert_text((50, y), "Description", fontsize=10, fontname="helv")
        page.insert_text((300, y), "Qty", fontsize=10)
        page.insert_text((350, y), "Price", fontsize=10)
        page.insert_text((450, y), "Total", fontsize=10)

        y += 20
        for desc, qty, price in inv["items"]:
            page.insert_text((50, y), desc, fontsize=10)
            page.insert_text((300, y), str(qty), fontsize=10)
            page.insert_text((350, y), f"${price:.2f}", fontsize=10)
            page.insert_text((450, y), f"${qty * price:.2f}", fontsize=10)
            y += 15

        # Total
        y += 20
        page.insert_text((350, y), "Total:", fontsize=12, fontname="helv")
        page.insert_text((450, y), f"${inv['total']:.2f}", fontsize=12)

        # Save
        filename = output_dir / f"{inv['number']}.pdf"
        doc.save(filename)
        doc.close()
        print(f"  ✓ Created {filename.name}")

    return True


def list_downloaded_files(directory: Path):
    """List downloaded invoice files."""
    if not directory.exists():
        return []

    files = list(directory.glob("**/*.pdf")) + list(directory.glob("**/*.jpg")) + list(directory.glob("**/*.png"))
    return files


def main():
    print("="*60)
    print("  Invoice Dataset Downloader")
    print("="*60)

    # Check for --generate flag to skip Kaggle
    if "--generate" in sys.argv:
        print("\nGenerating sample invoices (skipping Kaggle)...")
        success = create_sample_invoices(SAMPLES_DIR)
        if success:
            files = list_downloaded_files(SAMPLES_DIR)
            print(f"\n✅ Created {len(files)} sample invoice PDFs")
            print(f"\nFiles saved to: {SAMPLES_DIR}")
            print("\nNext: Run the OCR demo with:")
            print("  python demos/ocr_invoice_demo.py")
        return

    # Try Kaggle first
    kaggle_available = check_kaggle_setup()

    if kaggle_available:
        # Available datasets
        datasets = [
            ("ahtisham225/invoices-dataset", "General invoices"),
            ("jpmiller/layoutlm-invoices", "LayoutLM annotated invoices"),
        ]

        print("\nTrying Kaggle datasets...")

        success = False
        for dataset_name, desc in datasets:
            print(f"\nAttempting: {dataset_name}")
            success = download_dataset(dataset_name, SAMPLES_DIR)
            if success:
                break

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
            return

    # Fallback: Generate sample invoices
    print("\n" + "="*60)
    print("  Kaggle download failed - using fallback")
    print("="*60)
    print("\nGenerating sample invoice PDFs locally...")

    success = create_sample_invoices(SAMPLES_DIR)

    if success:
        files = list_downloaded_files(SAMPLES_DIR)
        print(f"\n✅ Created {len(files)} sample invoice PDFs")
        print(f"\nFiles saved to: {SAMPLES_DIR}")
        print("\nNext: Run the OCR demo with:")
        print("  python demos/ocr_invoice_demo.py")
    else:
        print("\n❌ Could not create sample invoices")
        print("   Install PyMuPDF: pip install pymupdf")


if __name__ == "__main__":
    main()
