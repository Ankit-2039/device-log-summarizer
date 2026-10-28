# PROMPT_LOG

## Initial prompt
"Ask an Claude to write a Python script that loads device_summary.json
and generates a bar chart comparing the average temperature per device using matplotlib.
"

## Issue in the first version
The chart had no title, no axis labels, no value labels, and no limit
reference line.

## Follow-up prompt
"Add a title, axis labels with units (°C), value labels on each bar, a dashed
line at the 80.0 limit, and call tight_layout()."

## Result
Claude's second version added a title, axis labels with °C, value labels on
each bar, a red dashed limit line read from the JSON, rotated x-axis labels,
extra y-axis headroom so the DEV_E label isn't cut off, and `tight_layout()`.
I ran it and checked the chart: <"all labels fit,
the dashed line sits at 80 level with DEV_E's bar">.