# Typing Speed Test

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Productivity Tool](https://img.shields.io/badge/productivity-tool-green.svg)]()

Terminal-based typing speed test CLI tool. Test your WPM (words per minute) and accuracy.

## 🌟 Features

- ⚡ **WPM Calculation** - Measure your words per minute
- 🎯 **Accuracy** - Track your typing accuracy percentage
- 📝 **Sample Texts** - Multiple sample texts to practice with
- 🎨 **Rich Output** - Beautiful terminal results display
- 🐍 **Python API** - Use as a library in your code

## 📦 Installation

```bash
git clone https://github.com/Master-626/typing-speed-test.git
cd typing-speed-test
pip install .
```

## 🚀 Usage

### Start Test
```bash
typing-test start
```

### Show Sample Texts
```bash
typing-test samples
```

## 🐍 Python API

```python
from typing_test import TypingTest

test = TypingTest()

# Calculate WPM
wpm = test.calculate_wpm("your typed text here", 30.0)

# Calculate accuracy
accuracy = test.calculate_accuracy("your typed text", "original text")

# Get full results
result = test.get_result_summary("typed text", 30.0)
print(f"WPM: {result['wpm']}, Accuracy: {result['accuracy']}%")
```

## 🧪 Testing

```bash
pip install -e ".[dev]"
pytest
```

## 📄 License

MIT License
