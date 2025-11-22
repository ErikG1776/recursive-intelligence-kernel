#!/usr/bin/env python3
"""
Live AGI UI Navigator — Playwright Edition (Browser-Stays-Open Version)
"""

import argparse
import asyncio
from dataclasses import dataclass
from difflib import SequenceMatcher
from typing import List

from playwright.async_api import async_playwright
from bs4 import BeautifulSoup


GOAL_SYNONYMS = [
    "log in", "login", "sign in",
    "start", "continue", "access", "submit",
    "click", "go"
]


@dataclass
class UIElement:
    role: str
    text: str
    selector: str
    score: float = 0.0


def semantic_score(label: str, synonyms: List[str]) -> float:
    label = label.lower().strip()
    if not label:
        return 0.0

    scores = []
    for term in synonyms:
        scores.append(SequenceMatcher(None, label, term).ratio())
        if term in label:
            scores.append(1.0)

    return max(scores)


def extract_ui(html: str) -> List[UIElement]:
    soup = BeautifulSoup(html, "html.parser")
    items = []

    # Buttons
    for btn in soup.find_all("button"):
        label = btn.get_text(strip=True)
        ident = btn.get("id")
        selector = f"#{ident}" if ident else "button"
        items.append(UIElement("button", label, selector))

    # Input submit
    for inp in soup.find_all("input"):
        t = (inp.get("type") or "").lower()
        if t in ["button", "submit"]:
            label = inp.get("value") or "submit"
            ident = inp.get("id")
            selector = f"input#{ident}" if ident else "input[type=submit]"
            items.append(UIElement("input", label, selector))

    return items


async def run(url: str, goal: str):
    print(f"\n🌐 Navigating to {url} ...")

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        page = await browser.new_page()

        # auto accept alerts
        page.on("dialog", lambda dialog: asyncio.create_task(dialog.accept()))

        await page.goto(url)
        print("🔍 Page loaded.")

        html = await page.content()
        elements = extract_ui(html)

        print(f"🧠 Found {len(elements)} actionable items.\n")

        for el in elements:
            el.score = semantic_score(el.text, GOAL_SYNONYMS)

        elements.sort(key=lambda x: x.score, reverse=True)

        if not elements or elements[0].score < 0.2:
            print("❌ No useful match found.")
            return

        best = elements[0]
        print(f"🎯 Best candidate: '{best.text}' (score={best.score:.3f})")
        print("👉 Attempting click...")

        try:
            locator = page.get_by_text(best.text, exact=True)
            if await locator.count() > 0:
                await locator.first.click()
            else:
                await page.locator(best.selector).first.click()
        except Exception:
            await page.locator(best.selector).first.click()

        print("✅ Click executed.\n")

        await asyncio.sleep(0.8)

        print("🔁 Re-scanning for new UI state...\n")

        # 🌟 KEEP THE BROWSER OPEN UNTIL USER CLOSES IT
        print("🧠 Browser will stay open until you close it manually.\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("url", help="URL or file:/// path to load")
    parser.add_argument("--goal", default="click", help="Goal behavior")
    args = parser.parse_args()

    asyncio.run(run(args.url, args.goal))


if __name__ == "__main__":
    main()