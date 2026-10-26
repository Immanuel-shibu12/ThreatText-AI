"""
ThreatText AI - Text Preprocessing & Email Parsing Module
Implements domain-aware NLP cleaning, tokenization-friendly normalization,
preservation of cybersecurity indicators, and .eml / .txt parsing.
"""

import re
import html
import email
from email import policy
from email.parser import BytesParser, Parser
from typing import Dict, Any, Tuple

# Security-critical urgency & action phrases to preserve/highlight
SUSPICIOUS_INDICATORS = [
    r"\burgent\b",
    r"\bverify your account\b",
    r"\baccount suspended\b",
    r"\bpassword reset\b",
    r"\bconfirm your identity\b",
    r"\bimmediate action required\b",
    r"\bunauthorized login\b",
    r"\bsecurity alert\b",
    r"\bclick here\b",
    r"\bupdate billing\b",
    r"\bfailure to respond\b",
    r"\bwire transfer\b",
    r"\baccess denied\b",
    r"\bclaim your prize\b",
    r"\brefund notification\b"
]

def strip_html_tags(text: str) -> str:
    """Removes HTML markup while preserving readable whitespace and decoded characters."""
    if not isinstance(text, str):
        return ""
    # Remove script and style elements
    text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", text, flags=re.DOTALL | re.IGNORECASE)
    # Replace <br> and <p> with spaces to avoid joining words
    text = re.sub(r"<(br|p|div|tr|li)[^>]*>", " ", text, flags=re.IGNORECASE)
    # Strip remaining HTML tags
    clean = re.sub(r"<[^>]+>", " ", text)
    # Unescape HTML entities after tag stripping so symbols like &lt; become < without being stripped as tags
    clean = html.unescape(clean)
    return clean

def normalize_urls_and_emails(text: str) -> str:
    """
    Normalizes URLs and email addresses to canonical tokens while
    retaining security signal features.
    """
    if not isinstance(text, str):
        return ""
    
    # Replace IP-based URLs (often phishing indicators: http://192.168.1.1/login)
    text = re.sub(r"https?://\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}[^\s]*", " ip_url_link ", text, flags=re.IGNORECASE)
    
    # Replace standard URLs with token, but also retain 'http' or 'https' indicator
    text = re.sub(r"https://[^\s<>\"']+", " secure_url_token ", text, flags=re.IGNORECASE)
    text = re.sub(r"http://[^\s<>\"']+", " http_url_token ", text, flags=re.IGNORECASE)
    text = re.sub(r"www\.[^\s<>\"']+", " web_link_token ", text, flags=re.IGNORECASE)
    
    # Normalize email addresses
    text = re.sub(r"[\w\.-]+@[\w\.-]+\.\w+", " email_address_token ", text)
    
    # Normalize excessive dollar/currency signs and large sums
    text = re.sub(r"[\$£€]\s*\d+([,\.]\d+)*", " currency_amount_token ", text)
    
    return text

def clean_email_text(text: str) -> str:
    """
    Comprehensive text preprocessing pipeline for phishing classification:
    - HTML stripping and unescaping
    - URL & email normalization
    - Retaining negation and security-specific semantics
    - Lowercasing and whitespace normalization
    """
    if not isinstance(text, str) or not text.strip():
        return ""
    
    # Step 1: Strip HTML
    cleaned = strip_html_tags(text)
    
    # Step 2: Normalize URLs and special tokens
    cleaned = normalize_urls_and_emails(cleaned)
    
    # Step 3: Remove unwanted special characters, but keep alphanumeric, apostrophes, and basic punctuation
    cleaned = re.sub(r"[^\w\s\$\%\!\?'-]", " ", cleaned)
    
    # Step 4: Normalize repeated punctuation (e.g., '!!!!' -> '!!', '????' -> '??')
    cleaned = re.sub(r"!{2,}", " !! ", cleaned)
    cleaned = re.sub(r"\?{2,}", " ?? ", cleaned)
    
    # Step 5: Convert to consistent lowercase
    cleaned = cleaned.lower()
    
    # Step 6: Normalize whitespace (multiple spaces/newlines into single space)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    
    return cleaned

def parse_raw_email(raw_content: str | bytes) -> Dict[str, Any]:
    """
    Parses an RFC 822 email string or bytes (standard .eml format).
    Extracts Subject, From, To, Date, and decoded body.
    """
    if isinstance(raw_content, str):
        msg = Parser(policy=policy.default).parsestr(raw_content)
    else:
        msg = BytesParser(policy=policy.default).parsebytes(raw_content)
        
    subject = msg.get("Subject", "") or ""
    sender = msg.get("From", "") or ""
    recipient = msg.get("To", "") or ""
    date_sent = msg.get("Date", "") or ""
    
    # Extract body content (prefer text/plain, fallback to text/html)
    body = ""
    if msg.is_multipart():
        plain_parts = []
        html_parts = []
        for part in msg.walk():
            content_type = part.get_content_type()
            content_disposition = str(part.get("Content-Disposition", ""))
            if "attachment" in content_disposition:
                continue
            if content_type == "text/plain":
                try:
                    plain_parts.append(part.get_content())
                except Exception:
                    pass
            elif content_type == "text/html":
                try:
                    html_parts.append(part.get_content())
                except Exception:
                    pass
        if plain_parts:
            body = "\n".join(plain_parts)
        elif html_parts:
            body = "\n".join(html_parts)
    else:
        try:
            body = msg.get_content() or ""
        except Exception:
            body = str(msg.get_payload())
            
    combined = f"Subject: {subject}\n\n{body}"
    
    return {
        "subject": subject,
        "from": sender,
        "to": recipient,
        "date": date_sent,
        "body": body,
        "combined_text": combined,
        "cleaned_text": clean_email_text(combined)
    }

def parse_email_file(file_content: str | bytes, filename: str) -> Dict[str, Any]:
    """
    Convenience function to parse either .eml or .txt email file contents.
    """
    fn_lower = filename.lower()
    if fn_lower.endswith(".eml"):
        return parse_raw_email(file_content)
    else:
        # Plain text file format
        text = file_content.decode("utf-8", errors="ignore") if isinstance(file_content, bytes) else file_content
        lines = text.strip().splitlines()
        subject = ""
        body_lines = []
        
        # Simple heuristic to extract Subject: header if present at top
        for i, line in enumerate(lines):
            if i < 5 and line.lower().startswith("subject:"):
                subject = line[8:].strip()
            else:
                body_lines.append(line)
                
        body = "\n".join(body_lines).strip()
        combined = f"Subject: {subject}\n\n{body}" if subject else body
        
        return {
            "subject": subject or "(No explicit subject)",
            "from": "Unknown (Text Upload)",
            "to": "Recipient",
            "date": "N/A",
            "body": body,
            "combined_text": combined,
            "cleaned_text": clean_email_text(combined)
        }

if __name__ == "__main__":
    sample_raw = """Subject: URGENT: Verify Your Bank Account Immediately!
From: Security Alert <support@sec-bank-update.com>
To: target@victim.com
Date: Mon, 26 Oct 2026 12:00:00 -0400

Dear Valued Customer,
We detected unauthorized login attempts to your account.
Your online banking access will be suspended within 24 hours.
Please click the link below to verify your password immediately:
http://192.168.1.100/verify-login?id=82374
Thank you.
"""
    parsed = parse_raw_email(sample_raw)
    print("Subject:", parsed["subject"])
    print("Cleaned text:\n", parsed["cleaned_text"])
