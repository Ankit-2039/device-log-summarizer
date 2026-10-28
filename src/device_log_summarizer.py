"""Device Log Summarizer CLI.

Reads a device telemetry CSV, aggregates per device, filters out hot devices,
writes JSON, and prints a summary table.
"""

import argparse
import csv
import json
import math
import sys
from pathlib import Path

MAX_READING = 500.0
TEMPERATURE_LIMIT = 80.0


# ---------- Section 1: sanitization ----------
def clean_sensor_readings(readings):
    """Return a list of valid floats from mixed input.

    Drops None, unconvertible values, NaN/inf, and negatives.
    Caps values above 500.0 at 500.0. Never raises on bad input.
    """
    cleaned = []
    if not readings:  # None or empty list
        return cleaned

    for item in readings:
        try:
            value = float(item)
        except (ValueError, TypeError):
            continue  # "abc", None, objects, etc.

        if math.isnan(value) or math.isinf(value):
            continue  # NaN would slip past the < 0 check
        if value < 0:
            continue

        cleaned.append(min(value, MAX_READING))
    return cleaned


# ---------- Section 2: CSV processing ----------
def read_records(csv_path):
    """Read the CSV and return (valid_records, skipped_count).

    Each record is (device_id, status, temperature).
    Bad rows are skipped and counted instead of crashing the program.
    """
    records = []
    skipped = 0
    required = {"device_id", "status", "temperature"}

    with open(csv_path, newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty.")

        headers = {name.strip() for name in reader.fieldnames}
        missing = required - headers
        if missing:
            raise ValueError(f"CSV is missing columns: {sorted(missing)}")

        for row in reader:
            row = {(k or "").strip(): (v or "").strip() for k, v in row.items()}
            device_id = row["device_id"]
            status = row["status"].upper()

            try:
                temperature = float(row["temperature"])
            except ValueError:
                skipped += 1
                continue

            if not device_id or math.isnan(temperature) or math.isinf(temperature):
                skipped += 1
                continue

            records.append((device_id, status, temperature))

    return records, skipped


def aggregate_by_device(records):
    """Group records by device_id and compute count, mean temp, ERROR count."""
    totals = {}
    for device_id, status, temperature in records:
        entry = totals.setdefault(
            device_id, {"count": 0, "temp_sum": 0.0, "error_count": 0}
        )
        entry["count"] += 1
        entry["temp_sum"] += temperature
        if status == "ERROR":
            entry["error_count"] += 1

    results = []
    for device_id in sorted(totals):
        entry = totals[device_id]
        results.append(
            {
                "device_id": device_id,
                "total_records": entry["count"],
                "average_temperature": entry["temp_sum"] / entry["count"],
                "error_count": entry["error_count"],
            }
        )
    return results


def filter_devices(summaries, limit=TEMPERATURE_LIMIT):
    """Keep devices whose average temperature is NOT above the limit."""
    return [d for d in summaries if d["average_temperature"] <= limit]


def export_json(summaries, output_path, limit=TEMPERATURE_LIMIT):
    """Write results to JSON (averages rounded to 2 decimals for display)."""
    rounded = [
        {**d, "average_temperature": round(d["average_temperature"], 2)}
        for d in summaries
    ]
    payload = {"temperature_limit": limit, "devices": rounded}

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(payload, file, indent=2)


def print_table(summaries):
    """Print a simple summary table to the terminal."""
    if not summaries:
        print("No devices to display.")
        return
    header = f"{'Device':<12}{'Records':>9}{'Avg Temp':>11}{'Errors':>9}"
    print(header)
    print("-" * len(header))
    for d in summaries:
        print(
            f"{d['device_id']:<12}{d['total_records']:>9}"
            f"{d['average_temperature']:>11.2f}{d['error_count']:>9}"
        )


def parse_args():
    parser = argparse.ArgumentParser(description="Summarize device telemetry CSV.")
    parser.add_argument("--input", default="data/device_telemetry.csv")
    parser.add_argument("--output", default="output/device_summary.json")
    return parser.parse_args()


def main():
    args = parse_args()

    try:
        records, skipped = read_records(args.input)
    except FileNotFoundError:
        print(f"Error: input file not found: {args.input}", file=sys.stderr)
        return 1
    except (ValueError, OSError, csv.Error) as error:
        print(f"Error reading CSV: {error}", file=sys.stderr)
        return 1

    if skipped:
        print(f"Warning: skipped {skipped} malformed row(s).", file=sys.stderr)
    if not records:
        print("Error: no valid records found in the CSV.", file=sys.stderr)
        return 1

    summaries = aggregate_by_device(records)
    kept = filter_devices(summaries)
    removed = len(summaries) - len(kept)

    export_json(kept, args.output)
    print_table(kept)
    print(f"\n{removed} device(s) removed (average temperature above {TEMPERATURE_LIMIT}).")
    print(f"Results saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())