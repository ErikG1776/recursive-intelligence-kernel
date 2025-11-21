"""
Live AGI UI Navigator Demo
--------------------------
This script demonstrates semantic UI navigation and recovery using the
Recursive Intelligence Kernel style. It performs DOM perception,
semantic intent matching, and self-healing plan reconstruction when key
selectors disappear.
"""

import argparse
import json
import os
import re
import textwrap
from dataclasses import dataclass, field
from difflib import SequenceMatcher
from typing import Dict, Iterable, List, Optional, Tuple

import requests
from bs4 import BeautifulSoup

SAMPLE_PAGE_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "sample_login_page.html")
DEFAULT_GOAL = "log in"

GOAL_SYNONYMS = [
    "log in",
    "login",
    "sign in",
    "sign-in",
    "my account",
    "access account",
    "continue",
    "start",
    "get started",
]


@dataclass
class SemanticElement:
    """Representation of an interactive UI element."""

    tag: str
    text: str
    attrs: Dict[str, str]
    category: str
    score: float = 0.0

    @property
    def label(self) -> str:
        label = self.text.strip()
        if label:
            return label
        for key in ("aria-label", "alt", "value", "placeholder", "id", "name"):
            value = self.attrs.get(key)
            if value:
                return str(value).strip()
        return self.tag

    def describe(self) -> str:
        highlight = self.label or self.tag
        ident = self.attrs.get("id") or self.attrs.get("name") or "-"
        return f"{self.category.title()}<{self.tag}> '{highlight}' (id={ident})"


@dataclass
class ReasoningTrace:
    """Keeps a structured reasoning trace."""

    steps: List[Dict[str, str]] = field(default_factory=list)

    def log(self, action: str, outcome: str, data: Optional[dict] = None) -> None:
        entry = {"action": action, "outcome": outcome}
        if data:
            entry["data"] = data
        self.steps.append(entry)

    def as_text(self) -> str:
        lines = []
        for idx, step in enumerate(self.steps, 1):
            lines.append(f"Step {idx}: {step['action']} → {step['outcome']}")
            if "data" in step:
                pretty = json.dumps(step["data"], indent=2)
                lines.append(textwrap.indent(pretty, prefix="    " ))
        return "\n".join(lines)


class SemanticDOMInterpreter:
    """Extracts interactive structures from HTML."""

    def __init__(self, html: str):
        self.soup = BeautifulSoup(html, "html.parser")

    def _normalize_attrs(self, tag) -> Dict[str, str]:
        attrs: Dict[str, str] = {}
        for key, value in tag.attrs.items():
            if isinstance(value, list):
                attrs[key] = " ".join(map(str, value))
            else:
                attrs[key] = str(value)
        return attrs

    def extract_interactive_elements(self) -> List[SemanticElement]:
        elements: List[SemanticElement] = []

        for button in self.soup.find_all(["button", "a", "div", "span"]):
            role = button.get("role", "")
            if button.name in {"div", "span"} and role not in {"button", "link"}:
                continue
            text = button.get_text(" ", strip=True)
            elements.append(
                SemanticElement(
                    tag=button.name,
                    text=text,
                    attrs=self._normalize_attrs(button),
                    category="button",
                )
            )

        for input_tag in self.soup.find_all("input"):
            input_type = input_tag.get("type", "text").lower()
            attrs = self._normalize_attrs(input_tag)
            if input_type in {"submit", "button"}:
                text = input_tag.get("value", "").strip()
                elements.append(
                    SemanticElement(
                        tag=input_tag.name,
                        text=text,
                        attrs=attrs,
                        category="button",
                    )
                )
            else:
                text = input_tag.get("placeholder", input_tag.get("name", "")).strip()
                elements.append(
                    SemanticElement(
                        tag=input_tag.name,
                        text=text,
                        attrs=attrs,
                        category="field",
                    )
                )

        for heading in self.soup.find_all(["h1", "h2", "h3"]):
            elements.append(
                SemanticElement(
                    tag=heading.name,
                    text=heading.get_text(" ", strip=True),
                    attrs=self._normalize_attrs(heading),
                    category="heading",
                )
            )

        return elements

    def extract_form_fields(self) -> List[Tuple[str, str]]:
        fields: List[Tuple[str, str]] = []
        for form in self.soup.find_all("form"):
            for input_tag in form.find_all("input"):
                name = input_tag.get("name") or input_tag.get("id") or "field"
                input_type = input_tag.get("type", "text")
                fields.append((name, input_type))
        return fields

    def mutate_for_breakage(self, primary: SemanticElement, elements: List[SemanticElement]) -> List[SemanticElement]:
        mutated: List[SemanticElement] = []
        removed = False
        for element in elements:
            if not removed and element.label.lower() == primary.label.lower():
                removed = True
                continue
            mutated.append(element)

        # Introduce a renamed variant to mimic UI redesigns
        if mutated:
            first = mutated[0]
            renamed = SemanticElement(
                tag=first.tag,
                text="Access Portal",
                attrs=dict(first.attrs, **{"data-semantic-alias": "sign-in"}),
                category=first.category,
                score=first.score,
            )
            mutated[0] = renamed
        return mutated


