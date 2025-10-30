"""
selector_recovery.py | RIK Web Scraper Self-Healing Module
-----------------------------------------------------------
Provides intelligent fallback strategies for failed CSS/XPath selectors.
Used for demonstrating RIK's self-healing capabilities with real web scraping.
"""

from typing import List, Dict, Any
from bs4 import BeautifulSoup
import re
from rik_fail_safe.fallback_core import diagnose, simulate_counterfactuals
import memory


def generate_alternative_selectors(failed_selector: str, html: str, target_content: str = None) -> List[Dict[str, Any]]:
    """
    Generate alternative CSS/XPath selectors when original selector fails.

    Args:
        failed_selector: The selector that didn't work
        html: HTML content to analyze
        target_content: Optional - if known, use to validate alternatives

    Returns:
        List of alternative selectors with confidence scores
    """
    alternatives = []

    try:
        soup = BeautifulSoup(html, 'html.parser')

        # Strategy 1: Try common variations of the failed selector
        if failed_selector.startswith('.'):
            # Failed class selector - try variations
            class_name = failed_selector[1:]
            alternatives.extend([
                {"type": "css", "selector": f"[class*='{class_name}']", "strategy": "Partial class match", "confidence": 0.85},
                {"type": "css", "selector": f".{class_name}-title", "strategy": "Common suffix pattern", "confidence": 0.70},
                {"type": "css", "selector": f".{class_name}-link", "strategy": "Alternate naming", "confidence": 0.65},
            ])

        elif failed_selector.startswith('#'):
            # Failed ID selector - try data attributes or classes
            id_name = failed_selector[1:]
            alternatives.extend([
                {"type": "css", "selector": f"[data-id='{id_name}']", "strategy": "Data attribute fallback", "confidence": 0.80},
                {"type": "css", "selector": f"[id*='{id_name}']", "strategy": "Partial ID match", "confidence": 0.75},
            ])

        # Strategy 2: Analyze actual HTML structure and suggest common patterns
        # Look for title/heading patterns
        if 'title' in failed_selector.lower():
            alternatives.extend([
                {"type": "css", "selector": "h1", "strategy": "Primary heading", "confidence": 0.75},
                {"type": "css", "selector": "h1 a", "strategy": "Heading link", "confidence": 0.80},
                {"type": "css", "selector": "[class*='title']", "strategy": "Any title class", "confidence": 0.85},
                {"type": "css", "selector": ".entry-title", "strategy": "WordPress pattern", "confidence": 0.60},
                {"type": "xpath", "selector": "//h1//a | //h2//a", "strategy": "Heading links XPath", "confidence": 0.70},
            ])

        # Look for link patterns
        if 'link' in failed_selector.lower() or 'href' in failed_selector.lower():
            alternatives.extend([
                {"type": "css", "selector": "a[href]", "strategy": "Any link", "confidence": 0.50},
                {"type": "css", "selector": ".link", "strategy": "Link class", "confidence": 0.65},
                {"type": "xpath", "selector": "//a[@href]", "strategy": "Links with href", "confidence": 0.60},
            ])

        # Strategy 3: Test against actual HTML to see what exists
        existing_classes = set()
        for tag in soup.find_all(class_=True):
            if isinstance(tag.get('class'), list):
                existing_classes.update(tag.get('class'))

        # Suggest classes that actually exist
        for cls in existing_classes:
            if any(keyword in cls.lower() for keyword in ['title', 'headline', 'entry', 'post', 'article']):
                alternatives.append({
                    "type": "css",
                    "selector": f".{cls}",
                    "strategy": f"Detected class in HTML",
                    "confidence": 0.90
                })

        # Strategy 4: Generic fallback strategies
        alternatives.extend([
            {"type": "css", "selector": "article h1, article h2", "strategy": "Article headers", "confidence": 0.55},
            {"type": "css", "selector": "[role='main'] h1", "strategy": "Main content heading", "confidence": 0.60},
            {"type": "xpath", "selector": "//*[contains(@class, 'title') or contains(@class, 'headline')]", "strategy": "XPath keyword search", "confidence": 0.65},
        ])

    except Exception as e:
        print(f"[WARN] Error analyzing HTML: {e}")
        # Return safe fallback strategies even if parsing fails
        alternatives.extend([
            {"type": "css", "selector": "h1", "strategy": "Safe fallback: H1", "confidence": 0.50},
            {"type": "css", "selector": "h1 a, h2 a", "strategy": "Safe fallback: Heading links", "confidence": 0.55},
        ])

    # Remove duplicates and sort by confidence
    seen = set()
    unique_alternatives = []
    for alt in alternatives:
        key = (alt['type'], alt['selector'])
        if key not in seen:
            seen.add(key)
            unique_alternatives.append(alt)

    # Sort by confidence (highest first)
    unique_alternatives.sort(key=lambda x: x['confidence'], reverse=True)

    # Return top 5 alternatives
    return unique_alternatives[:5]


