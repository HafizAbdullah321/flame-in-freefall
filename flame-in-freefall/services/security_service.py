"""Security, Input Sanitization & Guardrails Service.

Prevents Cross-Site Scripting (XSS), prompt injection attacks, hazardous sabotage commands,
and invalid numerical inputs before they reach analytical or language model pipelines.
Complies with NASA Software Safety (NASA-STD-8719.13) and Trustworthy AI principles.
"""
import html
import re
from typing import Tuple, List, Optional

# Maximum permissible user query length to prevent token-exhaustion DoS
MAX_INPUT_LENGTH = 2000

# Adversarial prompt injection, jailbreak, and delimiter escape patterns
INJECTION_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior)\s+(instructions|prompts)",
    r"system\s*:\s*you\s+are\s+now",
    r"disregard\s+the\s+above",
    r"repeat\s+the\s+system\s+prompt",
    r"output\s+your\s+instructions",
    r"you\s+are\s+in\s+developer\s+mode",
    r"you\s+are\s+no\s+longer",
    r"bypass\s+all\s+(rules|safety|guardrails)",
    r"act\s+as\s+an\s+unfiltered",
    r"dan\s+mode",
    r"<script[\s>]",
    r"javascript\s*:",
    r"<\s*/?context\s*>",
    r"\[\s*/?inst\s*\]",
    r"<\s*\|\s*im_start\s*\|",
    r"<\s*\|\s*im_end\s*\|",
    r"<<\s*SYS\s*>>",
]

# Aerospace hazard, sabotage, and illicit ordnance patterns
AEROSPACE_HAZARD_PATTERNS = [
    r"(make|synthesize|build|create)\s+an?\s+(improvised\s+)?(bomb|explosive|incendiary\s+device|molotov)",
    r"(sabotage|disable|override|defeat)\s+(the\s+)?(relief\s+valve|eclss|oxygen\s+sensor|fire\s+alarm|extinguisher)",
    r"(cause|trigger)\s+(a\s+)?cabin\s+flashover",
]

class SecurityService:
    """Security utilities for user input validation, sanitization, and safety."""

    @staticmethod
    def sanitize_text(user_input: Optional[str]) -> str:
        """Sanitize raw user text to prevent XSS injection in HTML/Markdown cards.
        
        Strips invisible zero-width unicode characters and escapes HTML delimiters.
        """
        if not user_input:
            return ""
        # Strip zero-width and invisible control characters often used to evade regex
        zero_width = dict.fromkeys([0x200B, 0x200C, 0x200D, 0xFEFF, 0x202A, 0x202B, 0x202C, 0x202D, 0x202E])
        cleaned = user_input.translate(zero_width)
        # Retain standard whitespace and printable ASCII/UTF-8
        cleaned = "".join(ch for ch in cleaned if ch.isprintable() or ch in "\n\r\t")
        # Escape HTML special characters (&, <, >, ", ')
        return html.escape(cleaned.strip())

    @staticmethod
    def detect_prompt_injection(prompt: str) -> Tuple[bool, Optional[str]]:
        """Scan input for prompt injection, adversarial delimiters, or hazardous commands.
        
        Returns (is_safe, failure_reason)
        """
        if not prompt:
            return True, None

        # 1. Length DoS validation
        if len(prompt) > MAX_INPUT_LENGTH:
            return False, f"Input rejected: query length ({len(prompt)}) exceeds disallowed limit ({MAX_INPUT_LENGTH} characters)."

        lower_prompt = prompt.lower()

        # 2. Adversarial prompt injection & delimiter escape
        for pat in INJECTION_PATTERNS:
            if re.search(pat, lower_prompt):
                return False, f"Input rejected: contains disallowed system override or delimiter pattern '{pat}'."

        # 3. Aerospace hazard and life-support sabotage filter
        for pat in AEROSPACE_HAZARD_PATTERNS:
            if re.search(pat, lower_prompt):
                return False, f"Input rejected: contains disallowed aerospace safety hazard / sabotage instruction."

        return True, None

    @staticmethod
    def validate_scenario_bounds(
        pressure_kpa: float,
        o2_pct: float,
        gravity_g: float,
    ) -> Tuple[bool, List[str]]:
        """Validate scenario input values against physical aerospace reality."""
        errors = []
        if pressure_kpa <= 0:
            errors.append("Total pressure must be strictly greater than 0 kPa.")
        elif pressure_kpa > 500.0:
            errors.append("Total pressure exceeds maximum realistic spacecraft rating (500 kPa).")

        if o2_pct <= 0:
            errors.append("Oxygen concentration must be greater than 0%.")
        elif o2_pct > 100.0:
            errors.append("Oxygen concentration cannot exceed 100%.")

        if gravity_g < 0:
            errors.append("Gravity acceleration cannot be negative.")
        elif gravity_g > 10.0:
            errors.append("Gravity exceeds realistic acceleration regime (max 10g).")

        return len(errors) == 0, errors
