"""Bar chart of average temperature per device, from the JSON summary."""

import argparse
import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # save to file without needing a display
import matplotlib.pyplot as plt

DEFAULT_LIMIT = 80.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="output/device_summary.json")
    parser.add_argument("--output", default="output/device_temperature_chart.png")
    args = parser.parse_args()

    try:
        with open(args.input, encoding="utf-8") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError) as error:
        print(f"Error loading {args.input}: {error}", file=sys.stderr)
        return 1

    devices = data.get("devices", [])
    if not devices:
        print("No devices in JSON, nothing to plot.", file=sys.stderr)
        return 1

    limit = data.get("temperature_limit", DEFAULT_LIMIT)
    names = [d["device_id"] for d in devices]
    averages = [d["average_temperature"] for d in devices]

    fig, ax = plt.subplots(figsize=(8, 5))
    bars = ax.bar(names, averages, color="steelblue")

    ax.bar_label(bars, fmt="%.2f", padding=3)  # value on each bar
    ax.axhline(limit, color="red", linestyle="--", label=f"Limit ({limit} °C)")

    ax.set_title("Average Temperature per Device")
    ax.set_xlabel("Device ID")
    ax.set_ylabel("Average Temperature (°C)")
    ax.set_ylim(0, max(max(averages), limit) * 1.15)  # room for labels
    ax.legend()
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

    fig.tight_layout()

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=150)
    plt.close(fig)
    print(f"Chart saved to {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())