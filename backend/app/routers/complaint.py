"""
/assist/complaint — Template engine for NCRP cybercrime complaint and bank dispute email.

SCOPE: Pure templating over user-provided incident fields. No ML, no external API calls,
no new dependencies. Accepts structured JSON that can be filled in directly by the user
or forwarded from /check/digital-arrest / /classify/document responses.
"""
import datetime
from typing import Literal, Optional

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.responses import DISCLAIMER, ComplaintResponse

router = APIRouter(prefix="/assist", tags=["complaint"])

_NEXT_STEPS = [
    "File your complaint online at cybercrime.gov.in — available 24/7.",
    "Call 1930 (National Cyber Crime Helpline) immediately — report the incident verbally and get a reference number.",
    "Report to your bank right away — request an immediate hold on the recipient account; the sooner you report, the better the chance of fund recovery before money is moved further.",
    "Collect and preserve all evidence: screenshots, call recordings, transaction receipts, UPI app history.",
    "Do NOT pay anyone who claims they can help recover the money — this is a common follow-up scam.",
    "Share the NCRP complaint number with your bank to strengthen the dispute.",
]

_DIVIDER = "━" * 50
_LEGAL_NOTE = (
    "NOTE: Legal section references are current as of this writing; verify current "
    "section numbers with the NCRP portal or a legal professional before filing, "
    "as citations can be amended."
)


def _ph(value: Optional[str], label: str) -> str:
    """Return value if present, else a bracketed placeholder."""
    return value.strip() if value and value.strip() else f"[{label}]"


def _fmt_amount(amount: Optional[float]) -> str:
    if amount is None:
        return "[AMOUNT]"
    return f"₹{amount:,.2f}"


def _fmt_patterns(patterns: Optional[list[str]]) -> str:
    if not patterns:
        return "[none recorded]"
    return ", ".join(patterns)


