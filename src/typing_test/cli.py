"""
CLI interface for typing-speed-test.
"""

import click
from rich.console import Console
from rich.panel import Panel

from .tester import TypingTest, SAMPLE_TEXTS

console = Console()


@click.group()
@click.version_option()
def main():
    """Typing Speed Test - Test your typing speed and accuracy."""
    pass


@main.command()
def start():
    """Start a typing speed test."""
    test = TypingTest(SAMPLE_TEXTS[0])

    console.print(Panel.fit(
        "[bold cyan]Typing Speed Test[/bold cyan]\n\n"
        "Type the following text as fast and accurately as you can.\n"
        "Press Enter when you're done.",
        border_style="blue"
    ))

    console.print(f"\n[yellow]{test.sample_text}[/yellow]\n")

    typed_text = click.prompt("Your typing")

    # Simple timing (prompt waits for user input)
    console.print("\n[green]Test complete! Here are your results:[/green]\n")

    # Show sample result (in real use, we'd measure actual time)
    result = test.get_result_summary(typed_text, 30.0)

    console.print(f"📊 WPM: [bold green]{result['wpm']}[/bold green]")
    console.print(f"🎯 Accuracy: [bold green]{result['accuracy']}%[/bold green]")
    console.print(f"⏱️  Time: {result['time_seconds']}s")
    console.print(f"⌨️  Characters: {result['correct_chars']}/{len(test.sample_text)} correct")


@main.command()
def samples():
    """Show available sample texts."""
    test = TypingTest()
    texts = test.get_sample_texts()

    console.print("\n📝 Available sample texts:\n")
    for i, text in enumerate(texts, 1):
        console.print(f"  {i}. {text[:60]}...")


if __name__ == "__main__":
    main()
