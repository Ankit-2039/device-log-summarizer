# Device Log Summarizer

CLI tool that reads a device telemetry CSV, aggregates per device, removes
devices with an average temperature above 80.0, exports JSON, prints a summary
table, and plots a bar chart.

> **Note:** `data/device_telemetry.csv` is synthetic sample data created for
> local testing. It was not supplied with the assessment. To use the real
> dataset, replace the file or pass `--input path/to/file.csv`.

## Setup

```bash
python -m venv venv
venv\Scripts\Activate.ps1        # Windows PowerShell
# source venv/bin/activate       # macOS/Linux
pip install -r requirements.txt
```

## Run

```bash
python tests/test_sanitization.py
python src/device_log_summarizer.py
python src/plot_chart.py
```

Custom paths:

```bash
python src/device_log_summarizer.py --input data/device_telemetry.csv --output output/device_summary.json
python src/plot_chart.py --input output/device_summary.json --output output/device_temperature_chart.png
```

## Output

- `output/device_summary.json`: per-device record count, average temperature, ERROR count
- `output/device_temperature_chart.png`: bar chart of average temperature per device

## Error handling

- Missing input file: prints an error and exits with code 1
- Missing columns or empty CSV: prints an error and exits with code 1
- Malformed rows (non-numeric temperature, blank device_id): skipped, with a warning showing the count

## Section 1

`clean_sensor_readings` in `src/device_log_summarizer.py`, tested in
`tests/test_sanitization.py`.