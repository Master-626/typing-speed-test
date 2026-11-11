"""
Core typing test logic.
"""

import math
import random
from typing import Dict, List, Optional

# Sample texts for typing test
SAMPLE_TEXTS = [
    (
        "The quick brown fox jumps over the lazy dog. "
        "This sentence contains every letter of the alphabet."
    ),
    (
        "Programming is the art of telling another computer what to do. "
        "It requires patience, logic, and creativity."
    ),
    (
        "Technology is best when it brings people together. "
        "Good tools should be invisible and intuitive to use."
    ),
    (
        "The best way to predict the future is to invent it. "
        "Keep learning and never stop improving your skills."
    ),
    (
        "Success is not final, failure is not fatal: "
        "it is the courage to continue that counts. Keep going."
    ),
]


class SampleSelectionError(ValueError):
    """Raised when a built-in passage cannot be selected."""


class TypingTest:
    """Typing speed test calculator."""

    def __init__(self, sample_text: Optional[str] = None):
        # Only None means "use the default". An explicit empty passage is kept.
        if sample_text is None:
            sample_text = SAMPLE_TEXTS[0] if SAMPLE_TEXTS else ""
        self.sample_text = sample_text

    def calculate_wpm(self, typed_text: str, time_seconds: float) -> float:
        """Calculate WPM from whitespace-separated words.

        A word is a maximal run of non-whitespace characters, so punctuation
        stays attached to the token it follows. The duration is the exact
        number of seconds passed in. Non-positive, non-finite, or otherwise
        unusable durations score 0.
        """
        duration = _positive_duration(time_seconds)
        if duration is None:
            return 0.0

        words = len(typed_text.split())
        minutes = duration / 60.0
        if minutes <= 0:
            return 0.0
        wpm = words / minutes
        if not math.isfinite(wpm):
            return 0.0
        return round(wpm, 1)

    def calculate_accuracy(self, typed_text: str, original_text: str) -> float:
        """Calculate positional character accuracy as a percentage.

        Characters are compared from the start of both strings. Extra and
        missing characters count as incorrect. The score is 100 only when
        the strings are identical, including when both are empty. An
        imperfect attempt is never rounded up to 100.
        """
        if original_text == "" and typed_text == "":
            return 100.0
        if not original_text:
            return 0.0

        correct_chars = sum(
            1 for a, b in zip(typed_text, original_text) if a == b
        )
        total_chars = max(len(original_text), len(typed_text))
        if correct_chars == total_chars:
            return 100.0
        rounded = round((correct_chars / total_chars) * 100, 1)
        if rounded >= 100.0:
            return 99.9
        return rounded

    def get_sample_texts(self) -> List[str]:
        """Get all sample texts."""
        return SAMPLE_TEXTS.copy()

    def get_result_summary(self, typed_text: str, time_seconds: float) -> Dict:
        """Get full test result summary.

        ``time_seconds`` in the result is rounded to one decimal place.
        A duration that is non-positive, non-finite, or so small that it
        rounds to 0 is reported as 0 seconds with 0 WPM, so the two fields
        stay consistent.
        """
        duration = _positive_duration(time_seconds)
        if duration is None:
            wpm = 0.0
            reported_time = 0.0
        else:
            reported_time = round(time_seconds, 1)
            if reported_time <= 0:
                wpm = 0.0
                reported_time = 0.0
            else:
                wpm = self.calculate_wpm(typed_text, duration)

        accuracy = self.calculate_accuracy(typed_text, self.sample_text)
        total_chars = len(typed_text)
        correct_chars = sum(
            1 for a, b in zip(typed_text, self.sample_text) if a == b
        )

        return {
            "wpm": wpm,
            "accuracy": accuracy,
            "time_seconds": reported_time,
            "total_chars": total_chars,
            "correct_chars": correct_chars,
        }


def select_sample_text(
    sample: Optional[int] = None,
    *,
    random_sample: bool = False,
) -> str:
    """Return one built-in passage.

    ``sample`` is 1-based and matches the numbers printed by
    ``typing-test samples``. Pass ``random_sample=True`` and leave
    ``sample`` unset to choose uniformly at random.
    """
    if random_sample and sample is not None:
        raise SampleSelectionError("Use either sample or random_sample, not both.")

    texts = SAMPLE_TEXTS
    if not texts:
        raise SampleSelectionError("No sample texts are available.")
    if random_sample:
        return random.choice(texts)
    if sample is None:
        return texts[0]
    if isinstance(sample, bool) or not isinstance(sample, int):
        raise SampleSelectionError(
            f"sample must be an integer between 1 and {len(texts)}"
        )
    if sample < 1 or sample > len(texts):
        raise SampleSelectionError(
            f"sample must be an integer between 1 and {len(texts)}"
        )
    return texts[sample - 1]


def format_sample_preview(text: str, limit: int = 60) -> str:
    """Return ``text``, appending an ellipsis only when it is shortened."""
    if len(text) <= limit:
        return text
    return text[:limit] + "..."


def _positive_duration(time_seconds: float) -> Optional[float]:
    """Return a positive finite duration in seconds, or None if unusable.

    Non-numeric values still raise ``TypeError``, matching the previous
    comparison against zero.
    """
    if not math.isfinite(time_seconds) or time_seconds <= 0:
        return None
    return float(time_seconds)
