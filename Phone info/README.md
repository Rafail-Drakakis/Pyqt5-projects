# Phone Info

A PyQt5 GUI that analyses phone numbers using the [`phonenumbers`](https://github.com/daviddrysdale/python-phonenumbers) library. It can process a single number or an entire file of numbers and save the results to a text file.

## Highlights

- Two tabs: one for a single lookup and one for bulk processing
- Results include carrier, country, timezone and type information
- Processing happens in a background thread so the interface stays responsive
- Progress bar and status messages

## Usage

```
python phone_info_gui.py
```

Enter a number with country code (e.g. `+1234567890`) or select a file containing numbers (one per line). Choose an output file and start the analysis.
