"""
RIK SDK - Invoice Processing Examples
======================================

Examples showing how to use RIK for intelligent invoice exception handling.
"""

import json
from rik_sdk import RIKClient
from rik_sdk.exceptions import RIKValidationError


def example_process_invoice_with_exceptions():
    """Process an invoice with multiple exceptions."""
    print("=" * 60)
    print("Example: Invoice Processing with Exceptions")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    # Invoice with exceptions (missing PO, low confidence)
    invoice_data = {
        "invoice_number": "INV-2024-001",
        "vendor_name": "Acme Corporation",
        "amount": 4500.00,
        "date": "2024-11-01",
        "po_number": "",  # Missing PO number!
        "extraction_confidence": 0.15  # Low OCR confidence!
    }

    print(f"\n📄 Processing Invoice:")
    print(f"   Invoice #: {invoice_data['invoice_number']}")
    print(f"   Vendor: {invoice_data['vendor_name']}")
    print(f"   Amount: ${invoice_data['amount']:,.2f}")
    print(f"   PO Number: {'(MISSING)' if not invoice_data['po_number'] else invoice_data['po_number']}")
    print(f"   Confidence: {invoice_data['extraction_confidence']:.0%}")

    # Convert to PDF content (JSON string)
    pdf_content = json.dumps(invoice_data)

    # Process invoice
    result = client.process_invoice(
        pdf_content=pdf_content,
        invoice_id=invoice_data['invoice_number']
    )

    print(f"\n🧠 RIK Analysis:")
    print(f"   Final Action: {result.final_action.upper()}")
    print(f"   Confidence: {result.confidence_score:.1%}")
    print(f"   Processing Time: {result.processing_time_seconds:.3f}s")
    print(f"   Exceptions Found: {result.exceptions_found}")
    print(f"   Exceptions Resolved: {result.exceptions_resolved}")
    print(f"   Similar Cases: {result.similar_cases_found}")
    print(f"   Strategies Simulated: {result.strategies_simulated}")

    print(f"\n💡 Reasoning:")
    print(f"   {result.reasoning}")

    print(f"\n📊 RPA Comparison:")
    if result.traditional_rpa_would_fail:
        print(f"   ✗ Traditional RPA: WOULD FAIL")
        print(f"   ✓ RIK: SUCCESS")
    else:
        print(f"   ✓ Both would succeed")

    # Check if needs review
    if result.needs_human_review():
        print(f"\n⚠️  Escalated to human review")
    else:
        print(f"\n✓  Fully automated (no human review needed)")

    return result


def example_batch_processing():
    """Process multiple invoices in batch."""
    print("\n" + "=" * 60)
    print("Example: Batch Invoice Processing")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    invoices = [
        {"invoice_number": "INV-001", "vendor_name": "Acme Corp", "amount": 1000, "po_number": "PO-123"},
        {"invoice_number": "INV-002", "vendor_name": "TechCo", "amount": 5000, "po_number": ""},  # Missing PO
        {"invoice_number": "INV-003", "vendor_name": "SupplyCo", "amount": 15000, "po_number": "PO-456"},
        {"invoice_number": "INV-004", "vendor_name": "Unknown Vendor", "amount": 2500, "po_number": ""},  # Unknown + missing PO
    ]

    results = []
    automated_count = 0
    escalated_count = 0

    for invoice in invoices:
        pdf_content = json.dumps(invoice)
        result = client.process_invoice(pdf_content, invoice_id=invoice['invoice_number'])
        results.append((invoice, result))

        if result.needs_human_review():
            escalated_count += 1
        else:
            automated_count += 1

    print(f"\n📊 Batch Processing Results:")
    print(f"   Total Invoices: {len(invoices)}")
    print(f"   Fully Automated: {automated_count} ({automated_count/len(invoices):.0%})")
    print(f"   Escalated: {escalated_count} ({escalated_count/len(invoices):.0%})")

    print(f"\n📋 Individual Results:")
    for invoice, result in results:
        status_icon = "✓" if not result.needs_human_review() else "⚠️"
        print(f"   {status_icon} {invoice['invoice_number']}: {result.final_action.upper()} "
              f"(confidence: {result.confidence_score:.0%})")


def example_get_invoice_stats():
    """Get ROI and automation statistics."""
    print("\n" + "=" * 60)
    print("Example: Invoice Processing ROI Stats")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    stats = client.get_invoice_stats()

    print(f"\n📊 Automation Statistics:")
    print(f"   Total Invoices Processed: {stats.total_invoices_processed:,}")
    print(f"   Invoices with Exceptions: {stats.invoices_with_exceptions:,}")
    print(f"   Auto-Resolved: {stats.exceptions_auto_resolved:,}")
    print(f"   Escalated: {stats.exceptions_escalated:,}")

    print(f"\n📈 Performance Comparison:")
    print(f"   RIK Automation Rate: {stats.automation_rate:.1%}")
    print(f"   Traditional RPA Rate: {stats.traditional_rpa_automation_rate:.1%}")
    print(f"   Improvement: {stats.automation_improvement}")

    print(f"\n💰 Financial Impact:")
    print(f"   Annual Savings: ${stats.annual_savings_usd:,.2f}")

    # Calculate per-invoice savings
    if stats.total_invoices_processed > 0:
        per_invoice_savings = stats.annual_savings_usd / stats.total_invoices_processed
        print(f"   Savings per Invoice: ${per_invoice_savings:.2f}")


def example_error_handling():
    """Demonstrate validation error handling."""
    print("\n" + "=" * 60)
    print("Example: Error Handling")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    # Try to process with invalid data
    try:
        result = client.process_invoice(
            pdf_content="",  # Empty content - should fail validation
            invoice_id="TEST-001"
        )
    except RIKValidationError as e:
        print(f"✓ Caught validation error: {e.message}")
        print(f"  Status Code: {e.status_code}")


if __name__ == "__main__":
    print("\n🧾 RIK SDK - Invoice Processing Examples\n")

    try:
        example_process_invoice_with_exceptions()
        example_batch_processing()
        example_get_invoice_stats()
        example_error_handling()

        print("\n" + "=" * 60)
        print("✓ All invoice processing examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
