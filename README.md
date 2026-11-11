# Typing Speed Test

## 简介

终端里的英文打字测速工具。程序给出一段内置范文，按你的输入计算每分钟词数（WPM，以空格分词）和逐字符准确率。

- 安装：`python -m pip install -e ".[dev]"`
- 开始：`typing-test start`；`--sample 2` 或 `--random` 用来选题
- 查看范文：`typing-test samples`
- 检查：`python -m ruff check .`，测试：`python -m pytest`

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![CI](https://github.com/Master-626/typing-speed-test/actions/workflows/ci.yml/badge.svg)](https://github.com/Master-626/typing-speed-test/actions/workflows/ci.yml)

Terminal typing-speed test. Practice a built-in English passage, then see your words per minute and character accuracy.

## Features

- **WPM** from the words you typed and the time you took
- **Accuracy** from a character-by-character comparison with the passage
- **Five sample passages**, selectable by number or at random
- **Two console commands:** `typing-test` and `typingspeed`
- **A small Python API** for the same scoring rules

## Installation

Python 3.8 or newer.

```bash
git clone https://github.com/Master-626/typing-speed-test.git
cd typing-speed-test
python -m pip install .
```

To work on the project, install the test and lint tools as well:

```bash
python -m pip install -e ".[dev]"
```

## Usage

Show the commands:

```bash
typing-test --help
typing-test --version
```

List the passages. Each line is numbered. Passages longer than 60 characters are shortened with `...`.

```bash
typing-test samples
```

Start a test. The first passage is used unless you pick another one. The clock starts when the `Your typing` prompt appears and stops when you press Enter.

```bash
typing-test start
typing-test start --sample 2
typing-test start --random
typingspeed start --sample 5
```

### Options

| Command | Option | Meaning |
| --- | --- | --- |
| `start` | `-s`, `--sample N` | Type passage `N`. `N` starts at 1 and matches `samples`. Default: `1`. |
| `start` | `--random` | Type a passage chosen at random. Do not combine it with `--sample`. |
| (global) | `--version` | Print the version. |
| (global) | `--help` | Print help. |

Passing `--sample` outside the catalog, or passing `--sample` together with `--random`, exits with an error.

## Python API

```python
from typing_test import TypingTest, select_sample_text

passage = select_sample_text(2)  # 1-based, same numbers as the CLI
test = TypingTest(passage)

typed = "Programming is the art"
elapsed_seconds = 12.5

wpm = test.calculate_wpm(typed, elapsed_seconds)
accuracy = test.calculate_accuracy(typed, passage)
summary = test.get_result_summary(typed, elapsed_seconds)
print(summary["wpm"], summary["accuracy"])
```

`get_result_summary` compares `typed` with the passage stored on that `TypingTest` instance. `calculate_accuracy` takes the target text itself, so the two calls above agree only when that target is `test.sample_text`.

`select_sample_text(random_sample=True)` returns a random built-in passage. Invalid numbers raise `SampleSelectionError`.

## How scoring works

**WPM.** Count whitespace-separated words in the text you typed, divide by the duration in minutes, and round to one decimal place. `"hello   world"` is two words. Punctuation stays on the word it is attached to. This is the ordinary word count, not the "5 characters = 1 word" convention used by some typing sites.

A duration that is zero, negative, or non-finite (`NaN`, infinity) scores `0.0` WPM. A duration so small that the result is not a finite number also scores `0.0`.

**Accuracy.** Walk both strings from the first character. Each matching position counts as correct. The denominator is the longer of the two lengths, so missing characters and extra characters both lower the score. Comparison is case-sensitive and includes spaces and punctuation. `100.0` is returned only when the strings are identical, including when both are empty. A near-perfect attempt is not rounded up to 100.

**Summary.** `get_result_summary` returns:

| Key | Meaning |
| --- | --- |
| `wpm` | Words per minute, from the exact duration |
| `accuracy` | Accuracy against `sample_text` |
| `time_seconds` | Duration rounded to one decimal place |
| `total_chars` | Characters you typed |
| `correct_chars` | Positions that matched the passage |

If the rounded time is `0.0` because the attempt was shorter than 0.05 seconds, both `time_seconds` and `wpm` are `0.0`. The CLI character line uses the longer of the typed text and the passage as its denominator, so extra characters are visible in that count.

## Running tests

```bash
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest
```

GitHub Actions runs the same lint and test steps on Python 3.8 through 3.13.

## License

MIT License. See [LICENSE](LICENSE).