def _build_ncrp(req: "ComplaintRequest") -> str:
    today = datetime.date.today().strftime("%d %B %Y")
    lines = [
        "COMPLAINT — CYBER FINANCIAL FRAUD (DIGITAL ARREST SCAM)",
        "To: National Cyber Crime Reporting Portal",
        "    cybercrime.gov.in  |  Helpline: 1930",
        "",
        f"Filed On: {today}",
        "",
        _DIVIDER,
        "COMPLAINANT DETAILS",
        _DIVIDER,
        f"Name:    {_ph(req.complainant_name, 'FULL NAME')}",
        f"Phone:   {_ph(req.complainant_phone, 'PHONE NUMBER')}",
        f"Email:   {_ph(req.complainant_email, 'EMAIL ADDRESS')}",
        f"Address: {_ph(req.complainant_address, 'FULL ADDRESS')}",
        "",
        _DIVIDER,
        "INCIDENT DETAILS",
        _DIVIDER,
        f"Date & Time of Fraud:  {_ph(req.incident_date, 'DATE AND TIME')}",
        f"Platform / Mode:       {_ph(req.platform_used, 'e.g. WhatsApp video call / phone call')}",
        "Nature of Fraud:       Digital Arrest — Impersonation of Government Official",
    ]
    if req.matched_patterns:
        lines.append(f"Scam Patterns Detected: {_fmt_patterns(req.matched_patterns)}")
    lines += [
        "",
        _DIVIDER,
        "INCIDENT DESCRIPTION",
        _DIVIDER,
        _ph(req.incident_description, "DESCRIBE WHAT HAPPENED — who contacted you, what they claimed, what threats were made, what you were told to do"),
        "",
        _DIVIDER,
        "FINANCIAL LOSS",
        _DIVIDER,
        f"Amount Lost:                    {_fmt_amount(req.amount_lost)}",
        f"Mode of Payment:                {_ph(req.payment_mode, 'UPI / NEFT / RTGS / IMPS')}",
        f"Transaction Reference / UTR:    {_ph(req.transaction_reference, 'UTR OR REFERENCE NUMBER')}",
        f"Date of Transaction:            {_ph(req.transaction_date, 'DATE OF TRANSFER')}",
        f"Recipient UPI ID / Account:     {_ph(req.recipient_account, 'RECIPIENT UPI ID OR ACCOUNT NUMBER')}",
    ]
    if req.payment_indicators:
        lines.append(f"Payment Indicators:             {_fmt_patterns(req.payment_indicators)}")
    lines += [
        "",
        _DIVIDER,
        "SUSPECT DETAILS (if known)",
        _DIVIDER,
        f"Name Claimed:        {_ph(req.suspect_name, 'NAME GIVEN BY CALLER')}",
        f"Phone Number Used:   {_ph(req.suspect_phone, 'CALLER PHONE NUMBER')}",
        f"UPI ID Provided:     {_ph(req.suspect_upi_id, 'UPI ID GIVEN FOR PAYMENT')}",
        f"Claimed Designation: {_ph(req.suspect_claimed_agency, 'e.g. CBI Officer / TRAI Department')}",
        "",
        _DIVIDER,
        "EVIDENCE AVAILABLE",
        _DIVIDER,
        "[ ] Screenshots of conversation / video call",
        "[ ] Call recording (if available)",
        "[ ] Transaction receipt / UPI app history",
        "[ ] Any documents or notices shared by the fraudster",
        "",
        _DIVIDER,
        "REQUESTED ACTION",
        _DIVIDER,
        "1. Immediate freeze of the fraudulent recipient account(s).",
        "2. Tracing, identification, and arrest of the suspect(s).",
        "3. Recovery and refund of the fraudulently transferred amount.",
        "4. Registration of FIR under relevant sections of the Information",
        "   Technology Act 2000 (§66C identity theft, §66D impersonation) and",
        "   Bharatiya Nyaya Sanhita 2023 (§318 cheating, §319 cheating by impersonation).",
        "",
        "I affirm that the above information is true and correct to the best of my knowledge.",
        "",
        "Signature: _____________________",
        f"Date:      {today}",
        "",
        _LEGAL_NOTE,
    ]
    return "\n".join(lines)


