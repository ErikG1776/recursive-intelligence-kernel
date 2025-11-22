#!/usr/bin/env python3

"""
PDF OCR Extraction Demo
-----------------------
This demo converts ANY PDF (including scanned PDFs) into images using
pdftoppm, then runs Tesseract OCR to extract text.

Usage:
    python3 demos/pdf_live_processing_ocr_demo.py "/path/to/invoice.pdf"
"""

import os
import sys
import subprocess
import pytesseract
from PIL import Image


def pdf_to_images(pdf_path, output_prefix="ocr_temp"):
    """Convert PDF → PNG images using pdftoppm."""
    print("📄 Converting PDF pages to images...")

    cmd = [
        "pdftoppm",
        pdf_path,
        output_prefix,
        "-png",
    ]

    subprocess.run(cmd, check=True)

    images = sorted([f for f in os.listdir(".") if f.startswith(output_prefix) and f.endswith(".png")])
    if not images:
        raise RuntimeError("No images were produced by pdftoppm — is the PDF valid?")

    print(f"🖼️  Generated {len(images)} page-images.")
    return images


def run_ocr_on_images(images):
    """Run OCR on each image and combine text."""
    full_text = ""

    for img in images:
        print(f"🔍 Running OCR on {img}...")
        text = pytesseract.image_to_string(Image.open(img))
        full_text += f"\n\n===== PAGE {img} =====\n"
        full_text += text

    return full_text


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 pdf_live_processing_ocr_demo.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"❌ File not found: {pdf_path}")
        sys.exit(1)

    try:
        images = pdf_to_images(pdf_path)
        text = run_ocr_on_images(images)

        print("\n\n======================================================================")
        print("📝 OCR OUTPUT")
        print("======================================================================")
        print(text[:4000])  # print first 4000 characters
        print("\n...(truncated)\n")

        with open("ocr_output.txt", "w") as f:
            f.write(text)

        print("💾 Saved full OCR text to ocr_output.txt")
        print("✅ Completed OCR successfully.")

    finally:
        # Clean up temp images
        for f in os.listdir("."):
            if f.startswith("ocr_temp") and f.endswith(".png"):
                os.remove(f)


if __name__ == "__main__":
    main()