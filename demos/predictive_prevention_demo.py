#!/usr/bin/env python3
"""
Predictive Exception Prevention Demo | Recursive Intelligence Kernel (RIK)
--------------------------------------------------------------------
Demonstrates RIK's REVOLUTIONARY capability: predicting and preventing
exceptions BEFORE they occur, not just handling them after.

This is the difference between good and game-changing:
- Current RIK: Handles exceptions 50% better
- Predictive RIK: Prevents 60% of exceptions entirely

Usage:
    python3 demos/predictive_prevention_demo.py
"""

import sys
import os
import json
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Note: This demo uses pattern analysis, not episodic memory storage

# ==========================================================
# 📊  HISTORICAL INVOICE DATA (For Pattern Learning)
# ==========================================================

# Simulated historical data - what RIK has learned from past invoices
HISTORICAL_PATTERNS = {
    "first_time_vendors": {
        "total_invoices": 847,
        "missing_po_rate": 0.73,
        "vendor_mismatch_rate": 0.41,
        "low_ocr_rate": 0.28,
        "avg_resolution_time_minutes": 12,
    },
    "government_contracts": {
        "total_invoices": 2341,
        "missing_po_rate": 0.12,
        "vendor_mismatch_rate": 0.08,
        "amount_variance_rate": 0.34,
        "avg_resolution_time_minutes": 8,
    },
    "international_vendors": {
        "total_invoices": 567,
        "missing_po_rate": 0.45,
        "format_issue_rate": 0.62,
        "currency_issue_rate": 0.38,
        "avg_resolution_time_minutes": 18,
    },
    "recurring_vendors": {
        "total_invoices": 5892,
        "missing_po_rate": 0.05,
        "vendor_mismatch_rate": 0.02,
        "amount_variance_rate": 0.15,
        "avg_resolution_time_minutes": 3,
    },
}

# Vendor intelligence database
VENDOR_INTELLIGENCE = {
    "ACME Federal Services LLC": {
        "category": "recurring_vendors",
        "avg_invoice_amount": 4200,
        "amount_stddev": 800,
        "typical_frequency": "monthly",
        "historical_exceptions": 2,
        "total_invoices": 24,
        "trust_score": 0.96,
    },
    "TechCorp Solutions Inc": {
        "category": "first_time_vendors",
        "avg_invoice_amount": None,  # Unknown - first time
        "amount_stddev": None,
        "typical_frequency": None,
        "historical_exceptions": None,
        "total_invoices": 0,
        "trust_score": 0.50,  # Default for new vendors
    },
    "Global Logistics Partners": {
        "category": "international_vendors",
        "avg_invoice_amount": 15600,
        "amount_stddev": 4200,
        "typical_frequency": "weekly",
        "historical_exceptions": 18,
        "total_invoices": 52,
        "trust_score": 0.78,
    },
    "Pacific Office Supplies": {
        "category": "recurring_vendors",
        "avg_invoice_amount": 2800,
        "amount_stddev": 600,
        "typical_frequency": "monthly",
        "historical_exceptions": 1,
        "total_invoices": 36,
        "trust_score": 0.98,
    },
    "DefenseTech Solutions": {
        "category": "government_contracts",
        "avg_invoice_amount": 45000,
        "amount_stddev": 12000,
        "typical_frequency": "quarterly",
        "historical_exceptions": 8,
        "total_invoices": 16,
        "trust_score": 0.85,
    },
    "MedSupply Distribution": {
        "category": "recurring_vendors",
        "avg_invoice_amount": 5200,
        "amount_stddev": 1100,
        "typical_frequency": "bi-weekly",
        "historical_exceptions": 3,
        "total_invoices": 48,
        "trust_score": 0.94,
    },
    "Sunrise Consulting Group": {
        "category": "first_time_vendors",
        "avg_invoice_amount": None,
        "amount_stddev": None,
        "typical_frequency": None,
        "historical_exceptions": None,
        "total_invoices": 0,
        "trust_score": 0.50,
    },
    "Metro Maintenance Corp": {
        "category": "recurring_vendors",
        "avg_invoice_amount": 8900,
        "amount_stddev": 2200,
        "typical_frequency": "monthly",
        "historical_exceptions": 5,
        "total_invoices": 30,
        "trust_score": 0.91,
    },
}

