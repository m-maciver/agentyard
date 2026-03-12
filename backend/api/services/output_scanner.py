"""
AgentYard — Output Scanner
Scans task output for integrity issues before delivery.

This is NOT a quality check. Quality is subjective and handled by the
review/dispute system over time.

This scanner catches:
  - Blank or empty files
  - Corrupted data (invalid encoding, truncated content)
  - Known malware signatures
  - Suspiciously small output relative to task complexity

It does NOT check:
  - Whether the output is "good enough"
  - Whether the output matches the brief
  - Grammar, style, or formatting quality
"""
import base64
import hashlib
import logging
import re
from dataclasses import dataclass
from typing import Optional

logger = logging.getLogger(__name__)

# Known malware signature prefixes (hex)
# These are simplified indicators — a production system would use ClamAV or similar
MALWARE_SIGNATURES = [
    "4d5a",        # MZ header (Windows PE executable)
    "7f454c46",    # ELF header (Linux executable)
    "cafebabe",    # Java class file / Mach-O fat binary
    "504b0304",    # ZIP (could contain payloads) — only flagged if unexpected
]

# Minimum output length to consider non-blank (bytes)
MIN_OUTPUT_LENGTH = 10

# Maximum ratio of null bytes before flagging as corrupted
MAX_NULL_BYTE_RATIO = 0.3


@dataclass
class ScanResult:
    """Result of an output integrity scan."""
    passed: bool
    reason: Optional[str] = None
    warnings: list[str] | None = None

    def to_dict(self) -> dict:
        result = {"passed": self.passed}
        if self.reason:
            result["reason"] = self.reason
        if self.warnings:
            result["warnings"] = self.warnings
        return result


def scan_output(content: str | bytes, content_type: str = "text") -> ScanResult:
    """
    Scan task output for integrity issues.

    Args:
        content: The output content (string or bytes)
        content_type: "text", "binary", or "base64"

    Returns:
        ScanResult with passed=True if clean, passed=False if issues found.
    """
    warnings: list[str] = []

    # ── Handle empty/None ──
    if content is None:
        return ScanResult(passed=False, reason="Output is empty — no content provided")

    # ── Normalize to bytes ──
    if isinstance(content, str):
        if content_type == "base64":
            try:
                raw_bytes = base64.b64decode(content)
            except Exception:
                return ScanResult(passed=False, reason="Output contains invalid base64 encoding")
        else:
            raw_bytes = content.encode("utf-8", errors="replace")
    else:
        raw_bytes = content

    # ── Check for blank/empty ──
    stripped = raw_bytes.strip()
    if len(stripped) == 0:
        return ScanResult(passed=False, reason="Output is blank — file contains only whitespace")

    if len(stripped) < MIN_OUTPUT_LENGTH:
        return ScanResult(
            passed=False,
            reason=f"Output is suspiciously short ({len(stripped)} bytes)"
        )

    # ── Check for corruption (high null byte ratio) ──
    null_count = raw_bytes.count(b"\x00")
    if len(raw_bytes) > 0 and (null_count / len(raw_bytes)) > MAX_NULL_BYTE_RATIO:
        return ScanResult(
            passed=False,
            reason=f"Output appears corrupted — {null_count}/{len(raw_bytes)} null bytes detected"
        )

    # ── Check for invalid UTF-8 (text content only) ──
    if content_type == "text" and isinstance(content, str):
        replacement_count = content.count("\ufffd")
        if replacement_count > len(content) * 0.1:
            return ScanResult(
                passed=False,
                reason="Output contains significant encoding errors"
            )

    # ── Check for malware signatures ──
    hex_prefix = raw_bytes[:8].hex().lower()
    for sig in MALWARE_SIGNATURES:
        if hex_prefix.startswith(sig):
            # ZIP files are only suspicious if content_type is "text"
            if sig == "504b0304" and content_type != "text":
                warnings.append("Output is a ZIP archive — verify contents")
                continue
            return ScanResult(
                passed=False,
                reason=f"Output contains executable binary data (signature: {sig})"
            )

    # ── Check for embedded scripts in text ──
    if content_type == "text" and isinstance(content, str):
        script_patterns = [
            r"<script[^>]*>",
            r"javascript:",
            r"data:text/html",
            r"on\w+\s*=\s*[\"']",
        ]
        for pattern in script_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                warnings.append("Output contains embedded script tags")
                break

    # ── Passed ──
    result = ScanResult(passed=True)
    if warnings:
        result.warnings = warnings
    return result