class SemanticNavigator:
    """Coordinates perception, planning, and recovery."""

    def __init__(self, goal: str, synonyms: Iterable[str]):
        self.goal = goal
        self.synonyms = [term.lower() for term in synonyms]
        self.trace = ReasoningTrace()

    def score_element(self, element: SemanticElement) -> float:
        label = element.label.lower()
        if not label:
            return 0.0
        similarities: List[float] = []
        for term in self.synonyms:
            if term in label:
                similarities.append(1.0)
            else:
                similarities.append(SequenceMatcher(None, term, label).ratio())
        base = max(similarities) if similarities else 0.0

        type_bonus = 0.12 if element.category == "button" else 0.05
        prominence_bonus = 0.08 if re.search(r"primary|cta|submit", " ".join(element.attrs.values()), re.I) else 0.0
        return min(base + type_bonus + prominence_bonus, 1.0)

    def rank_candidates(self, elements: List[SemanticElement]) -> List[SemanticElement]:
        for element in elements:
            element.score = round(self.score_element(element), 3)
        ranked = sorted(elements, key=lambda el: el.score, reverse=True)
        return [el for el in ranked if el.score > 0.2]

    def build_action_chain(self, ranked: List[SemanticElement], form_fields: List[Tuple[str, str]]) -> List[str]:
        actions: List[str] = []
        primary = ranked[0] if ranked else None
        if primary:
            actions.append(
                f"Locate semantic trigger → {primary.describe()} (confidence {primary.score:.2f})"
            )
            actions.append("Click trigger and wait for authentication surface")
        else:
            actions.append("Scan navigation for authentication trigger (no confident match yet)")

        if form_fields:
            actions.append("Identify credential form fields")
            for name, input_type in form_fields:
                actions.append(f"  - Map `{name}` ({input_type}) to stored credential")
            actions.append("Submit form and watch for dashboard signals")
        else:
            actions.append("Look for follow-up CTAs or redirects after click")
        actions.append("Validate success by confirming dashboard headings or account controls")
        return actions

    def run(self, html: str, allow_breakage: bool = True) -> ReasoningTrace:
        interpreter = SemanticDOMInterpreter(html)

        elements = interpreter.extract_interactive_elements()
        self.trace.log("Semantic perception", f"Detected {len(elements)} actionable elements")

        ranked = self.rank_candidates(elements)
        self.trace.log(
            "Intent matching",
            f"Top candidate: {ranked[0].describe()}" if ranked else "No confident match yet",
            data={"candidates": [f"{el.describe()} (score={el.score})" for el in ranked[:5]]},
        )

        actions = self.build_action_chain(ranked, interpreter.extract_form_fields())
        self.trace.log("Action plan", "Generated baseline navigation chain", data={"steps": actions})

        if allow_breakage and ranked:
            mutated = interpreter.mutate_for_breakage(primary=ranked[0], elements=elements)
            self.trace.log(
                "Injected breakage",
                "Removed primary trigger and renamed another element",
                data={"removed": ranked[0].describe()},
            )

            recovery_ranked = self.rank_candidates(mutated)
            recovery_actions = self.build_action_chain(recovery_ranked, interpreter.extract_form_fields())
            self.trace.log(
                "Self-healing scan",
                f"Recovered with {recovery_ranked[0].describe()}" if recovery_ranked else "Still searching",
                data={"candidates": [f"{el.describe()} (score={el.score})" for el in recovery_ranked[:5]]},
            )
            self.trace.log(
                "Revised plan",
                "Rebuilt navigation after breakage",
                data={"steps": recovery_actions},
            )
        return self.trace


def load_dom_source(url: Optional[str], sample_fallback: bool = True) -> Tuple[str, str]:
    if not url or url == "sample":
        with open(SAMPLE_PAGE_PATH, "r", encoding="utf-8") as f:
            return f.read(), "sample_login_page.html"

    if os.path.isfile(url):
        with open(url, "r", encoding="utf-8") as f:
            return f.read(), os.path.abspath(url)

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text, url
    except Exception as exc:  # noqa: BLE001
        if sample_fallback:
            with open(SAMPLE_PAGE_PATH, "r", encoding="utf-8") as f:
                fallback = f.read()
            return fallback, f"{url} (fallback to sample: {exc})"
        raise


def main():
    parser = argparse.ArgumentParser(description="Demonstrate semantic UI navigation + recovery.")
    parser.add_argument("url", nargs="?", help="Target URL or omit to use the bundled sample surface.")
    parser.add_argument("--goal", default=DEFAULT_GOAL, help="Navigation goal to pursue (default: log in).")
    parser.add_argument("--no-break", action="store_true", help="Disable breakage injection step.")
    parser.add_argument(
        "--no-fallback",
        action="store_true",
        help="Error instead of falling back to the sample page when fetching fails.",
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output reasoning trace as plain text or JSON.",
    )
    parser.add_argument(
        "--save",
        metavar="PATH",
        help="Optional path to save the reasoning trace (respects --format).",
    )
    args = parser.parse_args()

    html, source = load_dom_source(args.url, sample_fallback=not args.no_fallback)
    navigator = SemanticNavigator(goal=args.goal, synonyms=GOAL_SYNONYMS)

    print("\n🧠 RIK Live AGI UI Navigator Demo")
    print(f"Goal: {args.goal} | Source: {source}")
    if args.no_break:
        print("Breakage injection: disabled")
    else:
        print("Breakage injection: enabled (remove primary trigger + rename peer)")

    trace = navigator.run(html, allow_breakage=not args.no_break)

    serialized = trace.as_text() if args.format == "text" else json.dumps(trace.steps, indent=2)

    print("\n--- Reasoning Trace ---")
    print(serialized)

    if args.save:
        with open(args.save, "w", encoding="utf-8") as f:
            f.write(serialized)
        print(f"\n💾 Saved trace to {args.save}")

    print("\n✅ Demo complete.")


if __name__ == "__main__":
    main()
