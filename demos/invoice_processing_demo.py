"""
invoice_processing_demo.py | RIK Invoice Processing Demo
------------------------------------------------------------
Demonstrates RIK's cognitive loop on real business tasks:
- Invoice extraction
- PO validation
- Self-healing on mismatches
"""

import json
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import recursive_run

SAMPLES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "samples")


def load_sample(filename: str) -> dict:
    """Load a sample JSON file."""
    path = os.path.join(SAMPLES_DIR, filename)
    with open(path) as f:
        return json.load(f)


def demo_invoice_extraction():
    """Demo: Extract fields from invoice."""
    print("\n" + "="*60)
    print("DEMO 1: Invoice Field Extraction")
    print("="*60)

    invoice = load_sample("acme_invoice.json")
    print(f"\nLoaded invoice: {invoice['invoice_number']} from {invoice['vendor']}")
    print(f"Total: ${invoice['total']}")

    # Run through RIK
    task = f"Extract invoice total from {invoice['vendor']} invoice {invoice['invoice_number']}"
    result = recursive_run(task)

    print(f"\nRIK Result: {result['status']}")
    print(f"Fitness Score: {result.get('fitness_score', 'N/A')}")
    return result


def demo_po_validation():
    """Demo: Validate invoice against PO."""
    print("\n" + "="*60)
    print("DEMO 2: PO Validation")
    print("="*60)

    invoice = load_sample("vendor_bill.json")
    pos = load_sample("purchase_orders.json")

    # Find matching PO
    matching_po = None
    for po in pos["purchase_orders"]:
        if po["po_number"] == invoice["po_number"]:
            matching_po = po
            break

    if matching_po:
        print(f"\nInvoice: {invoice['invoice_number']} - ${invoice['total']}")
        print(f"PO: {matching_po['po_number']} - Approved: ${matching_po['approved_amount']}")

        if invoice['total'] <= matching_po['approved_amount']:
            print("Status: WITHIN BUDGET")
        else:
            print(f"Status: OVER BUDGET by ${invoice['total'] - matching_po['approved_amount']}")

    # Run through RIK
    task = f"Validate invoice {invoice['invoice_number']} against PO {invoice['po_number']}"
    result = recursive_run(task)

    print(f"\nRIK Result: {result['status']}")
    return result


def demo_fallback_recovery():
    """Demo: Trigger fallback system with intentional error."""
    print("\n" + "="*60)
    print("DEMO 3: Fallback Recovery (Intentional Failure)")
    print("="*60)

    # This task contains 'error' to trigger fallback
    task = "Process invoice with error in vendor lookup"
    result = recursive_run(task)

    print(f"\nRIK Result: {result['status']}")
    print(f"Fallback Engaged: {result.get('fallback_engaged', False)}")
    print(f"Reflection: {result.get('reflection', 'N/A')}")
    return result


def demo_batch_processing():
    """Demo: Process multiple invoices to show learning."""
    print("\n" + "="*60)
    print("DEMO 4: Batch Processing (Cross-Task Learning)")
    print("="*60)

    tasks = [
        "Extract line items from acme_invoice.json",
        "Calculate tax amount from vendor_bill.json",
        "Reconcile payment terms across all invoices",
        "Route invoice INV-2024-001 for approval",
    ]

    results = []
    for i, task in enumerate(tasks, 1):
        print(f"\n[{i}/{len(tasks)}] {task}")
        result = recursive_run(task)
        results.append(result)
        print(f"  Status: {result['status']} | Fitness: {result.get('fitness_score', 'N/A'):.3f}")

    # Summary
    successes = sum(1 for r in results if r['status'] == 'success')
    print(f"\n--- Batch Complete: {successes}/{len(tasks)} successful ---")
    return results


if __name__ == "__main__":
    print("\n" + "#"*60)
    print("#  RIK Invoice Processing Demo")
    print("#  Recursive Intelligence Kernel for RPA")
    print("#"*60)

    # Run all demos
    demo_invoice_extraction()
    demo_po_validation()
    demo_fallback_recovery()
    demo_batch_processing()

    print("\n" + "="*60)
    print("Demo Complete - Check data/memory.db for learned episodes")
    print("="*60 + "\n")
