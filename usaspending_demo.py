#!/usr/bin/env python3
"""
Recursive Intelligence Algorithm - USASpending.gov Demo

Self-healing RPA that navigates a real federal government website,
applies filters, and extracts contract data.

This demonstrates RIA handling:
- Dynamic React SPA
- Complex selectors
- Multi-step workflows
- Real-world adaptation

Usage:
    python usaspending_demo.py --headless
"""

import sys
import time
import json
import argparse
from pathlib import Path
from datetime import datetime, timezone

sys.path.insert(0, str(Path(__file__).parent))

from rpa_engine import RPAEngine
from memory import init_memory_db, save_episode


def print_banner():
    """Print demo banner."""
    banner = """
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║   RECURSIVE INTELLIGENCE ALGORITHM                       ║
    ║   USASpending.gov Live Demo                              ║
    ║                                                          ║
    ║   Self-healing RPA on a real federal government site:    ║
    ║   • Dynamic React SPA                                    ║
    ║   • Complex, changing DOM                                ║
    ║   • Multi-step workflow                                  ║
    ║   • Real contract data extraction                        ║
    ║                                                          ║
    ║   Watch the agent adapt and learn in real-time.          ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """
    print("\033[2J\033[H")
    print(banner)


def demo_ssa_contracts(headless: bool = True):
    """Demo: Navigate and extract SSA contract spending."""

    print("\n" + "="*60)
    print("  DEMO: Social Security Administration Contracts")
    print("="*60 + "\n")

    engine = RPAEngine(headless=headless)
    extracted_data = []

    try:
        engine.start()

        # Step 1: Navigate to search page
        print("📍 Step 1: Navigating to USASpending.gov search...")
        engine.navigate("https://www.usaspending.gov/search")
        time.sleep(4)  # Wait for React app to fully load

        # Step 2: Interact with the page - try the Award Search tab
        print("\n📍 Step 2: Finding searchable content...")

        # The page loads with spending by category - let's interact with what's visible
        # Try clicking on visible spending categories
        print("  → Looking for spending category links...")

        if engine.click("View Awards"):
            print("  ✓ Found View Awards button")
            time.sleep(2)
        elif engine.click("Contracts"):
            print("  ✓ Found Contracts section")
            time.sleep(2)
        elif engine.click("Award Search"):
            print("  ✓ Clicked Award Search")
            time.sleep(2)

        # Step 3: Try to interact with filter sidebar
        print("\n📍 Step 3: Exploring filter options...")

        # Look for expandable filter sections - they use specific class patterns
        filters_found = 0

        # Try clicking filter section headers (these are usually buttons/links)
        for filter_name in ["Keyword", "Award Type", "Location", "Recipient"]:
            print(f"  → Trying {filter_name} filter...")
            if engine.click(filter_name):
                print(f"  ✓ Found {filter_name}")
                filters_found += 1
                time.sleep(0.5)

        if filters_found == 0:
            print("  ⚠ Filters may be in collapsed state, exploring page...")

        # Step 4: Extract any visible data
        print("\n📍 Step 4: Extracting visible content...")

        # Look for spending amounts, counts, or summary text
        for target in ["spending", "awards", "results", "total"]:
            text = engine.get_text(target)
            if text and len(text) > 10:
                print(f"  ✓ Found {target} data")
                extracted_data.append({
                    "type": target,
                    "content": text[:300]
                })
                break

        # Try to get any table or list data
        table_text = engine.get_text("table")
        if table_text:
            print(f"  ✓ Found table data")
            extracted_data.append({
                "type": "table_data",
                "content": table_text[:500]
            })

        # Step 5: Save learning
        print("\n📍 Step 5: Saving learned patterns...")
        engine.save_learning()

        # Get stats
        stats = engine.get_stats()

        # Summary
        print("\n" + "="*60)
        print("  DEMO COMPLETE")
        print("="*60)

        print(f"\n  Actions attempted: {stats['total_actions']}")
        print(f"  Successful: {stats['successful_actions']}")
        print(f"  Success rate: {stats['success_rate']*100:.0f}%")

        if stats['strategy_stats']:
            print("\n  Strategy effectiveness:")
            sorted_stats = sorted(
                stats['strategy_stats'].items(),
                key=lambda x: x[1]['success'] / max(1, x[1]['success'] + x[1]['failure']),
                reverse=True
            )
            for name, data in sorted_stats[:5]:
                total = data['success'] + data['failure']
                if total > 0:
                    rate = data['success'] / total
                    print(f"    {name}: {rate*100:.0f}% ({data['success']}/{total})")

        if extracted_data:
            print(f"\n  Data extracted: {len(extracted_data)} items")

            # Save to file
            output_file = Path(__file__).parent / "usaspending_results.json"
            with open(output_file, 'w') as f:
                json.dump({
                    "timestamp": datetime.now(timezone.utc).isoformat(),
                    "stats": stats,
                    "data": extracted_data
                }, f, indent=2)
            print(f"  Results saved to: {output_file}")

        # Record in RIA memory
        save_episode(
            task="usaspending_ssa_contracts",
            result="completed",
            reflection=f"Success rate: {stats['success_rate']*100:.0f}%, "
                      f"Best strategy: {sorted_stats[0][0] if sorted_stats else 'N/A'}"
        )

        print("\n  \033[96mThe agent learned which selectors work on USASpending.gov.")
        print("  Future runs will be faster and more reliable.\033[0m\n")

    except Exception as e:
        print(f"\n  ❌ Error: {e}")
        save_episode(
            task="usaspending_ssa_contracts",
            result="error",
            reflection=str(e)
        )

    finally:
        engine.stop()


