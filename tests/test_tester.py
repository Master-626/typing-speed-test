"""Tests for scoring and sample selection."""

import math

import pytest

from typing_test.tester import (
    SAMPLE_TEXTS,
    SampleSelectionError,
    TypingTest,
    format_sample_preview,
    select_sample_text,
)

NINE_WORDS = "hello world this is a test of typing speed"
TEN_WORDS = "one two three four five six seven eight nine ten"


def test_calculate_wpm_counts_whitespace_separated_words():
    """WPM is words per minute, rounded to one decimal place."""
    test = TypingTest()
    # The string has 9 words, so 30 seconds is 18.0 WPM.
    assert len(NINE_WORDS.split()) == 9
    assert test.calculate_wpm(NINE_WORDS, 30.0) == 18.0
    assert test.calculate_wpm(TEN_WORDS, 30.0) == 20.0
    # Repeated spaces are one separator, not extra words.
    assert test.calculate_wpm("hello   world", 60) == 2.0


def test_calculate_wpm_rejects_non_numeric_duration():
    """Non-numeric durations still raise, rather than being scored as zero."""
    with pytest.raises(TypeError):
        TypingTest().calculate_wpm("hello world", "30")


def test_calculate_wpm_rejects_unusable_durations():
    """Zero, negative, NaN, infinite, and underflowed times score 0."""
    test = TypingTest()
    assert test.calculate_wpm("hello world", 0) == 0.0
    assert test.calculate_wpm("hello world", -3) == 0.0
    assert test.calculate_wpm("hello world", float("nan")) == 0.0
    assert test.calculate_wpm("hello world", float("inf")) == 0.0
    assert test.calculate_wpm("", float("nan")) == 0.0
    assert test.calculate_wpm("   \n\t", 30) == 0.0
    # A tiny positive duration used to come back as inf.
    assert test.calculate_wpm("hello world", 1e-320) == 0.0
    huge = test.calculate_wpm("hello world", 1e-10)
    assert huge > 0
    assert math.isfinite(huge)


def test_calculate_accuracy_exact_matches_and_mismatches():
    """Accuracy is a positional character percentage."""
    test = TypingTest("hello world")
    assert test.calculate_accuracy("hello world", "hello world") == 100.0
    # One substitution in 11 characters: 10/11 -> 90.9.
    assert test.calculate_accuracy("hello w0rld", "hello world") == 90.9
    assert test.calculate_accuracy("hell", "hello") == 80.0
    assert test.calculate_accuracy("hello!!!", "hello") == 62.5
    assert test.calculate_accuracy("", "hello") == 0.0
    assert test.calculate_accuracy("Hello", "hello") == 80.0
    # Punctuation is scored like any other character.
    assert test.calculate_accuracy("a b, c.", "a b, c.") == 100.0
    assert test.calculate_accuracy("a b. c.", "a b, c.") == 85.7


def test_calculate_accuracy_empty_inputs_and_rounding():
    """Empty agreement is perfect, and a single error cannot round to 100."""
    test = TypingTest()
    assert test.calculate_accuracy("", "") == 100.0
    # Falsy non-strings still follow the old "no target" guard.
    assert test.calculate_accuracy("hello", None) == 0.0

    perfect_except_last = "a" * 1999 + "b"
    target = "a" * 2000
    accuracy = test.calculate_accuracy(perfect_except_last, target)
    assert accuracy == 99.9
    assert accuracy != 100.0

    # A short single error stays at its real rounded value.
    assert test.calculate_accuracy("a" * 999 + "b", "a" * 1000) == 99.9


def test_empty_sample_text_is_preserved():
    """An explicit empty passage is not replaced by the default pangram."""
    test = TypingTest("")
    assert test.sample_text == ""
    summary = test.get_result_summary("", 12.0)
    assert summary["accuracy"] == 100.0
    assert summary["correct_chars"] == 0
    assert summary["total_chars"] == 0


def test_default_sample_text():
    """Omitting the passage selects the first built-in sample."""
    assert TypingTest().sample_text == SAMPLE_TEXTS[0]
    assert TypingTest(None).sample_text == SAMPLE_TEXTS[0]
    assert TypingTest("hello").sample_text == "hello"


