# backend/legal_mapping.py
import re
from typing import List, Dict

class LegalMapper:
    """
    Mini-project legal mapping engine (NOT legal advice).

    Inputs:
      - toxic_score (0..1)
      - threat_score (0..1)
      - text (optional, but recommended for sexual/CSAM/stalking cues)

    Outputs:
      - severity_level: "Minimal" | "Low" | "Moderate" | "High" | "Critical"
      - legal_sections: list[str]
      - reasons: list[str]
      - guidance: list[str]  (what user can do next)
    """

    # --- Keyword cues (simple heuristic) ---
    STALKING_PATTERNS = [
        r"\bi will follow you\b", r"\bi'm following you\b", r"\bwatching you\b",
        r"\bi know where you live\b", r"\bi will find you\b", r"\btrack you\b",
        r"\bstalk\b", r"\bfollow your\b", r"\bmonitor you\b"
    ]

    SEXUAL_HARASSMENT_CUES = [
        "nude", "nudes", "boobs", "porn", "sex", "kiss me", "sleep with me",
        "send pics", "send photo", "send video", "onlyfans", "xxx"
    ]

    # keep CSAM cues conservative (do not expand graphically)
    CSAM_CUES = [
        "child porn", "minor nude", "underage", "kid nude", "school girl nude"
    ]

    PRIVACY_CUES = [
        "leak", "leaked", "private", "recording", "recorded", "video", "photo", "pics",
        "mms", "dm screenshots", "share your pics"
    ]

    def _has_any_pattern(self, text: str, patterns: List[str]) -> bool:
        t = (text or "").lower()
        return any(re.search(p, t) for p in patterns)

    def _has_any_keyword(self, text: str, keywords: List[str]) -> bool:
        t = (text or "").lower()
        return any(k in t for k in keywords)

    # ✅ More divisions than Low/Medium/High
    def severity_from_scores(self, toxic_score: float, threat_score: float) -> str:
        """
        Severity mapping using two independent scores:
          - toxic_score: raw model probability of toxicity (0-1)
          - threat_score: keyword+negation-aware threat level (0-1, typically lower)
        """
        # Critical: very high threat AND toxicity
        if threat_score >= 0.85 and toxic_score >= 0.90:
            return "Critical"
        # High: strong threat OR very high toxicity
        if threat_score >= 0.70 or toxic_score >= 0.92:
            return "High"
        # Moderate: moderate threat OR high toxicity
        if threat_score >= 0.45 or toxic_score >= 0.75:
            return "Moderate"
        # Low: some threat signal OR moderate toxicity
        if threat_score >= 0.25 or toxic_score >= 0.50:
            return "Low"
        # Minimal
        return "Minimal"

    def map_law(self, text: str, toxic_score: float, threat_score: float) -> Dict:
        """
        Returns dict for frontend/API:
          {
            "severity": ...,
            "legal_sections": [...],
            "reasons": [...],
            "guidance": [...]
          }
        """
        severity = self.severity_from_scores(toxic_score, threat_score)

        legal_sections: List[str] = []
        reasons: List[str] = []
        guidance: List[str] = []

        # --- Threats (IPC 503) ---
        if threat_score >= 0.45:
            legal_sections.append("IPC 503 — Criminal intimidation (threats)")
            reasons.append(f"Threat score {threat_score:.2f} indicates intimidation/threat language.")

        # --- General harassment / insult (IPC 509) ---
        if toxic_score >= 0.40:
            legal_sections.append("IPC 509 — Insult to modesty / harassment")
            reasons.append(f"Toxicity score {toxic_score:.2f} indicates abusive/harassing language.")

        # --- Stalking (IPC 354D) ---
        if self._has_any_pattern(text, self.STALKING_PATTERNS) and severity in ["Moderate", "High", "Critical"]:
            legal_sections.append("IPC 354D — Stalking / cyber stalking")
            reasons.append("Stalking/monitoring phrases detected + elevated severity.")

        # --- Sexual harassment (IPC 354A) ---
        if self._has_any_keyword(text, self.SEXUAL_HARASSMENT_CUES) and severity in ["Moderate", "High", "Critical"]:
            legal_sections.append("IPC 354A — Sexual harassment")
            reasons.append("Sexual harassment cues detected in text + elevated severity.")

        # --- Privacy violation (IT Act 66E) ---
        if self._has_any_keyword(text, self.PRIVACY_CUES) and severity in ["Low", "Moderate", "High", "Critical"]:
            legal_sections.append("IT Act 66E — Violation of privacy / online harassment")
            reasons.append("Privacy/leak/recording/photo/video cues detected.")

        # --- Sexually explicit content (IT Act 67A) ---
        if self._has_any_keyword(text, ["sex", "porn", "xxx", "nude", "nudes"]) and severity in ["Moderate", "High", "Critical"]:
            legal_sections.append("IT Act 67A — Sexually explicit content")
            reasons.append("Explicit content cues detected + elevated severity.")

        # --- CSAM (IT Act 67B) ---
        if self._has_any_keyword(text, self.CSAM_CUES):
            legal_sections.append("IT Act 67B — Child sexual abuse material (CSAM)")
            reasons.append("CSAM-related cue detected (treat as highest priority).")
            severity = "Critical"  # override for safety

        # --- Add reporting guidance based on severity ---
        if severity in ["Minimal"]:
            guidance += [
                "If it continues, save screenshots and message links as evidence.",
                "Consider blocking/muting the account and tightening privacy settings."
            ]

        if severity in ["Low", "Moderate"]:
            guidance += [
                "Save evidence: screenshots, usernames, URLs, timestamps.",
                "Use in-app report/block features; inform a trusted person if needed.",
                "If repeated, consider reporting on the Cyber Crime Portal."
            ]

        if severity in ["High", "Critical"]:
            guidance += [
                "Do not engage. Preserve evidence immediately (screenshots/URLs/timestamps).",
                "Report urgently on the Cyber Crime Portal (online complaint/FIR).",
                "If you feel in immediate danger, contact local police / emergency help."
            ]

        # Always include portal mention (as user asked)
        guidance.append("Cyber Crime Portal — Online FIR & reporting (India): use for serious harassment/threats/CSAM.")

        # Deduplicate while preserving order
        seen = set()
        dedup_sections = []
        for s in legal_sections:
            if s not in seen:
                seen.add(s)
                dedup_sections.append(s)

        return {
            "severity": severity,
            "legal_sections": dedup_sections,
            "reasons": reasons,
            "guidance": guidance
        }
