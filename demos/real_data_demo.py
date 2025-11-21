#!/usr/bin/env python3
"""
Real Government Data Demo | Recursive Intelligence Kernel (RIK)
--------------------------------------------------------------------
Demonstrates RIK's intelligence on REAL government payment data.

This is the ultimate proof: RIK learning from and analyzing actual
NYC and federal government payments - not synthetic examples.

Usage:
    python3 demos/real_data_demo.py
"""

import sys
import os
import json
import math
import random
from datetime import datetime
from typing import Dict, List, Any
from collections import defaultdict

# Import the data loader
from real_data_loader import GovernmentDataLoader

# ==========================================================
# 🧠  REAL DATA INTELLIGENCE ENGINE
# ==========================================================

class RealDataIntelligenceEngine:
    """
    RIK Intelligence Engine running on real government data.

    Capabilities:
    - Learn patterns from actual government payments
    - Detect anomalies in real vendor data
    - Identify at-risk vendors
    - Predict exceptions based on real patterns
    """

    def __init__(self, invoices: List[Dict[str, Any]]):
        self.invoices = invoices
        self.vendor_profiles = {}
        self.agency_patterns = {}
        self.exception_predictions = {}

        # Build intelligence from real data
        self._build_vendor_profiles()
        self._build_agency_patterns()
        self._detect_anomalies()

    def _build_vendor_profiles(self):
        """Build vendor profiles from real payment data."""
        vendor_data = defaultdict(list)

        for inv in self.invoices:
            vendor = inv["vendor"]
            vendor_data[vendor].append(inv)

        for vendor, payments in vendor_data.items():
            amounts = [p["amount"] for p in payments]
            mean = sum(amounts) / len(amounts)
            variance = sum((x - mean) ** 2 for x in amounts) / len(amounts) if len(amounts) > 1 else 0
            std = math.sqrt(variance)

            # Calculate trust score based on patterns
            has_po_rate = sum(1 for p in payments if p.get("has_po")) / len(payments)
            avg_ocr = sum(p.get("ocr_confidence", 0.85) for p in payments) / len(payments)

            # Determine lifecycle
            if len(payments) <= 2:
                lifecycle = "new"
                trust = 0.5
            elif has_po_rate > 0.8 and avg_ocr > 0.85:
                lifecycle = "trusted"
                trust = 0.9
            elif has_po_rate > 0.5:
                lifecycle = "established"
                trust = 0.75
            else:
                lifecycle = "at_risk"
                trust = 0.4

            self.vendor_profiles[vendor] = {
                "payment_count": len(payments),
                "total_amount": sum(amounts),
                "avg_amount": mean,
                "std_amount": std,
                "min_amount": min(amounts),
                "max_amount": max(amounts),
                "has_po_rate": has_po_rate,
                "avg_ocr_confidence": avg_ocr,
                "lifecycle": lifecycle,
                "trust_score": trust,
                "agencies": list(set(p.get("agency", "") for p in payments)),
                "sources": list(set(p.get("source", "") for p in payments)),
            }

    def _build_agency_patterns(self):
        """Build agency spending patterns."""
        agency_data = defaultdict(list)

        for inv in self.invoices:
            agency = inv.get("agency", "Unknown")
            agency_data[agency].append(inv)

        for agency, payments in agency_data.items():
            amounts = [p["amount"] for p in payments]
            vendors = list(set(p["vendor"] for p in payments))

            self.agency_patterns[agency] = {
                "payment_count": len(payments),
                "total_spend": sum(amounts),
                "avg_payment": sum(amounts) / len(amounts),
                "vendor_count": len(vendors),
                "top_vendors": self._get_top_vendors(payments, 3),
            }

    def _get_top_vendors(self, payments: List[Dict], n: int) -> List[Dict]:
        """Get top N vendors by total amount."""
        vendor_totals = defaultdict(float)
        for p in payments:
            vendor_totals[p["vendor"]] += p["amount"]

        sorted_vendors = sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)
        return [{"vendor": v, "total": t} for v, t in sorted_vendors[:n]]

    def _detect_anomalies(self):
        """Detect anomalies in the real data."""
        self.anomalies = []

        for inv in self.invoices:
            vendor = inv["vendor"]
            if vendor not in self.vendor_profiles:
                continue

            profile = self.vendor_profiles[vendor]
            amount = inv["amount"]

            # Z-score anomaly detection
            if profile["std_amount"] > 0:
                z_score = abs(amount - profile["avg_amount"]) / profile["std_amount"]
                if z_score > 2:
                    self.anomalies.append({
                        "invoice_id": inv["id"],
                        "vendor": vendor,
                        "amount": amount,
                        "expected": profile["avg_amount"],
                        "z_score": z_score,
                        "severity": "HIGH" if z_score > 3 else "MEDIUM"
                    })

            # Missing PO anomaly
            if not inv.get("has_po") and profile["has_po_rate"] > 0.8:
                self.anomalies.append({
                    "invoice_id": inv["id"],
                    "vendor": vendor,
                    "amount": amount,
                    "type": "missing_po",
                    "reason": f"Vendor usually has PO ({profile['has_po_rate']:.0%})"
                })

    def analyze_invoice(self, invoice: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single invoice using learned patterns."""
        vendor = invoice["vendor"]
        amount = invoice["amount"]

        # Get vendor profile
        if vendor in self.vendor_profiles:
            profile = self.vendor_profiles[vendor]
            is_known_vendor = True
        else:
            profile = None
            is_known_vendor = False

        # Risk assessment
        risk_factors = []
        risk_score = 0.2  # Base risk

        # Check for anomalous amount
        if profile and profile["std_amount"] > 0:
            z_score = abs(amount - profile["avg_amount"]) / profile["std_amount"]
            if z_score > 2:
                risk_factors.append(f"Amount ${amount:,.0f} is {z_score:.1f}σ from average ${profile['avg_amount']:,.0f}")
                risk_score += min(0.4, z_score * 0.1)

        # Check for missing PO
        if not invoice.get("has_po"):
            if profile and profile["has_po_rate"] > 0.5:
                risk_factors.append(f"Missing PO - vendor usually has PO ({profile['has_po_rate']:.0%})")
                risk_score += 0.2
            else:
                risk_factors.append("Missing PO")
                risk_score += 0.1

        # Check OCR confidence
        ocr = invoice.get("ocr_confidence", 0.85)
        if ocr < 0.75:
            risk_factors.append(f"Low OCR confidence ({ocr:.0%})")
            risk_score += 0.15

        # Unknown vendor risk
        if not is_known_vendor:
            risk_factors.append("Unknown vendor - no historical data")
            risk_score += 0.25

        # Trust adjustment
        if profile:
            if profile["lifecycle"] == "trusted":
                risk_score = max(0, risk_score - 0.15)
            elif profile["lifecycle"] == "at_risk":
                risk_score = min(1, risk_score + 0.15)

        # Final risk level
        risk_score = min(1.0, risk_score)
        if risk_score > 0.6:
            risk_level = "HIGH"
            action = "ESCALATE"
        elif risk_score > 0.3:
            risk_level = "MEDIUM"
            action = "REVIEW"
        else:
            risk_level = "LOW"
            action = "APPROVE"

        return {
            "invoice_id": invoice["id"],
            "vendor": vendor,
            "amount": amount,
            "risk_level": risk_level,
            "risk_score": risk_score,
            "action": action,
            "risk_factors": risk_factors,
            "vendor_profile": {
                "known": is_known_vendor,
                "lifecycle": profile["lifecycle"] if profile else "unknown",
                "trust": profile["trust_score"] if profile else 0.5,
                "payment_count": profile["payment_count"] if profile else 0,
            } if profile else None
        }


# ==========================================================
# 📊  DEMO RUNNER
# ==========================================================

def run_demo():
    """Run the real government data demo."""
    print("=" * 70)
    print("🏛️   RIK REAL GOVERNMENT DATA ANALYSIS")
    print("    Intelligence on Actual Government Payments")
    print("=" * 70)
    print()

    # Load real data
    loader = GovernmentDataLoader()
    invoices = loader.load_all_sources(nyc_limit=30, fed_limit=20)

    if not invoices:
        print("❌  No data loaded. Check internet connection.")
        return

    print()
    print("=" * 70)
    print("🧠  BUILDING INTELLIGENCE FROM REAL DATA")
    print("=" * 70)
    print()

    # Split data: 70% for learning, 30% for analysis
    random.shuffle(invoices)
    split_point = int(len(invoices) * 0.7)
    training_data = invoices[:split_point]
    test_data = invoices[split_point:]

    print(f"Training data: {len(training_data)} invoices")
    print(f"Test data: {len(test_data)} invoices")
    print()

    # Build intelligence
    engine = RealDataIntelligenceEngine(training_data)

    # Show vendor profiles
    print("=" * 70)
    print("🏢  VENDOR PROFILES LEARNED")
    print("=" * 70)
    print()

    sorted_vendors = sorted(
        engine.vendor_profiles.items(),
        key=lambda x: x[1]["total_amount"],
        reverse=True
    )[:10]

    for vendor, profile in sorted_vendors:
        lifecycle_emoji = {
            "new": "🆕",
            "establishing": "📈",
            "established": "✅",
            "trusted": "⭐",
            "at_risk": "⚠️"
        }
        emoji = lifecycle_emoji.get(profile["lifecycle"], "❓")

        print(f"{emoji} {vendor[:40]}")
        print(f"   Payments: {profile['payment_count']} | Total: ${profile['total_amount']:,.0f}")
        print(f"   Avg: ${profile['avg_amount']:,.0f} | Trust: {profile['trust_score']:.0%}")
        print(f"   Lifecycle: {profile['lifecycle']}")
        print()

    # Show agency patterns
    print("=" * 70)
    print("🏛️   AGENCY SPENDING PATTERNS")
    print("=" * 70)
    print()

    sorted_agencies = sorted(
        engine.agency_patterns.items(),
        key=lambda x: x[1]["total_spend"],
        reverse=True
    )[:5]

    for agency, pattern in sorted_agencies:
        print(f"{agency[:45]}")
        print(f"   Payments: {pattern['payment_count']} | Total: ${pattern['total_spend']:,.0f}")
        print(f"   Avg Payment: ${pattern['avg_payment']:,.0f}")
        print(f"   Vendors: {pattern['vendor_count']}")
        print()

    # Analyze test invoices
    print("=" * 70)
    print("🔍  ANALYZING TEST INVOICES")
    print("=" * 70)
    print()

    results = []
    for inv in test_data:
        result = engine.analyze_invoice(inv)
        results.append(result)

        risk_emoji = {"LOW": "🟢", "MEDIUM": "🟡", "HIGH": "🔴"}
        action_emoji = {"APPROVE": "✅", "REVIEW": "⚠️", "ESCALATE": "🚨"}

        print("─" * 70)
        print(f"Invoice: {inv['id']}")
        print(f"Vendor: {inv['vendor'][:40]}")
        print(f"Amount: ${inv['amount']:,.2f}")
        print(f"Source: {inv.get('source', 'Unknown')}")
        print()

        print(f"Risk: {risk_emoji[result['risk_level']]} {result['risk_level']} ({result['risk_score']:.0%})")
        print(f"Action: {action_emoji[result['action']]} {result['action']}")

        if result['risk_factors']:
            print(f"Factors:")
            for factor in result['risk_factors']:
                print(f"  • {factor}")

        if result['vendor_profile']:
            vp = result['vendor_profile']
            print(f"Vendor: {vp['lifecycle']} ({vp['payment_count']} payments, {vp['trust']:.0%} trust)")
        print()

    # Summary
    print("=" * 70)
    print("📊  ANALYSIS SUMMARY")
    print("=" * 70)
    print()

    high_risk = sum(1 for r in results if r["risk_level"] == "HIGH")
    medium_risk = sum(1 for r in results if r["risk_level"] == "MEDIUM")
    low_risk = sum(1 for r in results if r["risk_level"] == "LOW")

    print(f"Invoices analyzed: {len(results)}")
    print()
    print("Risk Distribution:")
    print(f"  🔴 HIGH:   {high_risk} ({100*high_risk/len(results):.0f}%)")
    print(f"  🟡 MEDIUM: {medium_risk} ({100*medium_risk/len(results):.0f}%)")
    print(f"  🟢 LOW:    {low_risk} ({100*low_risk/len(results):.0f}%)")
    print()

    # Detected anomalies
    if engine.anomalies:
        print(f"Anomalies detected in training data: {len(engine.anomalies)}")
        print()

    print("=" * 70)
    print("🎯  THIS IS REAL DATA")
    print("=" * 70)
    print()
    print("Everything you just saw came from:")
    print("  • NYC Checkbook - actual city payments")
    print("  • USASpending.gov - actual federal contracts")
    print()
    print("RIK learned patterns from REAL government payments")
    print("and applied that intelligence to analyze new invoices.")
    print()
    print("This is not synthetic data. This is not simulation.")
    print("This is RIK working on real-world government data.")
    print()
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
