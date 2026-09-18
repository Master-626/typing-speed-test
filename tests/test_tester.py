import pytest
from typing_test.tester import TypingTest


def test_calculate_wpm():
    """Test WPM calculation."""
    test = TypingTest()
    # 10 words in 30 seconds = 20 WPM
    wpm = test.calculate_wpm("hello world this is a test of typing speed", 30.0)
    assert wpm > 0


def test_calculate_accuracy():
    """Test accuracy calculation."""
    test = TypingTest("hello world")
    accuracy = test.calculate_accuracy("hello world", "hello world")
    assert accuracy == 100.0

    accuracy_partial = test.calculate_accuracy("hello w0rld", "hello world")
    assert 80 < accuracy_partial < 100


def test_get_sample_texts():
    """Test getting sample texts."""
    test = TypingTest()
    texts = test.get_sample_texts()
    assert len(texts) >= 3


def test_result_summary():
    """Test result summary."""
    test = TypingTest("hello world test")
    result = test.get_result_summary("hello world test", 10.0)
    assert "wpm" in result
    assert "accuracy" in result
    assert "time_seconds" in result
