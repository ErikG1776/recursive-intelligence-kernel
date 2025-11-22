#!/usr/bin/env python3
"""
RIK Invoice-from-OCR Demo
-------------------------
Takes OCR’d text (from Tesseract) and parses it into structured fields:

- Invoice number
- Vendor name
- Total amount due
- Invoice date
- PO number (if present)

This is the bridge between OCR → RIK reasoning engine.
"""

import re
import sys
from typing import Optional, Dict

# -------------------------------------------------------
# Generic safe extraction helper
# -------------------------------------------------------

def extract_field(pattern: str, text: str, flags=0) -> Optional[str]:
    """
    Try to extract a field using regex.
    If the pattern has a capture group, return group(1).
    If not, return the entire match (group(0)).
    """
    m = re.search(pattern, text, flags)
    if not m:
        return None

    # If the regex has a capturing group, use it
    if m.lastindex:
        return m.group(1).strip()

    # Otherwise return full match
    return m.group(0).strip()


# -------------------------------------------------------
# Field Parsers
# -------------------------------------------------------

def parse_invoice(text: str) -> Dict[str, Optional[str]]:
    fields = {}

    # ---------- Invoice Number ----------
    fields["invoice_number"] = extract_field(
        r"Invoice Number[:\s]*([A-Za-z0-9\-]+)",
        text
    ) or extract_field(
        r"Invoice\s*#?\s*([0-9]{5,})",
        text
    )

    # ---------- Vendor ----------
    # Try highly specific match first
    vendor = extract_field(r"(Level 3 Communications[^\n]+)", text)

    if not vendor:
        # Fallbacks
        vendor = extract_field(r"(HERITAGE INSURANCE[^\n]+)", text, re.IGNORECASE)
    if not vendor:
        vendor = extract_field(r"([A-Z][A-Za-z0-9&\.\,\-\s]+LLC)", text)
    if not vendor:
        vendor = extract_field(r"([A-Z][A-Za-z0-9&\.\,\-\s]+Inc)", text)
    if not vendor:
        vendor = extract_field(r"([A-Z][A-Za-z0-9&\.\,\-\s]+Company)", text)
    if not vendor:
        vendor = extract_field(r"([A-Z][A-Za-z0-9&\.\,\-\s]+Services)", text)

    fields["vendor"] = vendor if vendor else "Unknown Vendor"

    # ---------- Total Amount Due ----------
    fields["amount"] = extract_field(
        r"Total Amount Due[^0-9]*([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    ) or extract_field(
        r"Total\s*USD[^0-9]*([\d,]+\.\d{2})",
        text,
        re.IGNORECASE
    ) or extract_field(
        r"\bUSD\s*([\d,]+\.\d{2})",
        text
    )

    # ---------- Invoice Date ----------
    fields["invoice_date"] = extract_field(
        r"Invoice Date[:\s]*([A-Za-z]+\s+\d{1,2},\s+\d{4})",
        text
    ) or extract_field(
        r"Invoice Date[:\s]*(\d{1,2}/\d{1,2}/\d{4})",
        text
    )

    # ---------- PO Number ----------
    fields["po_number"] = extract_field(
        r"PO\s*Number[:\s]*([A-Za-z0-9\-]+)",
        text
    )

    return fields


# -------------------------------------------------------
# Pretty-print structured output like RIK
# -------------------------------------------------------

def print_result(fields: Dict[str, Optional[str]]):
    print("\n======================================================================")
    print("📄  OCR → Structured Invoice Fields")
    print("======================================================================")

    print(f"Invoice Number : {fields.get('invoice_number')}")
    print(f"Vendor         : {fields.get('vendor')}")
    print(f"Amount         : {fields.get('amount')}")
    print(f"Invoice Date   : {fields.get('invoice_date')}")
    print(f"PO Number      : {fields.get('po_number')}")

    print("\n======================================================================")
    print("🧠  NEXT STEP")
    print("======================================================================")
    print("These extracted fields can now be passed directly into the RIK")
    print("reasoning engine for:")
    print("  • Exception detection")
    print("  • Semantic normalization")
    print("  • Confidence scoring")
    print("  • Auto-repair suggestions")
    print("  • Final approval / rejection decision\n")


# -------------------------------------------------------
# Main
# -------------------------------------------------------

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 invoice_from_ocr_demo.py <ocr_text_file>")
        sys.exit(1)

    path = sys.argv[1]
    print(f"Reading OCR text from: {path}")

    with open(path, "r", encoding="utf-8") as f:
        text = f.read()

    fields = parse_invoice(text)
    print_result(fields)


if __name__ == "__main__":
    main()