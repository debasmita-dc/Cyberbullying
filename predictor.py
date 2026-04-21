import torch
import numpy as np
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from preprocessing import TextPreprocessor
from config import Config


class Predictor:
    """
    Binary toxicity classifier using the fine-tuned DistilBERT model.

    The model outputs two classes:
      - Class 0: Non-toxic / Safe
      - Class 1: Toxic / Bullying

    We derive a separate threat_score using keyword heuristics so the
    severity mapper has two independent signals instead of one duplicated.

    Negation and humour cues are used to:
      1. Reduce the threat_score
      2. Adjust the effective toxic_score for labelling
    """

    # Keywords that suggest elevated threat (beyond generic toxicity)
    THREAT_KEYWORDS = [
        "kill", "murder", "die", "dead", "hurt", "attack", "stab", "shoot",
        "bomb", "destroy", "burn", "beat", "punch", "slap", "rape",
        "find you", "come for you", "follow you", "hunt you", "track you",
        "watch you", "end you", "finish you", "eliminate"
    ]

    # Cues that soften / negate harmful intent
    NEGATION_CUES = [
        "won't", "wont", "wouldn't", "wouldnt", "will not", "would not",
        "don't", "dont", "do not", "not going to", "never", "no way",
        "just kidding", "jk", "kidding", "joking", "sarcasm", "not really",
        "but i won't", "but i wont", "but not", "not gonna",
    ]

    # Humour / softening cues
    HUMOUR_CUES = [
        "lol", "lmao", "lmfao", "haha", "hehe", "rofl", "xd", "😂",
        "jk", "just kidding", "kidding", "joking", "joke",
        "ily", "love you", "luv u", "luv you", "but ily",
    ]

    def __init__(self):
        self.pre = TextPreprocessor()

        model_dir = Config.MODEL_DIR

        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir)
        self.model.eval()

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model.to(self.device)

    def _has_cues(self, text: str, cue_list: list) -> int:
        """Count how many cues from the list are present in text."""
        lower = text.lower()
        return sum(1 for c in cue_list if c in lower)

    def _compute_threat_score(self, text: str, toxic_prob: float) -> float:
        """
        Compute a threat score INDEPENDENT from the raw toxic probability.
        Uses keyword matching + negation/humour awareness.
        """
        lower = text.lower()

        # Check for threat keywords
        threat_hits = self._has_cues(text, self.THREAT_KEYWORDS)

        if threat_hits == 0:
            # No threatening language → baseline threat scaled down from toxicity
            return round(min(toxic_prob * 0.35, 0.35), 4)

        # Check for negation & humour cues that soften threat
        negation_hits = self._has_cues(text, self.NEGATION_CUES)
        humour_hits = self._has_cues(text, self.HUMOUR_CUES)
        softening = negation_hits + humour_hits

        if softening > 0:
            # Negation / humour present → heavily discount threat
            discount = min(0.20 * softening, 0.75)
            threat = toxic_prob * max(0.10, 1.0 - discount)
            return round(min(threat, 0.40), 4)  # capped

        # Genuine threat: keywords present, no softening
        keyword_boost = min(threat_hits * 0.15, 0.4)
        threat = toxic_prob * (0.6 + keyword_boost)
        return round(min(threat, 0.95), 4)

    def _compute_effective_toxic(self, text: str, raw_toxic: float) -> float:
        """
        Adjust the raw toxic probability when negation/humour cues are present.
        This doesn't change the model's output — it creates an 'effective' score
        that better represents actual intent for labelling and severity.
        """
        softening = self._has_cues(text, self.NEGATION_CUES) + self._has_cues(text, self.HUMOUR_CUES)

        if softening == 0:
            return raw_toxic

        # Each softening cue reduces confidence by ~15-20%
        discount = min(0.15 * softening, 0.55)
        effective = raw_toxic * (1.0 - discount)
        return round(effective, 4)

    @torch.no_grad()
    def predict(self, raw_text: str) -> dict:
        cleaned = self.pre.clean(raw_text)

        inputs = self.tokenizer(
            cleaned,
            truncation=True,
            padding=True,
            max_length=128,
            return_tensors="pt"
        ).to(self.device)

        outputs = self.model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1).squeeze().cpu().numpy()

        # Class 0 = non-toxic, Class 1 = toxic
        raw_toxic = float(probs[1]) if len(probs) > 1 else float(probs[0])

        # Compute adjusted scores
        effective_toxic = self._compute_effective_toxic(cleaned, raw_toxic)
        threat_score = self._compute_threat_score(cleaned, raw_toxic)

        # Label based on EFFECTIVE toxic score (which accounts for negation/humour)
        if effective_toxic >= 0.75:
            label = "Cyberbullying Detected"
        elif effective_toxic >= 0.45:
            label = "Possibly Bullying"
        else:
            label = "Safe / Non-bullying"

        return {
            "label": label,
            "confidence": round(raw_toxic, 4),         # raw model confidence
            "toxic_score": round(effective_toxic, 4),   # adjusted for intent
            "threat_score": threat_score,                # keyword-based threat
            "cleaned": cleaned
        }
