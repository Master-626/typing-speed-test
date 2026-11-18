"""
typing-speed-test - Terminal-based typing speed test.
"""

from .tester import SampleSelectionError, TypingTest, select_sample_text

__version__ = "0.1.1"
__all__ = [
    "SampleSelectionError",
    "TypingTest",
    "select_sample_text",
]
