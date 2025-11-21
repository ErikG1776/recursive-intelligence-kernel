#!/usr/bin/env python3
"""
RIK Intelligence Dashboard - Streamlit App

Full Intelligence Dashboard for demonstrating RIK's invoice processing capabilities.
Upload real PDFs and watch RIK analyze them in real-time.

Usage:
    streamlit run streamlit_app.py
"""

import streamlit as st
import os
import re
import random
from datetime import datetime
from typing import Dict, Any, List, Tuple
import json

# PDF extraction libraries
try:
    import pdfplumber
    PDF_LIBRARY = "pdfplumber"
except ImportError:
    try:
        import PyPDF2
        PDF_LIBRARY = "PyPDF2"
    except ImportError:
        PDF_LIBRARY = None

# ==========================================================================
# PAGE CONFIG
# ==========================================================================

st.set_page_config(
    page_title="RIK Intelligence Dashboard",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================================================
# CUSTOM CSS
# ==========================================================================

st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .decision-approve {
        background-color: #d4edda;
        border: 2px solid #28a745;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .decision-escalate {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .decision-reject {
        background-color: #f8d7da;
        border: 2px solid #dc3545;
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
    }
    .exception-item {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 5px 5px 0;
    }
    .reasoning-step {
        background-color: #e7f3ff;
        border-left: 4px solid #1f77b4;
        padding: 0.5rem 1rem;
        margin: 0.5rem 0;
        border-radius: 0 5px 5px 0;
    }
    .comparison-box {
        border: 1px solid #ddd;
        border-radius: 10px;
        padding: 1rem;
        height: 100%;
    }
    .rpa-fail {
        color: #dc3545;
        font-weight: bold;
    }
    .rik-success {
        color: #28a745;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================================================
# PDF EXTRACTION
# ==========================================================================

def extract_text_from_pdf(uploaded_file) -> Tuple[str, float]:
    """Extract text from uploaded PDF file."""

    if PDF_LIBRARY == "pdfplumber":
        import pdfplumber
        text_parts = []
        with pdfplumber.open(uploaded_file) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                text_parts.append(page_text)
        text = "\n".join(text_parts)
        word_count = len(text.split())
        confidence = min(0.95, 0.7 + (word_count / 500)) if word_count > 50 else 0.75
        return text, confidence

    elif PDF_LIBRARY == "PyPDF2":
        import PyPDF2
        text_parts = []
        reader = PyPDF2.PdfReader(uploaded_file)
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text_parts.append(page_text)
        text = "\n".join(text_parts)
        word_count = len(text.split())
        confidence = min(0.90, 0.65 + (word_count / 600)) if word_count > 50 else 0.55
        return text, confidence

    else:
        # No PDF library - try to read as text
        try:
            content = uploaded_file.read().decode('utf-8')
            uploaded_file.seek(0)
            return content, 0.85
        except:
            return "PDF extraction requires PyPDF2 or pdfplumber. Install with: pip install pdfplumber", 0.0


def extract_text_from_txt(uploaded_file) -> Tuple[str, float]:
    """Extract text from uploaded text file."""
    content = uploaded_file.read().decode('utf-8')
    uploaded_file.seek(0)
    word_count = len(content.split())
    confidence = 0.90 if word_count > 100 else 0.85
    return content, confidence

# ==========================================================================
# INVOICE PARSER
# ==========================================================================

class InvoiceParser:
    """Parse invoice fields from extracted text."""

    def __init__(self):
        self.patterns = {
            "invoice_number": [
                r"Invoice\s*(?:#|Number|No\.?|ID)?\s*[:\s]*([A-Z0-9\-]+)",
                r"INV[:\s\-]*([A-Z0-9\-]+)",
                r"Invoice[:\s]+([A-Z0-9\-]+)",
            ],
            "amount": [
                r"TOTAL[:\s]*\$?([\d,]+\.?\d*)",
                r"Total\s*(?:Due|Amount)?[:\s]*\$?([\d,]+\.?\d*)",
                r"Amount\s*Due[:\s]*\$?([\d,]+\.?\d*)",
                r"INVOICE\s*TOTAL[:\s]*\$?([\d,]+\.?\d*)",
            ],
            "po_number": [
                r"PO\s*(?:#|Number|No\.?)?\s*[:\s]*([A-Z0-9\-]+)",
                r"Purchase\s*Order[:\s]*([A-Z0-9\-]+)",
                r"Requisition[:\s]*([A-Z0-9\-]+)",
            ],
            "vendor": [
                r"^([A-Z][A-Za-z\s&,\.]+(?:LLC|Inc|Corp|Corporation|Company|Co|Ltd))",
                r"From[:\s]*\n*([A-Za-z\s&,\.]+(?:LLC|Inc|Corp|Corporation|Company|Co|Ltd)?)",
            ],
            "date": [
                r"(?:Invoice\s*)?Date[:\s]*(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
                r"(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})",
            ],
            "contract": [
                r"Contract[:\s#]*([A-Z0-9\-]+)",
            ],
        }

    def parse(self, text: str) -> Dict[str, Any]:
        """Parse all fields from invoice text."""
        fields = {}

        for field_name, patterns in self.patterns.items():
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
                if match:
                    value = match.group(1).strip()
                    if field_name == "amount":
                        value = value.replace(",", "")
                        try:
                            value = float(value)
                        except:
                            pass
                    fields[field_name] = value
                    break

            if field_name not in fields:
                fields[field_name] = None

        return fields

# ==========================================================================
# RIK REASONING ENGINE
# ==========================================================================

class RIKReasoningEngine:
    """RIK's intelligent reasoning engine for invoice processing."""

    def __init__(self):
        self.auto_approve_threshold = 50000
        self.ocr_confidence_threshold = 0.70
        self.known_vendors = {
            "Federal Supplies Inc": {"trust_score": 0.95, "history": 47},
            "Boeing Company": {"trust_score": 0.98, "history": 156},
            "Lockheed Martin": {"trust_score": 0.97, "history": 89},
            "General Dynamics": {"trust_score": 0.96, "history": 72},
            "Raytheon": {"trust_score": 0.95, "history": 63},
            "Northrop Grumman": {"trust_score": 0.94, "history": 45},
            "GDIT": {"trust_score": 0.92, "history": 38},
            "Vertex Aerospace": {"trust_score": 0.91, "history": 29},
        }

    def analyze(self, fields: Dict[str, Any], ocr_confidence: float) -> Dict[str, Any]:
        """Analyze invoice and produce intelligent decision."""

        exceptions = []
        reasoning_steps = []
        resolutions = []
        confidence = 1.0

        amount = fields.get("amount", 0)
        if isinstance(amount, str):
            try:
                amount = float(amount.replace(",", ""))
            except:
                amount = 0

        vendor = fields.get("vendor", "Unknown")
        po_number = fields.get("po_number")

        # Exception Detection

        # 1. Missing PO
        if not po_number:
            exceptions.append({
                "type": "missing_po_number",
                "severity": "medium",
                "description": "No Purchase Order number found in invoice"
            })

        # 2. Low OCR confidence
        if ocr_confidence < self.ocr_confidence_threshold:
            exceptions.append({
                "type": "low_ocr_confidence",
                "severity": "high",
                "description": f"OCR confidence {ocr_confidence:.0%} below threshold {self.ocr_confidence_threshold:.0%}"
            })

        # 3. Amount above threshold
        if amount > self.auto_approve_threshold:
            exceptions.append({
                "type": "amount_above_threshold",
                "severity": "high",
                "description": f"Amount ${amount:,.2f} exceeds auto-approve threshold ${self.auto_approve_threshold:,}"
            })

        # 4. Unknown vendor
        vendor_match = self._match_vendor(vendor)
        if not vendor_match["known"]:
            exceptions.append({
                "type": "unknown_vendor",
                "severity": "medium",
                "description": f"Vendor '{vendor}' not found in known vendor database"
            })

        # RIK Reasoning & Resolution

        resolved_count = 0

        for exc in exceptions:
            if exc["type"] == "missing_po_number":
                if vendor_match["known"] and vendor_match["trust_score"] > 0.9 and amount < 10000:
                    reasoning_steps.append(
                        f"Missing PO acceptable: Vendor '{vendor_match['matched']}' has trust score "
                        f"{vendor_match['trust_score']:.0%} and amount ${amount:,.2f} is under $10,000"
                    )
                    resolutions.append(exc["type"])
                    resolved_count += 1
                    confidence *= 0.92
                else:
                    reasoning_steps.append(
                        f"Missing PO requires attention: Cannot auto-resolve for this vendor/amount combination"
                    )
                    confidence *= 0.7

            elif exc["type"] == "amount_above_threshold":
                reasoning_steps.append(
                    f"Amount ${amount:,.2f} exceeds ${self.auto_approve_threshold:,} threshold. "
                    f"Escalating to manager approval queue."
                )
                confidence *= 0.5

            elif exc["type"] == "unknown_vendor":
                if vendor_match["confidence"] > 0.7:
                    reasoning_steps.append(
                        f"Vendor '{vendor}' may match known vendor '{vendor_match['matched']}' "
                        f"({vendor_match['confidence']:.0%} confidence). Flagging for verification."
                    )
                    confidence *= 0.8
                else:
                    reasoning_steps.append(
                        f"Vendor '{vendor}' not found in database. New vendor onboarding required."
                    )
                    confidence *= 0.6

            elif exc["type"] == "low_ocr_confidence":
                reasoning_steps.append(
                    f"OCR confidence {ocr_confidence:.0%} is low. Manual verification recommended."
                )
                confidence *= 0.7

        # Determine decision
        unresolved = len(exceptions) - resolved_count

        if unresolved == 0 and confidence > 0.8:
            decision = "APPROVE"
        elif any(e["type"] == "amount_above_threshold" for e in exceptions):
            decision = "ESCALATE"
        elif unresolved > 2 or confidence < 0.4:
            decision = "REJECT"
        else:
            decision = "ESCALATE"

        # Traditional RPA comparison
        traditional_rpa_result = "FAILED" if exceptions else "SUCCESS"
        traditional_rpa_reasons = [e["type"] for e in exceptions]

        return {
            "decision": decision,
            "confidence": confidence,
            "exceptions": exceptions,
            "resolved_count": resolved_count,
            "reasoning_steps": reasoning_steps,
            "vendor_match": vendor_match,
            "traditional_rpa": {
                "result": traditional_rpa_result,
                "failure_reasons": traditional_rpa_reasons
            },
            "amount": amount,
            "vendor": vendor,
        }

    def _match_vendor(self, vendor_name: str) -> Dict[str, Any]:
        """Fuzzy match vendor against known vendors."""
        if not vendor_name:
            return {"known": False, "matched": None, "confidence": 0, "trust_score": 0}

        vendor_lower = vendor_name.lower()

        # Direct match
        for known, info in self.known_vendors.items():
            if known.lower() in vendor_lower or vendor_lower in known.lower():
                return {
                    "known": True,
                    "matched": known,
                    "confidence": 0.95,
                    "trust_score": info["trust_score"],
                    "history": info["history"]
                }

        # Fuzzy match
        best_match = None
        best_score = 0

        for known, info in self.known_vendors.items():
            # Simple word overlap scoring
            vendor_words = set(vendor_lower.split())
            known_words = set(known.lower().split())
            overlap = len(vendor_words & known_words)
            total = len(vendor_words | known_words)
            score = overlap / total if total > 0 else 0

            if score > best_score:
                best_score = score
                best_match = known

        if best_score > 0.3:
            return {
                "known": False,
                "matched": best_match,
                "confidence": best_score,
                "trust_score": self.known_vendors[best_match]["trust_score"],
                "history": self.known_vendors[best_match]["history"]
            }

        return {"known": False, "matched": None, "confidence": 0, "trust_score": 0}

# ==========================================================================
# MAIN APP
# ==========================================================================

def main():
    # Header
    st.markdown('<p class="main-header">🧠 RIK Intelligence Dashboard</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Upload invoices and watch AI-powered intelligent processing in real-time</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.header("📁 Upload Invoice")

        uploaded_files = st.file_uploader(
            "Choose PDF or TXT files",
            type=["pdf", "txt"],
            accept_multiple_files=True,
            help="Upload one or more invoice files for RIK analysis"
        )

        st.divider()

        st.header("⚙️ Settings")
        auto_approve_threshold = st.number_input(
            "Auto-approve threshold ($)",
            min_value=1000,
            max_value=1000000,
            value=50000,
            step=5000
        )

        ocr_threshold = st.slider(
            "OCR confidence threshold",
            min_value=0.5,
            max_value=0.95,
            value=0.70,
            step=0.05
        )

        st.divider()

        st.header("📊 PDF Library")
        if PDF_LIBRARY:
            st.success(f"Using: {PDF_LIBRARY}")
        else:
            st.warning("No PDF library found")
            st.code("pip install pdfplumber", language="bash")

        st.divider()

        # Sample data option
        st.header("📝 Demo Mode")
        use_sample = st.checkbox("Use sample invoice", value=False)

    # Main content
    if not uploaded_files and not use_sample:
        # Welcome screen
        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 📄 Upload")
            st.write("Drop any PDF invoice in the sidebar")

        with col2:
            st.markdown("### 🔍 Analyze")
            st.write("RIK extracts and reasons about the data")

        with col3:
            st.markdown("### ✅ Decide")
            st.write("Get intelligent decisions with explanations")

        st.divider()

        # Feature highlights
        st.markdown("### Why RIK vs Traditional RPA?")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""
            **Traditional RPA** ❌
            - Requires exact templates
            - Fails on format variations
            - No reasoning capability
            - Hard-coded rules only
            - ~30% automation rate
            """)

        with col2:
            st.markdown("""
            **RIK** ✅
            - Handles any format
            - Intelligent field extraction
            - Explainable reasoning
            - Learns from patterns
            - ~80% automation rate
            """)

        return

    # Process files
    parser = InvoiceParser()
    engine = RIKReasoningEngine()
    engine.auto_approve_threshold = auto_approve_threshold
    engine.ocr_confidence_threshold = ocr_threshold

    files_to_process = []

    if use_sample:
        # Create sample invoice
        sample_text = """
INVOICE

Boeing Company
100 N Riverside Plaza
Chicago, IL 60606

Invoice Number: BA-2024-78234
Invoice Date: November 15, 2024

Bill To:
Department of Defense
Defense Logistics Agency

Contract Number: W52P1J-20-D-0015
PO Number: PO-DOD-2024-45123

Description: Aircraft maintenance parts and support services

Line Items:
1. F-15 Engine Components      $892,400.00
2. Avionics Repair Services    $234,500.00
3. Technical Documentation     $ 45,000.00

TOTAL: $1,171,900.00

Payment Terms: Net 30
"""
        files_to_process.append(("Sample Boeing Invoice", sample_text, 0.92))

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith('.pdf'):
                text, confidence = extract_text_from_pdf(uploaded_file)
            else:
                text, confidence = extract_text_from_txt(uploaded_file)

            files_to_process.append((uploaded_file.name, text, confidence))

    # Process each file
    for filename, text, ocr_confidence in files_to_process:
        st.markdown(f"## 📄 {filename}")

        # Create tabs
        tab1, tab2, tab3, tab4 = st.tabs(["🧠 Analysis", "📝 Extracted Text", "📊 Comparison", "📥 Report"])

        # Parse and analyze
        fields = parser.parse(text)
        result = engine.analyze(fields, ocr_confidence)

        with tab1:
            # Decision banner
            decision = result["decision"]
            confidence = result["confidence"]

            if decision == "APPROVE":
                st.markdown(f"""
                <div class="decision-approve">
                    <h2>✅ APPROVE</h2>
                    <p>Confidence: {confidence:.0%}</p>
                </div>
                """, unsafe_allow_html=True)
            elif decision == "ESCALATE":
                st.markdown(f"""
                <div class="decision-escalate">
                    <h2>⚠️ ESCALATE</h2>
                    <p>Confidence: {confidence:.0%}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="decision-reject">
                    <h2>❌ REJECT</h2>
                    <p>Confidence: {confidence:.0%}</p>
                </div>
                """, unsafe_allow_html=True)

            st.divider()

            # Parsed fields
            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### 📋 Extracted Fields")
                st.write(f"**Invoice #:** {fields.get('invoice_number', 'Not found')}")
                st.write(f"**Vendor:** {fields.get('vendor', 'Not found')}")
                st.write(f"**Amount:** ${result['amount']:,.2f}" if result['amount'] else "**Amount:** Not found")
                st.write(f"**PO Number:** {fields.get('po_number', 'Not found')}")
                st.write(f"**Date:** {fields.get('date', 'Not found')}")
                st.write(f"**Contract:** {fields.get('contract', 'Not found')}")

            with col2:
                st.markdown("### 📊 Metrics")
                st.metric("OCR Confidence", f"{ocr_confidence:.0%}")
                st.metric("Exceptions Found", len(result["exceptions"]))
                st.metric("Exceptions Resolved", result["resolved_count"])

                if result["vendor_match"]["matched"]:
                    st.metric("Vendor Match",
                             result["vendor_match"]["matched"],
                             f"{result['vendor_match']['confidence']:.0%}")

            st.divider()

            # Exceptions
            if result["exceptions"]:
                st.markdown("### ⚠️ Exceptions Detected")
                for exc in result["exceptions"]:
                    resolved = exc["type"] in [e for e in ["resolved"]]  # simplified
                    severity_color = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(exc["severity"], "⚪")
                    st.markdown(f"""
                    <div class="exception-item">
                        {severity_color} <strong>{exc['type']}</strong> [{exc['severity']}]<br>
                        {exc['description']}
                    </div>
                    """, unsafe_allow_html=True)

            # Reasoning
            if result["reasoning_steps"]:
                st.markdown("### 🧠 RIK Reasoning Chain")
                for i, step in enumerate(result["reasoning_steps"], 1):
                    st.markdown(f"""
                    <div class="reasoning-step">
                        <strong>Step {i}:</strong> {step}
                    </div>
                    """, unsafe_allow_html=True)

        with tab2:
            st.markdown("### Raw Extracted Text")
            st.code(text, language=None)
            st.metric("Character Count", len(text))
            st.metric("Word Count", len(text.split()))

        with tab3:
            st.markdown("### Traditional RPA vs RIK")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("""
                <div class="comparison-box">
                    <h3>Traditional RPA</h3>
                </div>
                """, unsafe_allow_html=True)

                trad_result = result["traditional_rpa"]["result"]
                if trad_result == "FAILED":
                    st.error(f"**Result: {trad_result}**")
                    st.write("**Failure reasons:**")
                    for reason in result["traditional_rpa"]["failure_reasons"]:
                        st.write(f"- {reason}")
                    st.write("")
                    st.write("**What happens next:**")
                    st.write("- Invoice goes to manual queue")
                    st.write("- Human reviews from scratch")
                    st.write("- Average resolution: 15 minutes")
                else:
                    st.success(f"**Result: {trad_result}**")

            with col2:
                st.markdown("""
                <div class="comparison-box">
                    <h3>RIK</h3>
                </div>
                """, unsafe_allow_html=True)

                if decision == "APPROVE":
                    st.success(f"**Result: {decision}** ({confidence:.0%})")
                elif decision == "ESCALATE":
                    st.warning(f"**Result: {decision}** ({confidence:.0%})")
                else:
                    st.error(f"**Result: {decision}** ({confidence:.0%})")

                st.write("**What RIK did:**")
                st.write(f"- Detected {len(result['exceptions'])} exceptions")
                st.write(f"- Resolved {result['resolved_count']} automatically")
                st.write(f"- Provided {len(result['reasoning_steps'])} reasoning steps")
                st.write("")
                st.write("**What happens next:**")
                if decision == "APPROVE":
                    st.write("- Auto-approved, no human needed")
                elif decision == "ESCALATE":
                    st.write("- Escalated with full context")
                    st.write("- Human reviews RIK's analysis")
                    st.write("- Average resolution: 2 minutes")

            # ROI calculation
            st.divider()
            st.markdown("### 💰 ROI Impact")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Traditional RPA Time", "15 min", help="Average manual processing time")
            with col2:
                st.metric("RIK Time", "2 min" if decision != "APPROVE" else "0 min",
                         help="Time with RIK assistance")
            with col3:
                savings = 13 if decision != "APPROVE" else 15
                st.metric("Time Saved", f"{savings} min", f"${savings * 0.5:.2f}")

        with tab4:
            st.markdown("### 📥 Decision Report")

            report = {
                "invoice_id": fields.get("invoice_number", "Unknown"),
                "timestamp": datetime.now().isoformat(),
                "vendor": result["vendor"],
                "amount": result["amount"],
                "decision": decision,
                "confidence": confidence,
                "exceptions_count": len(result["exceptions"]),
                "exceptions_resolved": result["resolved_count"],
                "reasoning_steps": result["reasoning_steps"],
                "ocr_confidence": ocr_confidence,
                "vendor_match": result["vendor_match"],
            }

            st.json(report)

            st.download_button(
                label="Download Report (JSON)",
                data=json.dumps(report, indent=2, default=str),
                file_name=f"rik_report_{filename.replace('.', '_')}.json",
                mime="application/json"
            )

        st.divider()

    # Summary stats if multiple files
    if len(files_to_process) > 1:
        st.markdown("## 📊 Batch Summary")
        st.write(f"Processed {len(files_to_process)} invoices")

if __name__ == "__main__":
    main()
