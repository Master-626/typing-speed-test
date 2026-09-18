"""
Core typing test logic.
"""

import time
from typing import Dict, List


# Sample texts for typing test
SAMPLE_TEXTS = [
    "The quick brown fox jumps over the lazy dog. This sentence contains every letter of the alphabet.",
    "Programming is the art of telling another computer what to do. It requires patience, logic, and creativity.",
    "Technology is best when it brings people together. Good tools should be invisible and intuitive to use.",
    "The best way to predict the future is to invent it. Keep learning and never stop improving your skills.",
    "Success is not final, failure is not fatal: it is the courage to continue that counts. Keep going.",
]


class TypingTest:
    """Typing speed test calculator."""

    def __init__(self, sample_text: str = None):
        self.sample_text = sample_text or SAMPLE_TEXTS[0]

    def calculate_wpm(self, typed_text: str, time_seconds: float) -> float:
        """Calculate WPM (words per minute)."""
        if time_seconds <= 0:
            return 0.0

        words = len(typed_text.split())
        minutes = time_seconds / 60
        return round(words / minutes, 1)

    def calculate_accuracy(self, typed_text: str, original_text: str) -> float:
        """Calculate typing accuracy percentage."""
        if not original_text:
            return 0.0

        correct_chars = sum(1 for a, b in zip(typed_text, original_text) if a == b)
        total_chars = max(len(original_text), len(typed_text))
        return round((correct_chars / total_chars) * 100, 1)

    def get_sample_texts(self) -> List[str]:
        """Get all sample texts."""
        return SAMPLE_TEXTS.copy()

    def get_result_summary(self, typed_text: str, time_seconds: float) -> Dict:
        """Get full test result summary."""
        wpm = self.calculate_wpm(typed_text, time_seconds)
        accuracy = self.calculate_accuracy(typed_text, self.sample_text)
        total_chars = len(typed_text)
        correct_chars = sum(1 for a, b in zip(typed_text, self.sample_text) if a == b)

        return {
            "wpm": wpm,
            "accuracy": accuracy,
            "time_seconds": round(time_seconds, 1),
            "total_chars": total_chars,
            "correct_chars": correct_chars,
        }
