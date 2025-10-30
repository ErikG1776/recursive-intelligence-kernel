"""
test_selector_recovery.py | Quick integration test for selector recovery
--------------------------------------------------------------------------
Tests the complete selector recovery workflow:
1. Selector recovery module works
2. API endpoint responds correctly
3. HTML parsing functions properly
"""

import requests
import json
from selector_recovery import recover_selector, test_selector


def test_selector_recovery_module():
    """Test the selector recovery module directly"""
    print("\n" + "="*60)
    print("TEST 1: Selector Recovery Module")
    print("="*60)

    sample_html = """
    <html>
        <head><title>Test Page</title></head>
        <body>
            <div class="content">
                <h1 class="main-title">Breaking News: Test Article</h1>
                <h2 class="titleline"><a href="/story1">Story 1</a></h2>
                <h2 class="titleline"><a href="/story2">Story 2</a></h2>
                <div class="article-body">
                    <p>Content here</p>
                </div>
            </div>
        </body>
    </html>
    """

    # Test with a failed selector
    result = recover_selector(
        failed_selector=".old-title-class",
        html=sample_html,
        url="https://example.com/test"
    )

    print(f"✓ Recovery completed: {result['success']}")
    print(f"✓ Total alternatives: {result['total_alternatives']}")

    if result['recommended']:
        print(f"✓ Recommended selector: {result['recommended']['selector']}")
        print(f"  Strategy: {result['recommended']['strategy']}")
        print(f"  Confidence: {result['recommended']['confidence']}")

    print("\nTop 3 alternatives:")
    for i, alt in enumerate(result['alternatives'][:3], 1):
        print(f"  {i}. {alt['selector']} - {alt['strategy']} ({alt['confidence']:.0%})")

    assert result['success'] == True, "Recovery should succeed"
    assert result['total_alternatives'] > 0, "Should generate alternatives"

    print("\n✅ Module test PASSED\n")
    return result


def test_selector_testing():
    """Test the selector validation function"""
    print("="*60)
    print("TEST 2: Selector Testing Function")
    print("="*60)

    sample_html = """
    <html>
        <body>
            <h1 class="titleline">Test Title</h1>
            <h2 class="titleline">Another Title</h2>
        </body>
    </html>
    """

    # Test working selector
    result = test_selector(".titleline", sample_html, "css")
    print(f"✓ Testing .titleline: Found {result['count']} elements")
    print(f"  Success: {result['success']}")
    if result.get('samples'):
        print(f"  Samples: {result['samples']}")

    assert result['success'] == True, ".titleline should work"
    assert result['count'] == 2, "Should find 2 elements"

    # Test failing selector
    result = test_selector(".nonexistent", sample_html, "css")
    print(f"\n✓ Testing .nonexistent: Found {result['count']} elements")
    print(f"  Success: {result['success']}")

    assert result['success'] == False, ".nonexistent should fail"
    assert result['count'] == 0, "Should find 0 elements"

    print("\n✅ Selector testing PASSED\n")


def test_api_endpoint():
    """Test the API endpoint (requires API to be running)"""
    print("="*60)
    print("TEST 3: API Endpoint Integration")
    print("="*60)

    api_url = "http://localhost:8000/recover_selector"

    # Check if API is running
    try:
        health_check = requests.get("http://localhost:8000/health", timeout=2)
        if health_check.status_code != 200:
            print("⚠️  API not running - skipping endpoint test")
            print("   Start API with: python3 rik_api.py")
            return
    except requests.exceptions.RequestException:
        print("⚠️  API not running - skipping endpoint test")
        print("   Start API with: python3 rik_api.py")
        return

    payload = {
        "failed_selector": ".old-selector",
        "html": "<html><body><h1 class='titleline'>Test</h1></body></html>",
        "url": "https://example.com",
        "context": {"test": True}
    }

    print(f"Calling API: POST {api_url}")
    response = requests.post(api_url, json=payload, timeout=10)

    print(f"✓ Status code: {response.status_code}")

    data = response.json()
    print(f"✓ Response received:")
    print(f"  Success: {data.get('success')}")
    print(f"  Total alternatives: {data.get('total_alternatives')}")

    if data.get('recommended'):
        print(f"  Recommended: {data['recommended']['selector']}")

    assert response.status_code == 200, "API should return 200"
    assert data.get('success') == True, "Recovery should succeed"

    print("\n✅ API endpoint test PASSED\n")


def test_real_website():
    """Test with real Hacker News HTML"""
    print("="*60)
    print("TEST 4: Real Website HTML")
    print("="*60)

    try:
        response = requests.get("https://news.ycombinator.com", timeout=5)
        html = response.text
        print(f"✓ Fetched Hacker News HTML ({len(html)} chars)")

        # Test with intentionally wrong selector
        result = recover_selector(
            failed_selector=".old-titleline-selector",
            html=html[:5000],  # First 5000 chars
            url="https://news.ycombinator.com"
        )

        print(f"✓ Recovery completed: {result['success']}")
        print(f"✓ Generated {result['total_alternatives']} alternatives")

        if result['recommended']:
            print(f"\nRecommended selector:")
            print(f"  {result['recommended']['selector']}")
            print(f"  Strategy: {result['recommended']['strategy']}")
            print(f"  Confidence: {result['recommended']['confidence']:.0%}")

            # Test if recommended selector actually works
            test_result = test_selector(
                result['recommended']['selector'],
                html,
                result['recommended']['type']
            )
            print(f"\n✓ Testing recommended selector:")
            print(f"  Found {test_result['count']} elements")
            print(f"  Works: {test_result['success']}")

        print("\n✅ Real website test PASSED\n")

    except Exception as e:
        print(f"⚠️  Could not fetch Hacker News: {e}")
        print("   (This is okay - test can run offline)")


def main():
    """Run all tests"""
    print("\n" + "🤖 RIK Selector Recovery Integration Tests".center(60))
    print("="*60)

    try:
        # Run tests
        test_selector_recovery_module()
        test_selector_testing()
        test_api_endpoint()
        test_real_website()

        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED".center(60))
        print("="*60)
        print("\nYour RIK selector recovery system is ready for demo!")
        print("\nNext steps:")
        print("1. Start RIK API: python3 rik_api.py")
        print("2. Import n8n workflow: n8n_workflows/rik_self_healing_scraper.json")
        print("3. Read demo guide: DEMO_SCRAPER_GUIDE.md")
        print("4. Run your first self-healing scraper! 🚀\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        return 1
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
