"""
RIK SDK - Web Scraping Selector Recovery Examples
==================================================

Examples showing how to use RIK for self-healing web scrapers.
"""

from rik_sdk import RIKClient


def example_recover_broken_selector():
    """Recover a broken CSS selector after website redesign."""
    print("=" * 60)
    print("Example: Recover Broken Selector")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    # Simulate a website redesign
    # Old HTML (selector worked):
    # <div class="old-price">$99.99</div>
    #
    # New HTML (selector broken):
    new_html = """
    <html>
    <body>
        <div class="product-card">
            <h2 class="product-title">Premium Widget</h2>
            <div class="pricing-container">
                <span class="price-tag price-current">$99.99</span>
                <span class="price-tag price-original">$129.99</span>
            </div>
            <button class="add-to-cart">Add to Cart</button>
        </div>
    </body>
    </html>
    """

    failed_selector = ".old-price"  # This selector no longer works
    url = "https://example.com/products/widget"

    print(f"\n🔍 Attempting to recover selector:")
    print(f"   Failed Selector: {failed_selector}")
    print(f"   URL: {url}")
    print(f"   Target: Product price")

    # Ask RIK to recover the selector
    result = client.recover_selector(
        failed_selector=failed_selector,
        html=new_html,
        url=url,
        context={"target_element": "product price", "example_value": "$99.99"}
    )

    print(f"\n✓ Selector Recovered!")
    print(f"   New Selector: {result.recovered_selector}")
    print(f"   Type: {result.selector_type}")
    print(f"   Confidence: {result.confidence_score:.1%}")
    print(f"   Processing Time: {result.processing_time_seconds:.3f}s")

    print(f"\n💡 Reasoning:")
    print(f"   {result.reasoning}")

    if result.fallback_strategies:
        print(f"\n🔄 Fallback Strategies:")
        for strategy in result.fallback_strategies:
            print(f"   - {strategy}")

    # Test the new selector
    print(f"\n🧪 Testing new selector...")
    test_result = client.test_selector(
        selector=result.recovered_selector,
        html=new_html,
        selector_type=result.selector_type
    )

    if test_result['success']:
        print(f"   ✓ New selector works!")
        print(f"   Matched {test_result['element_count']} element(s)")
        if test_result.get('sample_text'):
            print(f"   Sample text: {test_result['sample_text']}")
    else:
        print(f"   ✗ New selector failed")

    return result


def example_test_selector():
    """Test if a selector works on given HTML."""
    print("\n" + "=" * 60)
    print("Example: Test Selector")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    html = """
    <div class="products">
        <div class="product" data-id="1">
            <h3 class="product-name">Widget A</h3>
            <span class="product-price">$29.99</span>
        </div>
        <div class="product" data-id="2">
            <h3 class="product-name">Widget B</h3>
            <span class="product-price">$39.99</span>
        </div>
    </div>
    """

    selectors_to_test = [
        (".product-price", "css"),
        (".product-name", "css"),
        (".nonexistent-class", "css"),
        ("//span[@class='product-price']", "xpath"),
    ]

    print("\n🧪 Testing Selectors:\n")

    for selector, selector_type in selectors_to_test:
        result = client.test_selector(
            selector=selector,
            html=html,
            selector_type=selector_type
        )

        status = "✓" if result['success'] else "✗"
        count = result.get('element_count', 0)
        print(f"{status} {selector} ({selector_type}): {count} element(s) matched")


def example_multi_selector_recovery():
    """Recover multiple selectors for a complete scraper."""
    print("\n" + "=" * 60)
    print("Example: Multi-Selector Recovery")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    html = """
    <div class="listing-container">
        <article class="job-post" data-job-id="12345">
            <header>
                <h2 class="job-title">Senior Python Developer</h2>
                <div class="company-info">
                    <span class="company-name">Tech Corp Inc.</span>
                    <span class="location-badge">San Francisco, CA</span>
                </div>
            </header>
            <div class="job-details">
                <span class="salary-range">$120k - $180k</span>
                <span class="job-type">Full-time</span>
            </div>
        </article>
    </div>
    """

    # Old selectors that broke after redesign
    failed_selectors = {
        "title": ".title",
        "company": ".company",
        "location": ".location",
        "salary": ".pay",
    }

    print(f"\n🔄 Recovering {len(failed_selectors)} broken selectors...")

    recovered = {}
    for field, old_selector in failed_selectors.items():
        print(f"\n   Recovering: {field} (was: {old_selector})")

        result = client.recover_selector(
            failed_selector=old_selector,
            html=html,
            url="https://jobs.example.com/listing/12345",
            context={"target_element": f"job {field}"}
        )

        recovered[field] = result.recovered_selector
        confidence_bar = "█" * int(result.confidence_score * 10)
        print(f"   ✓ New: {result.recovered_selector}")
        print(f"   Confidence: {confidence_bar} {result.confidence_score:.0%}")

    print(f"\n📋 Updated Scraper Configuration:")
    print(f"   selectors = {{")
    for field, selector in recovered.items():
        print(f"       '{field}': '{selector}',")
    print(f"   }}")


def example_context_aware_recovery():
    """Use context to improve selector recovery accuracy."""
    print("\n" + "=" * 60)
    print("Example: Context-Aware Selector Recovery")
    print("=" * 60)

    client = RIKClient("http://localhost:8000")

    html = """
    <div class="product-page">
        <div class="price-section">
            <span class="price price-sale">$79.99</span>
            <span class="price price-regular">$99.99</span>
            <span class="price price-shipping">$5.99</span>
        </div>
    </div>
    """

    failed_selector = ".price"  # Ambiguous - matches multiple prices

    # Provide context to help RIK pick the right price
    result = client.recover_selector(
        failed_selector=failed_selector,
        html=html,
        url="https://shop.example.com/product/123",
        context={
            "target_element": "current sale price (not regular or shipping)",
            "example_value": "$79.99",
            "exclude_classes": ["price-regular", "price-shipping"]
        }
    )

    print(f"\n🎯 Context-Aware Recovery:")
    print(f"   Old (ambiguous): {failed_selector}")
    print(f"   New (specific): {result.recovered_selector}")
    print(f"   Confidence: {result.confidence_score:.1%}")
    print(f"\n💡 Reasoning:")
    print(f"   {result.reasoning}")


if __name__ == "__main__":
    print("\n🕷️ RIK SDK - Web Scraping Selector Recovery Examples\n")

    try:
        example_recover_broken_selector()
        example_test_selector()
        example_multi_selector_recovery()
        example_context_aware_recovery()

        print("\n" + "=" * 60)
        print("✓ All web scraping examples completed!")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
