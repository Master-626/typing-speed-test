"""CLI tests for timing, passage selection, and result display."""

from click.testing import CliRunner

from typing_test import __version__
from typing_test.cli import main
from typing_test.tester import SAMPLE_TEXTS


def _invoke(args, input_text=None, monkeypatch=None, clock=None):
    if clock is not None:
        monkeypatch.setattr("typing_test.cli.time.perf_counter", clock)
    result = CliRunner().invoke(main, args, input=input_text)
    return result


def test_version_option():
    result = _invoke(["--version"])
    assert result.exit_code == 0, result.output
    assert __version__ in result.output
    assert "typing-test" in result.output


def test_start_help_lists_sample_options():
    result = _invoke(["start", "--help"])
    assert result.exit_code == 0, result.output
    assert "--sample" in result.output
    assert "--random" in result.output


def test_samples_command_truncates_long_passages_only():
    result = _invoke(["samples"])
    assert result.exit_code == 0, result.output
    assert "1." in result.output
    assert f"{len(SAMPLE_TEXTS)}." in result.output
    assert SAMPLE_TEXTS[0][:60] + "..." in result.output
    # The full passage is longer than the preview, so it is not printed whole.
    assert SAMPLE_TEXTS[0] not in result.output


def test_samples_keep_short_text_and_brackets(monkeypatch):
    passage = "use list[int] today"
    monkeypatch.setattr("typing_test.tester.SAMPLE_TEXTS", [passage])
    result = _invoke(["samples"])
    assert result.exit_code == 0, result.output
    assert "list[int]" in result.output
    assert "..." not in result.output


def test_start_prints_brackets_in_the_passage(monkeypatch):
    passage = "use list[int] today"
    monkeypatch.setattr("typing_test.tester.SAMPLE_TEXTS", [passage])
    result = _invoke(["start"], input_text="use\n")
    assert result.exit_code == 0, result.output
    assert "list[int]" in result.output
    assert "Sample 1 of 1." in result.output


def test_start_uses_selected_sample():
    result = _invoke(["start", "--sample", "2"], input_text="Programming\n")
    assert result.exit_code == 0, result.output
    assert "Sample 2 of 5." in result.output
    # Rich may wrap the passage, so match a prefix that stays on one line.
    assert "Programming is the art of telling another" in result.output
    assert "quick brown fox" not in result.output


def test_start_rejects_an_unknown_sample():
    for bad in ("0", "9", "-1"):
        result = _invoke(["start", "--sample", bad])
        assert result.exit_code != 0, bad
        assert "between 1 and" in result.output


def test_start_rejects_sample_and_random_together():
    result = _invoke(["start", "--sample", "2", "--random"])
    assert result.exit_code != 0
    assert "not both" in result.output


def test_start_random_sample(monkeypatch):
    monkeypatch.setattr(
        "typing_test.tester.random.choice",
        lambda texts: texts[3],
    )
    result = _invoke(["start", "--random"], input_text="Success\n")
    assert result.exit_code == 0, result.output
    assert "Sample 4 of 5." in result.output
    assert "The best way to predict the future" in result.output
    assert "quick brown fox" not in result.output


def test_start_measures_elapsed_time(monkeypatch):
    """The score uses the time spent at the prompt, not a fixed 30 seconds."""
    ticks = iter([1000.0, 1015.5])

    def clock():
        return next(ticks)

    result = _invoke(
        ["start", "--sample", "1"],
        input_text="one two three four five\n",
        monkeypatch=monkeypatch,
        clock=clock,
    )
    assert result.exit_code == 0, f"{result.output}\n{result.exception!r}"
    # 5 words in 15.5 seconds is 19.4 WPM. A hardcoded 30s run would be 10.0.
    assert "19.4" in result.output
    assert "15.5s" in result.output
    assert "10.0" not in result.output


def test_start_character_line_counts_extra_typed_characters(monkeypatch):
    """Extra characters widen the denominator instead of looking fully correct."""
    monkeypatch.setattr("typing_test.tester.SAMPLE_TEXTS", ["hi"])
    result = _invoke(["start", "--sample", "1"], input_text="hi!!!!\n")
    assert result.exit_code == 0, result.output
    assert "2/6 correct" in result.output
    assert "2/2 correct" not in result.output
    assert "33.3%" in result.output


def test_default_group_help():
    result = _invoke(["--help"])
    assert result.exit_code == 0, result.output
    assert "start" in result.output
    assert "samples" in result.output
