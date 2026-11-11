"""
CLI interface for typing-speed-test.
"""

import time

import click
from rich.console import Console
from rich.panel import Panel

from . import __version__
from . import tester as catalog
from .tester import (
    SampleSelectionError,
    TypingTest,
    format_sample_preview,
    select_sample_text,
)

console = Console()


@click.group()
@click.version_option(__version__, prog_name="typing-test")
def main():
    """Typing Speed Test - Test your typing speed and accuracy."""


@main.command()
@click.option(
    "--sample",
    "-s",
    type=int,
    default=1,
    show_default=True,
    help="1-based sample text to type (see the samples command).",
)
@click.option(
    "--random",
    "random_sample",
    is_flag=True,
    help="Type a randomly chosen sample instead of --sample.",
)
@click.pass_context
def start(ctx: click.Context, sample: int, random_sample: bool) -> None:
    """Start a typing speed test."""
    sample_was_explicit = (
        ctx.get_parameter_source("sample") == click.core.ParameterSource.COMMANDLINE
    )
    if random_sample and sample_was_explicit:
        raise click.UsageError("Use either --sample or --random, not both.")

    try:
        chosen = select_sample_text(
            None if random_sample else sample,
            random_sample=random_sample,
        )
    except SampleSelectionError as exc:
        raise click.UsageError(str(exc)) from exc

    texts = catalog.SAMPLE_TEXTS
    index = texts.index(chosen) + 1
    test = TypingTest(chosen)

    console.print(
        Panel.fit(
            "\n".join(
                [
                    "[bold cyan]Typing Speed Test[/bold cyan]",
                    "",
                    f"Sample {index} of {len(texts)}.",
                    "Type the following text as fast and accurately as you can.",
                    "Press Enter when you're done.",
                ]
            ),
            border_style="blue",
        )
    )
    # markup=False so characters like "[" in the passage are printed literally.
    console.print()
    console.print(test.sample_text, style="yellow", markup=False)
    console.print()

    started = time.perf_counter()
    typed_text = click.prompt("Your typing")
    elapsed = time.perf_counter() - started

    console.print("\n[green]Test complete! Here are your results:[/green]\n")
    result = test.get_result_summary(typed_text, elapsed)
    compared = max(len(typed_text), len(test.sample_text))

    console.print(f"📊 WPM: [bold green]{result['wpm']}[/bold green]")
    console.print(f"🎯 Accuracy: [bold green]{result['accuracy']}%[/bold green]")
    console.print(f"⏱️  Time: {result['time_seconds']}s")
    console.print(f"⌨️  Characters: {result['correct_chars']}/{compared} correct")


@main.command()
def samples() -> None:
    """Show available sample texts."""
    test = TypingTest()
    texts = test.get_sample_texts()

    console.print("\n📝 Available sample texts:\n")
    for i, text in enumerate(texts, 1):
        console.print(f"  {i}. {format_sample_preview(text)}", markup=False)


if __name__ == "__main__":
    main()