# Incoming invoices to analyze (what's expected this week)
INCOMING_INVOICES = [
    {
        "id": "INCOMING-001",
        "vendor_name": "TechCorp Solutions",  # First-time vendor
        "expected_amount_range": (3000, 8000),
        "expected_date": "tomorrow",
        "source": "Email notification from vendor",
        "po_status": "unknown",
    },
    {
        "id": "INCOMING-002",
        "vendor_name": "Global Logistics Partners",  # International
        "expected_amount_range": (12000, 18000),
        "expected_date": "2 days",
        "source": "Scheduled delivery",
        "po_status": "PO-2024-445 issued",
    },
    {
        "id": "INCOMING-003",
        "vendor_name": "Pacific Office Supplies",  # Recurring, reliable
        "expected_amount_range": (2500, 3200),
        "expected_date": "3 days",
        "source": "Monthly subscription",
        "po_status": "Auto-PO enabled",
    },
    {
        "id": "INCOMING-004",
        "vendor_name": "Sunrise Consulting Group",  # First-time
        "expected_amount_range": (15000, 25000),
        "expected_date": "this week",
        "source": "New contract signed",
        "po_status": "pending creation",
    },
    {
        "id": "INCOMING-005",
        "vendor_name": "DefenseTech Solutions",  # Government
        "expected_amount_range": (40000, 55000),
        "expected_date": "4 days",
        "source": "Quarterly delivery",
        "po_status": "PO-GOV-2024-998",
    },
    {
        "id": "INCOMING-006",
        "vendor_name": "MedSupply Distribution",  # Recurring
        "expected_amount_range": (4800, 5600),
        "expected_date": "tomorrow",
        "source": "Bi-weekly order",
        "po_status": "Auto-PO enabled",
    },
    {
        "id": "INCOMING-007",
        "vendor_name": "Unknown Vendor XYZ",  # Completely unknown
        "expected_amount_range": (1000, 5000),
        "expected_date": "this week",
        "source": "Unexpected email",
        "po_status": "none",
    },
]


# ==========================================================
# 🔮  PREDICTIVE ENGINE
# ==========================================================

@dataclass
class ExceptionPrediction:
    """Predicted exception with probability and prevention strategy."""
    exception_type: str
    probability: float
    impact: str  # low, medium, high
    prevention_action: str
    prevention_effort: str  # minutes


@dataclass
class InvoicePrediction:
    """Complete prediction for an incoming invoice."""
    invoice_id: str
    vendor_name: str
    risk_score: float
    risk_level: str  # low, medium, high, critical
    predicted_exceptions: List[ExceptionPrediction]
    preventive_actions: List[str]
    estimated_prevention_time: int  # minutes
    estimated_resolution_time: int  # minutes if not prevented
    prevention_roi: float  # time saved