def recover_selector(failed_selector: str, html: str, url: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Complete selector recovery workflow with RIK integration.

    Args:
        failed_selector: Selector that failed
        html: HTML content
        url: URL being scraped
        context: Additional context about the failure

    Returns:
        Recovery result with alternative selectors and metadata
    """
    # Diagnose the failure
    diagnosis = diagnose(
        Exception(f"Selector '{failed_selector}' returned no elements"),
        {
            "selector": failed_selector,
            "url": url,
            "html_length": len(html),
            "context": context or {}
        }
    )

    # Generate alternative selectors
    alternatives = generate_alternative_selectors(failed_selector, html)

    # Simulate success probability for each alternative
    strategy_descriptions = [
        f"{alt['strategy']}: {alt['selector']}"
        for alt in alternatives
    ]
    simulations = simulate_counterfactuals(strategy_descriptions)

    # Combine alternatives with simulations
    for i, alt in enumerate(alternatives):
        if i < len(simulations):
            alt['predicted_success'] = simulations[i]['predicted_success']
        else:
            alt['predicted_success'] = alt['confidence']

    # Save to memory for learning
    memory.save_episode(
        task=f"Selector recovery: {failed_selector} on {url}",
        result="alternatives_generated",
        reflection=f"Generated {len(alternatives)} alternative selectors. Top strategy: {alternatives[0]['strategy']}"
    )

    return {
        "success": True,
        "original_selector": failed_selector,
        "url": url,
        "diagnosis": diagnosis,
        "alternatives": alternatives,
        "recommended": alternatives[0] if alternatives else None,
        "total_alternatives": len(alternatives)
    }


def test_selector(selector: str, html: str, selector_type: str = "css") -> Dict[str, Any]:
    """
    Test if a selector works on given HTML.

    Args:
        selector: CSS or XPath selector to test
        html: HTML content
        selector_type: 'css' or 'xpath'

    Returns:
        Dict with success status and extracted elements
    """
    try:
        soup = BeautifulSoup(html, 'html.parser')

        if selector_type == "css":
            elements = soup.select(selector)
        elif selector_type == "xpath":
            # Note: BeautifulSoup doesn't support XPath natively
            # In production, use lxml for XPath support
            return {"success": False, "error": "XPath testing requires lxml", "count": 0}
        else:
            return {"success": False, "error": f"Unknown selector type: {selector_type}", "count": 0}

        return {
            "success": len(elements) > 0,
            "count": len(elements),
            "samples": [elem.get_text(strip=True)[:100] for elem in elements[:3]]
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "count": 0
        }


# Example usage for testing
if __name__ == "__main__":
    # Test with sample HTML
    sample_html = """
    <html>
        <body>
            <div class="content">
                <h1 class="main-title">Test Article</h1>
                <div class="article-body">
                    <p>Content here</p>
                </div>
            </div>
        </body>
    </html>
    """

    result = recover_selector(".old-title-class", sample_html, "https://example.com/test")
    print("Recovery Result:")
    print(f"  Found {result['total_alternatives']} alternatives")
    print(f"  Recommended: {result['recommended']}")