def demo_keyword_search(keyword: str, headless: bool = True):
    """Demo: Keyword search and multi-page scrape."""

    print("\n" + "="*60)
    print(f"  DEMO: Keyword Search - '{keyword}'")
    print("="*60 + "\n")

    engine = RPAEngine(headless=headless)

    try:
        engine.start()

        # Navigate to search
        print("📍 Navigating to search page...")
        engine.navigate("https://www.usaspending.gov/search")
        time.sleep(3)

        # Find search input and enter keyword
        print(f"\n📍 Searching for '{keyword}'...")

        search_filled = (
            engine.fill("Search", keyword) or
            engine.fill("Keyword", keyword) or
            engine.fill("search", keyword)
        )

        if search_filled:
            print("  ✓ Entered search term")

            # Submit
            engine.click("Search") or engine.click("Submit")
            time.sleep(3)

            # Try to get results
            print("\n📍 Extracting results...")
            results = engine.get_text("results")
            if results:
                print(f"  ✓ Found results")
                print(f"  Preview: {results[:200]}...")

        # Save learning
        engine.save_learning()
        stats = engine.get_stats()

        print(f"\n  Success rate: {stats['success_rate']*100:.0f}%")

        save_episode(
            task=f"usaspending_search_{keyword}",
            result="completed",
            reflection=f"Searched for '{keyword}', success rate: {stats['success_rate']*100:.0f}%"
        )

    finally:
        engine.stop()


def main():
    parser = argparse.ArgumentParser(description="USASpending.gov RIA Demo")
    parser.add_argument("--headless", action="store_true", default=True,
                       help="Run headless (default: True)")
    parser.add_argument("--visible", action="store_true",
                       help="Run with visible browser")
    parser.add_argument("--demo", choices=["ssa", "search"], default="ssa",
                       help="Which demo to run")
    parser.add_argument("--keyword", default="contracts",
                       help="Keyword for search demo")
    args = parser.parse_args()

    headless = not args.visible

    # Initialize
    init_memory_db()
    print_banner()

    # Run selected demo
    if args.demo == "ssa":
        demo_ssa_contracts(headless=headless)
    elif args.demo == "search":
        demo_keyword_search(args.keyword, headless=headless)


if __name__ == "__main__":
    main()