def _build_bank_dispute(req: "ComplaintRequest") -> str:
    today = datetime.date.today().strftime("%d %B %Y")
    acct_last4 = (req.account_number or "")[-4:] or "XXXX"
    subject = (
        f"URGENT — Fraudulent Transaction Dispute | "
        f"Account {acct_last4} | "
        f"Ref: {req.transaction_reference or '[UTR]'}"
    )
    lines = [
        f"Subject: {subject}",
        "",
        f"To: Customer Grievance / Nodal Officer",
        f"    {_ph(req.bank_name, 'BANK NAME')}",
        "",
        f"Date: {today}",
        "",
        "Dear Sir / Madam,",
        "",
        "I am writing to formally dispute a fraudulent transaction on my account",
        "and request immediate action to freeze the recipient account and reverse",
        "the transfer.",
        "",
        _DIVIDER,
        "ACCOUNT HOLDER DETAILS",
        _DIVIDER,
        f"Name:              {_ph(req.complainant_name, 'FULL NAME')}",
        f"Account Number:    {_ph(req.account_number, 'ACCOUNT NUMBER')}",
        f"Registered Phone:  {_ph(req.complainant_phone, 'REGISTERED PHONE')}",
        f"Email:             {_ph(req.complainant_email, 'EMAIL ADDRESS')}",
        "",
        _DIVIDER,
        "DISPUTED TRANSACTION",
        _DIVIDER,
        f"Transaction Date:      {_ph(req.transaction_date, 'DATE OF TRANSFER')}",
        f"Amount:                {_fmt_amount(req.amount_lost)}",
        f"Mode:                  {_ph(req.payment_mode, 'UPI / NEFT / RTGS / IMPS')}",
        f"Transaction Ref / UTR: {_ph(req.transaction_reference, 'UTR OR REFERENCE NUMBER')}",
        f"Transferred To:        {_ph(req.recipient_account, 'RECIPIENT UPI ID OR ACCOUNT')}",
        "",
        _DIVIDER,
        "REASON FOR DISPUTE",
        _DIVIDER,
        (
            f"I am the victim of a 'Digital Arrest' cybercrime fraud, a scheme in which "
            f"criminals impersonating {_ph(req.suspect_claimed_agency, 'government officials')} "
            f"coerced me into making the above payment under duress and threat of arrest. "
            f"This is a known fraud pattern formally flagged by the Ministry of Home Affairs "
            f"and the Reserve Bank of India."
        ),
        "",
        _ph(req.incident_description, "BRIEF DESCRIPTION OF WHAT HAPPENED"),
        "",
        _DIVIDER,
        "NCRP COMPLAINT REFERENCE",
        _DIVIDER,
        f"NCRP Complaint Number: {_ph(req.ncrp_complaint_number, 'FILE AT cybercrime.gov.in / 1930 — ENTER NUMBER HERE')}",
        "(Complaint filed with National Cyber Crime Reporting Portal / 1930 helpline.)",
        "",
        _DIVIDER,
        "REQUESTED ACTION",
        _DIVIDER,
        "1. Immediately freeze / place a hold on the recipient account listed above.",
        "2. Initiate transaction reversal / chargeback under the RBI Master Direction",
        "   on Limiting Liability of Customers in Unauthorised Electronic Banking",
        "   Transactions (RBI/2017-18/15).",
        "3. Coordinate with the receiving bank to freeze the fraudulent account.",
        "4. Provide written acknowledgment of this dispute within 24 hours.",
        "5. Share a complaint tracking number for follow-up.",
        "",
        "Yours faithfully,",
        _ph(req.complainant_name, "FULL NAME"),
        f"Phone: {_ph(req.complainant_phone, 'PHONE')}",
        f"Date:  {today}",
        "",
        _LEGAL_NOTE,
    ]
    return "\n".join(lines)


class ComplaintRequest(BaseModel):
    complaint_type: Literal["ncrp", "bank_dispute", "both"]

    # Complainant identity
    complainant_name: Optional[str] = None
    complainant_phone: Optional[str] = None
    complainant_email: Optional[str] = None
    complainant_address: Optional[str] = None

    # Incident
    incident_date: Optional[str] = None
    incident_description: Optional[str] = Field(None, max_length=2000)
    platform_used: Optional[str] = None
    suspect_name: Optional[str] = None
    suspect_phone: Optional[str] = None
    suspect_upi_id: Optional[str] = None
    suspect_claimed_agency: Optional[str] = None

    # Financial
    amount_lost: Optional[float] = Field(None, ge=0)
    payment_mode: Optional[str] = None
    transaction_reference: Optional[str] = None
    transaction_date: Optional[str] = None
    recipient_account: Optional[str] = None

    # Bank
    bank_name: Optional[str] = None
    account_number: Optional[str] = None

    # Forwarded from prior endpoint responses
    ncrp_complaint_number: Optional[str] = None
    matched_patterns: Optional[list[str]] = None
    payment_indicators: Optional[list[str]] = None


@router.post("/complaint", response_model=ComplaintResponse)
async def generate_complaint(req: ComplaintRequest) -> ComplaintResponse:
    """Generate a ready-to-file NCRP complaint text and/or bank dispute email.

    Pure templating — no ML, no external API. Accepts incident fields entered
    directly or forwarded from /check/digital-arrest and /classify/document responses.
    """
    ncrp_text = _build_ncrp(req) if req.complaint_type in ("ncrp", "both") else None
    bank_text = _build_bank_dispute(req) if req.complaint_type in ("bank_dispute", "both") else None

    return ComplaintResponse(
        ncrp_complaint_text=ncrp_text,
        bank_dispute_text=bank_text,
        next_steps=_NEXT_STEPS,
        disclaimer=DISCLAIMER,
    )
