# Calculator

A desktop calculator built with PyQt5. It supports standard operations and an optional scientific panel with functions like sine, cosine, tangent, logarithms and square root.

## Features

- Numeric keypad with operators and parentheses
- Toggleable scientific buttons (`sin`, `cos`, `tan`, `log`, `ln`, `sqrt`, `^`)
- Basic editing (`C` to clear, `⌫` backspace)

## Usage

Run the application from this folder:

```bash
python calculator.py
```

Check the *Scientific* box to reveal advanced functions. Results are evaluated using Python's `math` module with a restricted `eval`.
