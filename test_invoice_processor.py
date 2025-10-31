"""
Integration Tests for RIK Invoice Exception Processor
=====================================================

Tests the complete invoice processing workflow including:
- Field extraction
- Exception detection
- RIK reasoning
- Decision making
- API endpoints
"""

import json
import sys


def print_header(title):
    """Print a formatted test section header"""
    width = 60
    print("\n" + "=" * width)
    print(f"TEST: {title}")
    print("=" * width)


def print_result(test_name, passed, details=None):
    """Print test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"\n{status}: {test_name}")
    if details:
        print(f"  → {details}")


def test_field_extraction():
    """Test 1: Field extraction from invoice JSON"""
    print_header("Field Extraction")

    from invoice_processor import extract_invoice_fields

    # Test standard invoice
    invoice_json = json.dumps({
        "invoice_number": "INV-2024-001",
        "vendor_name": "Acme Corporation",
        "amount": 3240.00,
        "date": "10/30/2024",
        "po_number": "PO-2024-5521"
    })

    result = extract_invoice_fields(invoice_json)

    # Assertions
    tests_passed = 0
    total_tests = 5

    if result['invoice_number'] == "INV-2024-001":
        print_result("Invoice number extracted", True)
        tests_passed += 1
    else:
        print_result("Invoice number extracted", False, f"Got: {result.get('invoice_number')}")

    if result['vendor_name'] == "Acme Corporation":
        print_result("Vendor name extracted", True)
        tests_passed += 1
    else:
        print_result("Vendor name extracted", False, f"Got: {result.get('vendor_name')}")

    if result['amount'] == 3240.00:
        print_result("Amount extracted", True)
        tests_passed += 1
    else:
        print_result("Amount extracted", False, f"Got: {result.get('amount')}")

    if result['po_number'] == "PO-2024-5521":
        print_result("PO number extracted", True)
        tests_passed += 1
    else:
        print_result("PO number extracted", False, f"Got: {result.get('po_number')}")

    if result['confidence'] == 1.0:
        print_result("Confidence score correct", True)
        tests_passed += 1
    else:
        print_result("Confidence score correct", False, f"Got: {result.get('confidence')}")

    return tests_passed == total_tests


def test_exception_detection():
    """Test 2: Exception detection"""
    print_header("Exception Detection")

    from invoice_processor import detect_exceptions

    # Test invoice with missing PO
    invoice_data = {
        "invoice_number": "INV-2024-002",
        "vendor_name": "Acme Corporation",
        "amount": 4100.00,
        "date": "10/31/2024",
        "po_number": "",
        "confidence": 1.0
    }

    exceptions = detect_exceptions(invoice_data)

    # Should detect missing PO
    missing_po = any(e['type'] == 'missing_po_number' for e in exceptions)
    print_result("Missing PO detected", missing_po, f"Found {len(exceptions)} exceptions")

    # Test invoice with typo
    invoice_data_typo = {
        "invoice_number": "INV-2024-003",
        "vendor_name": "Microsft Corporation",  # Typo!
        "amount": 8500.00,
        "po_number": "PO-2024-5522",
        "confidence": 1.0
    }

    exceptions_typo = detect_exceptions(invoice_data_typo)
    typo_detected = any(e['type'] == 'vendor_name_typo' for e in exceptions_typo)
    print_result("Vendor typo detected", typo_detected, f"Found {len(exceptions_typo)} exceptions")

    # Test high amount
    invoice_data_high = {
        "invoice_number": "INV-2024-005",
        "vendor_name": "Amazon Web Services",
        "amount": 12500.00,
        "po_number": "PO-2024-5524",
        "confidence": 1.0
    }

    exceptions_high = detect_exceptions(invoice_data_high)
    high_amount = any(e['type'] == 'amount_over_threshold' for e in exceptions_high)
    print_result("High amount detected", high_amount, f"Amount: $12,500 over $5,000 threshold")

    return missing_po and typo_detected and high_amount


def test_vendor_similarity():
    """Test 3: Vendor name typo detection with similarity matching"""
    print_header("Vendor Similarity Matching")

    from invoice_processor import find_similar_vendor, BUSINESS_RULES

    # Test typo matching
    typo_vendor = "Microsft Corporation"
    matched, similarity = find_similar_vendor(typo_vendor, BUSINESS_RULES['trusted_vendors'])

    correct_match = matched == "Microsoft Corporation"
    high_confidence = similarity >= 0.85

    print_result("Matched Microsoft typo", correct_match, f"Matched: {matched}")
    print_result("High similarity score", high_confidence, f"Similarity: {similarity:.2%}")

    # Test another typo
    typo_vendor2 = "Salesforc Inc"
    matched2, similarity2 = find_similar_vendor(typo_vendor2, BUSINESS_RULES['trusted_vendors'])

    correct_match2 = matched2 == "Salesforce Inc"
    print_result("Matched Salesforce typo", correct_match2, f"Matched: {matched2}, Similarity: {similarity2:.2%}")

    return correct_match and high_confidence and correct_match2


def test_standard_invoice_processing():
    """Test 4: Complete processing of standard invoice (happy path)"""
    print_header("Standard Invoice Processing (Happy Path)")

    from invoice_processor import process_invoice

    # Load standard invoice
    with open('sample_invoices/1_standard_invoice.json', 'r') as f:
        invoice_content = f.read()

    result = process_invoice(invoice_content, invoice_id="TEST-001")

    # Assertions
    tests = []
    tests.append(("Invoice processed successfully", result is not None))
    tests.append(("No exceptions found", result['exceptions_found'] == 0))
    tests.append(("Auto-approved", result['final_action'] == 'approve'))
    tests.append(("Processing time recorded", result['processing_time_seconds'] > 0))
    tests.append(("Traditional RPA would succeed", not result['traditional_rpa_would_fail']))

    for test_name, passed in tests:
        print_result(test_name, passed)

    return all(t[1] for t in tests)


def test_missing_po_reasoning():
    """Test 5: RIK reasoning about missing PO number"""
    print_header("Missing PO Number Reasoning")

    from invoice_processor import process_invoice

    # Load invoice with missing PO
    with open('sample_invoices/2_invoice_no_po.json', 'r') as f:
        invoice_content = f.read()

    result = process_invoice(invoice_content, invoice_id="TEST-002")

    # Should detect exception but still approve (trusted vendor, low amount)
    tests = []
    tests.append(("Exception detected", result['exceptions_found'] > 0))
    tests.append(("Still approved", result['final_action'] == 'approve'))
    tests.append(("RIK reasoned about it", len(result['decisions']) > 0))
    tests.append(("Traditional RPA would fail", result['traditional_rpa_would_fail']))

    for test_name, passed in tests:
        print_result(test_name, passed)

    # Show reasoning
    if result['decisions']:
        reasoning = result['decisions'][0]['decision']['reasoning']
        print(f"\n💡 RIK Reasoning: {reasoning}")

    return all(t[1] for t in tests)


def test_vendor_typo_correction():
    """Test 6: Vendor name typo auto-correction"""
    print_header("Vendor Name Typo Auto-Correction")

    from invoice_processor import process_invoice

    # Load invoice with vendor typo
    with open('sample_invoices/3_invoice_vendor_typo.json', 'r') as f:
        invoice_content = f.read()

    result = process_invoice(invoice_content, invoice_id="TEST-003")

    # Should detect typo and auto-correct
    typo_exception = any(
        e['type'] == 'vendor_name_typo'
        for e in result['exceptions']
    )

    auto_corrected = result['invoice_data'].get('vendor_corrected', False)

    tests = []
    tests.append(("Typo detected", typo_exception))
    tests.append(("Vendor auto-corrected", auto_corrected))
    tests.append(("Corrected to Microsoft", "Microsoft Corporation" in result['invoice_data']['vendor_name']))
    tests.append(("Traditional RPA would fail", result['traditional_rpa_would_fail']))

    for test_name, passed in tests:
        print_result(test_name, passed)

    return all(t[1] for t in tests)


def test_high_amount_escalation():
    """Test 7: High amount invoice escalation"""
    print_header("High Amount Invoice Escalation")

    from invoice_processor import process_invoice

    # Load high amount invoice
    with open('sample_invoices/5_invoice_high_amount.json', 'r') as f:
        invoice_content = f.read()

    result = process_invoice(invoice_content, invoice_id="TEST-005")

    # Should escalate due to high amount
    tests = []
    tests.append(("Exception detected", result['exceptions_found'] > 0))
    tests.append(("Escalated (not auto-approved)", result['final_action'] == 'escalate'))
    tests.append(("Amount over threshold exception", any(
        e['type'] == 'amount_over_threshold'
        for e in result['exceptions']
    )))

    for test_name, passed in tests:
        print_result(test_name, passed)

    return all(t[1] for t in tests)


def test_multiple_exceptions():
    """Test 8: Multiple exceptions in one invoice"""
    print_header("Multiple Exceptions Handling")

    from invoice_processor import process_invoice

    # Load invoice with multiple exceptions
    with open('sample_invoices/6_invoice_multiple_exceptions.json', 'r') as f:
        invoice_content = f.read()

    result = process_invoice(invoice_content, invoice_id="TEST-006")

    # Should detect multiple exceptions
    tests = []
    tests.append(("Multiple exceptions detected", result['exceptions_found'] >= 2))
    tests.append(("RIK reasoned about each", len(result['decisions']) >= 2))
    tests.append(("Traditional RPA would fail", result['traditional_rpa_would_fail']))

    for test_name, passed in tests:
        print_result(test_name, passed)

    # Show all exceptions found
    print(f"\n📋 Exceptions found: {result['exceptions_found']}")
    for i, exc in enumerate(result['exceptions'], 1):
        print(f"   {i}. {exc['type']} - {exc['message']}")

    return all(t[1] for t in tests)


def test_automation_stats():
    """Test 9: Automation statistics calculation"""
    print_header("Automation Statistics")

    from invoice_processor import get_automation_stats

    stats = get_automation_stats()

    # Verify stats structure
    tests = []
    tests.append(("Stats returned", stats is not None))
    tests.append(("Total invoices tracked", stats.get('total_invoices_processed', 0) > 0))
    tests.append(("Exception rate calculated", stats.get('invoices_with_exceptions', 0) > 0))
    tests.append(("Auto-resolution tracked", stats.get('exceptions_auto_resolved', 0) > 0))
    tests.append(("Automation rate > traditional",
                  stats.get('automation_rate', 0) > stats.get('traditional_rpa_automation_rate', 0)))

    for test_name, passed in tests:
        print_result(test_name, passed)

    # Show key metrics
    print(f"\n📊 Key Metrics:")
    print(f"   Automation Rate (RIK): {stats.get('automation_rate', 0):.0%}")
    print(f"   Automation Rate (Traditional): {stats.get('traditional_rpa_automation_rate', 0):.0%}")
    print(f"   Improvement: {(stats.get('automation_rate', 0) - stats.get('traditional_rpa_automation_rate', 0)) * 100:.0f}%")

    return all(t[1] for t in tests)


def test_api_endpoints():
    """Test 10: API endpoints (requires running API)"""
    print_header("API Endpoints Integration")

    import requests

    # Check if API is running
    try:
        response = requests.get('http://localhost:8000/health', timeout=2)
        api_running = response.status_code == 200
    except:
        print_result("API is running", False, "Start API with: python3 rik_api.py")
        return False

    print_result("API is running", True, f"Version: {response.json().get('version')}")

    # Test process_invoice endpoint
    with open('sample_invoices/2_invoice_no_po.json', 'r') as f:
        invoice_data = json.load(f)

    try:
        response = requests.post(
            'http://localhost:8000/process_invoice',
            json={
                "pdf_content": json.dumps(invoice_data),
                "invoice_id": "API-TEST-001"
            },
            timeout=10
        )

        endpoint_works = response.status_code == 200
        print_result("POST /process_invoice works", endpoint_works)

        if endpoint_works:
            result = response.json()
            print(f"   → Final action: {result.get('final_action')}")
            print(f"   → Exceptions: {result.get('exceptions_found')}")

    except Exception as e:
        print_result("POST /process_invoice works", False, str(e))
        return False

    # Test invoice_stats endpoint
    try:
        response = requests.get('http://localhost:8000/invoice_stats', timeout=2)
        stats_works = response.status_code == 200
        print_result("GET /invoice_stats works", stats_works)

        if stats_works:
            stats = response.json()
            print(f"   → Monthly savings: ${stats.get('roi', {}).get('monthly_savings_usd', 0):,.0f}")

    except Exception as e:
        print_result("GET /invoice_stats works", False, str(e))
        return False

    return endpoint_works and stats_works


def main():
    """Run all integration tests"""
    print("\n" + "█" * 60)
    print("  RIK Invoice Exception Processor - Integration Tests")
    print("█" * 60)

    tests = [
        ("Field Extraction", test_field_extraction),
        ("Exception Detection", test_exception_detection),
        ("Vendor Similarity", test_vendor_similarity),
        ("Standard Invoice", test_standard_invoice_processing),
        ("Missing PO Reasoning", test_missing_po_reasoning),
        ("Vendor Typo Correction", test_vendor_typo_correction),
        ("High Amount Escalation", test_high_amount_escalation),
        ("Multiple Exceptions", test_multiple_exceptions),
        ("Automation Stats", test_automation_stats),
        ("API Endpoints", test_api_endpoints),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            passed = test_func()
            results.append((test_name, passed))
        except Exception as e:
            print(f"\n❌ EXCEPTION in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅" if passed else "❌"
        print(f"{status} {test_name}")

    print("\n" + "=" * 60)
    print(f"RESULT: {passed_count}/{total_count} tests passed")
    print("=" * 60)

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED!")
        print("\nYour RIK Invoice Exception Handler is ready for demo!")
        print("\nNext steps:")
        print("1. Start RIK API: python3 rik_api.py")
        print("2. Import n8n workflow: n8n_workflows/rik_invoice_exception_handler.json")
        print("3. Read demo guide: DEMO_INVOICE_GUIDE.md")
        print("4. Deliver your knockout demo! 🚀")
        return 0
    else:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed")
        print("Review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