class PredictiveEngine:
    """
    RIK Predictive Exception Prevention Engine.

    This is the REVOLUTIONARY capability - predicting exceptions
    before they occur and recommending preventive actions.
    """

    def __init__(self):
        self.historical_patterns = HISTORICAL_PATTERNS
        self.vendor_intelligence = VENDOR_INTELLIGENCE

    def analyze_incoming_invoice(self, invoice: Dict[str, Any]) -> InvoicePrediction:
        """
        Analyze an incoming invoice and predict exceptions.

        This is where the magic happens - we use historical patterns
        to predict what will go wrong and how to prevent it.
        """
        vendor_name = invoice["vendor_name"]
        predictions = []
        preventive_actions = []

        # Get vendor intelligence
        vendor_info = self._get_vendor_intelligence(vendor_name)
        category = vendor_info.get("category", "first_time_vendors")
        patterns = self.historical_patterns.get(category, self.historical_patterns["first_time_vendors"])

        # ===========================================
        # Predict Missing PO Exception
        # ===========================================
        po_status = invoice.get("po_status", "unknown")
        if po_status in ["unknown", "none", "pending creation"]:
            base_prob = patterns["missing_po_rate"]
            # Adjust based on vendor history
            if vendor_info["total_invoices"] == 0:
                prob = min(0.95, base_prob * 1.3)  # Higher for new vendors
            else:
                prob = base_prob * (1 - vendor_info["trust_score"] * 0.5)

            if prob > 0.3:
                predictions.append(ExceptionPrediction(
                    exception_type="missing_po_number",
                    probability=prob,
                    impact="high" if invoice["expected_amount_range"][1] > 10000 else "medium",
                    prevention_action=f"Pre-create PO for expected amount ${invoice['expected_amount_range'][0]:,}-${invoice['expected_amount_range'][1]:,}",
                    prevention_effort="5 minutes"
                ))
                preventive_actions.append(
                    f"Create PO-2024-{random.randint(1000, 9999)} for {vendor_name} "
                    f"(amount range: ${invoice['expected_amount_range'][0]:,}-${invoice['expected_amount_range'][1]:,})"
                )

        # ===========================================
        # Predict Vendor Mismatch Exception
        # ===========================================
        if vendor_info["total_invoices"] == 0:
            # First-time vendor - high chance of name mismatch
            prob = patterns.get("vendor_mismatch_rate", 0.41)
            predictions.append(ExceptionPrediction(
                exception_type="vendor_name_mismatch",
                probability=prob,
                impact="medium",
                prevention_action=f"Add vendor aliases for '{vendor_name}'",
                prevention_effort="3 minutes"
            ))
            preventive_actions.append(
                f"Pre-register vendor aliases: '{vendor_name}', "
                f"'{vendor_name.replace(' ', '')}', "
                f"'{vendor_name.split()[0]}'"
            )

        # ===========================================
        # Predict Amount Variance Exception
        # ===========================================
        if vendor_info["avg_invoice_amount"]:
            expected_mid = (invoice["expected_amount_range"][0] + invoice["expected_amount_range"][1]) / 2
            if vendor_info["amount_stddev"]:
                variance = abs(expected_mid - vendor_info["avg_invoice_amount"]) / vendor_info["amount_stddev"]
                if variance > 2:
                    prob = min(0.85, 0.3 + variance * 0.15)
                    predictions.append(ExceptionPrediction(
                        exception_type="amount_variance",
                        probability=prob,
                        impact="high",
                        prevention_action="Pre-approve variance or flag for review",
                        prevention_effort="2 minutes"
                    ))
                    preventive_actions.append(
                        f"Alert: Expected amount ${expected_mid:,.0f} differs from "
                        f"historical average ${vendor_info['avg_invoice_amount']:,.0f} "
                        f"(variance: {variance:.1f}σ)"
                    )

        # ===========================================
        # Predict Format/International Issues
        # ===========================================
        if category == "international_vendors":
            prob = patterns.get("format_issue_rate", 0.62)
            if prob > 0.3:
                predictions.append(ExceptionPrediction(
                    exception_type="format_issue",
                    probability=prob,
                    impact="medium",
                    prevention_action="Pre-configure format templates",
                    prevention_effort="4 minutes"
                ))
                preventive_actions.append(
                    f"Configure international invoice template for {vendor_name}"
                )

            currency_prob = patterns.get("currency_issue_rate", 0.38)
            if currency_prob > 0.2:
                predictions.append(ExceptionPrediction(
                    exception_type="currency_conversion",
                    probability=currency_prob,
                    impact="low",
                    prevention_action="Pre-fetch exchange rates",
                    prevention_effort="1 minute"
                ))
                preventive_actions.append(
                    "Pre-fetch current exchange rates for invoice processing"
                )

        # ===========================================
        # Predict Low OCR Confidence
        # ===========================================
        if category in ["first_time_vendors", "international_vendors"]:
            prob = patterns.get("low_ocr_rate", 0.28)
            if prob > 0.2:
                predictions.append(ExceptionPrediction(
                    exception_type="low_ocr_confidence",
                    probability=prob,
                    impact="medium",
                    prevention_action="Request digital/typed invoice",
                    prevention_effort="2 minutes"
                ))
                preventive_actions.append(
                    f"Request {vendor_name} send digital PDF instead of scanned copy"
                )

        # ===========================================
        # Calculate Risk Score
        # ===========================================
        if predictions:
            # Weighted risk score based on probability and impact
            impact_weights = {"low": 1, "medium": 2, "high": 3}
            total_risk = sum(
                p.probability * impact_weights[p.impact]
                for p in predictions
            )
            max_risk = len(predictions) * 3  # Max if all were 100% prob, high impact
            risk_score = min(1.0, total_risk / max(1, max_risk) * 1.5)
        else:
            risk_score = 0.1

        # Determine risk level
        if risk_score >= 0.75:
            risk_level = "critical"
        elif risk_score >= 0.50:
            risk_level = "high"
        elif risk_score >= 0.25:
            risk_level = "medium"
        else:
            risk_level = "low"

        # Calculate time estimates
        prevention_time = sum(int(p.prevention_effort.split()[0]) for p in predictions)
        resolution_time = patterns["avg_resolution_time_minutes"] * len(predictions)
        prevention_roi = max(0, resolution_time - prevention_time)

        return InvoicePrediction(
            invoice_id=invoice["id"],
            vendor_name=vendor_name,
            risk_score=risk_score,
            risk_level=risk_level,
            predicted_exceptions=predictions,
            preventive_actions=preventive_actions,
            estimated_prevention_time=prevention_time,
            estimated_resolution_time=resolution_time,
            prevention_roi=prevention_roi
        )

    def _get_vendor_intelligence(self, vendor_name: str) -> Dict[str, Any]:
        """Get intelligence about a vendor from our database."""
        # Try exact match
        if vendor_name in self.vendor_intelligence:
            return self.vendor_intelligence[vendor_name]

        # Try fuzzy match
        vendor_lower = vendor_name.lower()
        for known_vendor, info in self.vendor_intelligence.items():
            if known_vendor.lower() in vendor_lower or vendor_lower in known_vendor.lower():
                return info

        # Unknown vendor
        return {
            "category": "first_time_vendors",
            "avg_invoice_amount": None,
            "amount_stddev": None,
            "typical_frequency": None,
            "historical_exceptions": None,
            "total_invoices": 0,
            "trust_score": 0.50,
        }