def test_get_sample_texts_is_a_copy():
    """Callers can mutate the returned list without changing the catalog."""
    test = TypingTest()
    texts = test.get_sample_texts()
    assert texts == SAMPLE_TEXTS
    assert len(texts) >= 3
    texts.append("extra passage")
    assert test.get_sample_texts() == SAMPLE_TEXTS


def test_result_summary_exact_values():
    """The summary reports WPM, accuracy, time, and character counts."""
    test = TypingTest("hello world")
    result = test.get_result_summary("hello world", 30.0)
    assert result == {
        "wpm": 4.0,
        "accuracy": 100.0,
        "time_seconds": 30.0,
        "total_chars": 11,
        "correct_chars": 11,
    }

    partial = TypingTest("hello").get_result_summary("hxllo", 60)
    assert partial["correct_chars"] == 4
    assert partial["total_chars"] == 5
    assert partial["accuracy"] == 80.0
    assert partial["wpm"] == 1.0

    extra = TypingTest("hello").get_result_summary("hello!!", 60)
    assert extra["correct_chars"] == 5
    assert extra["total_chars"] == 7
    assert extra["accuracy"] == 71.4


def test_result_summary_does_not_pair_zero_time_with_a_huge_wpm():
    """Durations that round to 0 seconds are an unscored attempt."""
    test = TypingTest("hello world")
    tiny = test.get_result_summary("hello world", 0.04)
    assert tiny["time_seconds"] == 0.0
    assert tiny["wpm"] == 0.0
    assert tiny["accuracy"] == 100.0

    # The low-level WPM helper still uses the exact positive duration.
    assert test.calculate_wpm("hello world", 0.04) == 3000.0


def test_result_summary_clamps_negative_and_non_finite_time():
    """Negative and non-finite durations are reported as zero, not echoed."""
    test = TypingTest("ab")
    negative = test.get_result_summary("ab", -5)
    assert negative["wpm"] == 0.0
    assert negative["time_seconds"] == 0.0
    assert negative["accuracy"] == 100.0

    for bad in (float("nan"), float("inf"), float("-inf")):
        result = test.get_result_summary("ab", bad)
        assert result["wpm"] == 0.0
        assert result["time_seconds"] == 0.0
        assert math.isfinite(result["accuracy"])


def test_select_sample_text_by_index():
    """Passage numbers are 1-based and follow the samples listing."""
    assert select_sample_text() == SAMPLE_TEXTS[0]
    assert select_sample_text(None) == SAMPLE_TEXTS[0]
    assert select_sample_text(1) == SAMPLE_TEXTS[0]
    assert select_sample_text(len(SAMPLE_TEXTS)) == SAMPLE_TEXTS[-1]


@pytest.mark.parametrize("bad", [0, -1, len(SAMPLE_TEXTS) + 1, True, False, "1", 1.5])
def test_select_sample_text_rejects_bad_indexes(bad):
    with pytest.raises(SampleSelectionError, match="between 1 and"):
        select_sample_text(bad)


def test_select_sample_text_random(monkeypatch):
    """Random selection uses the catalog and can be forced in tests."""
    monkeypatch.setattr(
        "typing_test.tester.random.choice",
        lambda texts: texts[2],
    )
    assert select_sample_text(random_sample=True) == SAMPLE_TEXTS[2]


def test_select_sample_text_rejects_mixed_modes():
    with pytest.raises(SampleSelectionError, match="not both"):
        select_sample_text(1, random_sample=True)


def test_select_sample_text_when_catalog_is_empty(monkeypatch):
    monkeypatch.setattr("typing_test.tester.SAMPLE_TEXTS", [])
    with pytest.raises(SampleSelectionError, match="No sample texts"):
        select_sample_text()
    assert TypingTest().sample_text == ""


def test_format_sample_preview_adds_ellipsis_only_when_shortened():
    assert format_sample_preview("short", 60) == "short"
    assert format_sample_preview("a" * 60, 60) == "a" * 60
    assert format_sample_preview("a" * 61, 60) == ("a" * 60) + "..."
    # Built-in passages are longer than the preview width.
    assert format_sample_preview(SAMPLE_TEXTS[0]) == SAMPLE_TEXTS[0][:60] + "..."