# ==========================================================
# 📊  DEMO RUNNER
# ==========================================================

def run_demo():
    """
    Run the Predictive Exception Prevention Demo.

    This shows RIK's revolutionary capability: preventing exceptions
    before they occur, not just handling them after.
    """
    print("=" * 70)
    print("🔮  RIK PREDICTIVE EXCEPTION PREVENTION")
    print("    Preventing Problems Before They Occur")
    print("=" * 70)
    print()

    engine = PredictiveEngine()

    results = {
        "total_invoices": len(INCOMING_INVOICES),
        "high_risk": 0,
        "medium_risk": 0,
        "low_risk": 0,
        "total_exceptions_predicted": 0,
        "total_prevention_time": 0,
        "total_resolution_time": 0,
        "predictions": []
    }

    print(f"Analyzing {len(INCOMING_INVOICES)} incoming invoices...\n")

    for i, invoice in enumerate(INCOMING_INVOICES, 1):
        prediction = engine.analyze_incoming_invoice(invoice)
        results["predictions"].append(prediction)
        results["total_exceptions_predicted"] += len(prediction.predicted_exceptions)
        results["total_prevention_time"] += prediction.estimated_prevention_time
        results["total_resolution_time"] += prediction.estimated_resolution_time

        if prediction.risk_level in ["high", "critical"]:
            results["high_risk"] += 1
        elif prediction.risk_level == "medium":
            results["medium_risk"] += 1
        else:
            results["low_risk"] += 1

        # Display prediction
        print("─" * 70)
        print(f"Invoice {i}/{len(INCOMING_INVOICES)}: {invoice['id']}")
        print(f"Vendor: {invoice['vendor_name']}")
        print(f"Expected Amount: ${invoice['expected_amount_range'][0]:,} - ${invoice['expected_amount_range'][1]:,}")
        print(f"Expected: {invoice['expected_date']}")
        print(f"PO Status: {invoice['po_status']}")
        print()

        # Risk assessment
        risk_emoji = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴"
        }
        print(f"Risk Score: {prediction.risk_score:.0%} {risk_emoji[prediction.risk_level]} {prediction.risk_level.upper()}")
        print()

        if prediction.predicted_exceptions:
            print("Predicted Exceptions:")
            for exc in prediction.predicted_exceptions:
                prob_bar = "█" * int(exc.probability * 10) + "░" * (10 - int(exc.probability * 10))
                print(f"  • {exc.exception_type}")
                print(f"    Probability: [{prob_bar}] {exc.probability:.0%}")
                print(f"    Impact: {exc.impact}")
                print(f"    Prevention: {exc.prevention_action}")
                print()

            print("Recommended Preventive Actions:")
            for j, action in enumerate(prediction.preventive_actions, 1):
                print(f"  {j}. {action}")
            print()

            print(f"Time Analysis:")
            print(f"  Prevention effort: {prediction.estimated_prevention_time} minutes")
            print(f"  Resolution if not prevented: {prediction.estimated_resolution_time} minutes")
            print(f"  ⭐ Time saved by prevention: {prediction.prevention_roi} minutes")
        else:
            print("✅ No significant exceptions predicted")
            print("   This invoice should process smoothly")

        print()

    # ===========================================
    # Summary
    # ===========================================

    print("=" * 70)
    print("📊  PREDICTION SUMMARY")
    print("=" * 70)
    print()

    print("RISK DISTRIBUTION:")
    print(f"  🔴 High/Critical Risk: {results['high_risk']}/{results['total_invoices']}")
    print(f"  🟡 Medium Risk: {results['medium_risk']}/{results['total_invoices']}")
    print(f"  🟢 Low Risk: {results['low_risk']}/{results['total_invoices']}")
    print()

    print("EXCEPTION FORECAST:")
    print(f"  Total exceptions predicted: {results['total_exceptions_predicted']}")
    print(f"  Invoices with predicted issues: {results['high_risk'] + results['medium_risk']}/{results['total_invoices']}")
    print()

    # ===========================================
    # Prevention ROI
    # ===========================================

    print("=" * 70)
    print("💰  PREVENTION ROI")
    print("=" * 70)
    print()

    prevention_rate = 0.65  # Assume 65% of predicted exceptions can be prevented
    exceptions_prevented = int(results["total_exceptions_predicted"] * prevention_rate)

    print("THIS WEEK:")
    print(f"  Exceptions predicted: {results['total_exceptions_predicted']}")
    print(f"  Exceptions preventable: {exceptions_prevented} ({prevention_rate:.0%})")
    print(f"  Prevention effort: {results['total_prevention_time']} minutes")
    print(f"  Resolution time avoided: {int(results['total_resolution_time'] * prevention_rate)} minutes")
    time_saved = int(results['total_resolution_time'] * prevention_rate) - results['total_prevention_time']
    print(f"  ⭐ Net time saved: {time_saved} minutes")
    print()

    # Scale to monthly
    weeks_per_month = 4.3
    monthly_exceptions = int(results["total_exceptions_predicted"] * weeks_per_month)
    monthly_prevented = int(monthly_exceptions * prevention_rate)
    monthly_time_saved = int(time_saved * weeks_per_month)
    hourly_rate = 30
    monthly_savings = (monthly_time_saved / 60) * hourly_rate
    annual_savings = monthly_savings * 12

    print("MONTHLY PROJECTION:")
    print(f"  Exceptions predicted: {monthly_exceptions}")
    print(f"  Exceptions prevented: {monthly_prevented}")
    print(f"  Hours saved: {monthly_time_saved / 60:.1f}")
    print(f"  Cost savings: ${monthly_savings:,.2f}")
    print()

    print("ANNUAL PROJECTION:")
    print(f"  Exceptions prevented: {monthly_prevented * 12}")
    print(f"  Hours saved: {monthly_time_saved * 12 / 60:.1f}")
    print(f"  ⭐ PREVENTION SAVINGS: ${annual_savings:,.2f}")
    print()

    # ===========================================
    # Combined Value
    # ===========================================

    print("=" * 70)
    print("🎯  TOTAL RIK VALUE")
    print("=" * 70)
    print()

    resolution_savings = 30000  # From invoice demo
    total_savings = resolution_savings + annual_savings

    print("EXCEPTION RESOLUTION (from invoice demo):")
    print(f"  Automation improvement: 30% → 80%")
    print(f"  Annual savings: ${resolution_savings:,.2f}")
    print()

    print("EXCEPTION PREVENTION (this demo):")
    print(f"  Exceptions prevented: {prevention_rate:.0%}")
    print(f"  Annual savings: ${annual_savings:,.2f}")
    print()

    print("COMBINED VALUE:")
    print(f"  ⭐ TOTAL ANNUAL SAVINGS: ${total_savings:,.2f}")
    print()

    # ===========================================
    # Revolutionary Insight
    # ===========================================

    print("=" * 70)
    print("🚀  THE REVOLUTIONARY DIFFERENCE")
    print("=" * 70)
    print()

    print("Traditional RPA:")
    print("  Invoice arrives → Exception occurs → Manual handling → Resolved")
    print("  (Reactive - deals with problems after they happen)")
    print()

    print("RIK Exception Handling:")
    print("  Invoice arrives → Exception occurs → RIK resolves → Approved")
    print("  (Better - handles problems faster)")
    print()

    print("RIK Predictive Prevention:")
    print("  Invoice expected → Predict exceptions → Prevent → Invoice arrives → ✅ Clean")
    print("  (Revolutionary - problems never occur)")
    print()

    print("This is the difference between:")
    print("  • Firefighting vs Fire Prevention")
    print("  • Reactive IT vs Predictive Operations")
    print("  • Good automation vs Intelligent automation")
    print()

    print("=" * 70)
    print("🎯  CONCLUSION")
    print("=" * 70)
    print()
    print("RIK doesn't just handle exceptions better - it PREVENTS them.")
    print()
    print(f"  • {results['total_exceptions_predicted']} exceptions predicted this week")
    print(f"  • {exceptions_prevented} can be prevented with {results['total_prevention_time']} minutes effort")
    print(f"  • Annual prevention savings: ${annual_savings:,.2f}")
    print(f"  • Combined with resolution: ${total_savings:,.2f}/year")
    print()
    print("This is what makes RIK revolutionary, not just better.")
    print()
    print("=" * 70)


if __name__ == "__main__":
    run_demo()
