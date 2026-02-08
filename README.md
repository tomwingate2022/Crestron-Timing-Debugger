# Timing Debug Plotter (Plotly)

A lightweight Python tool to visualize Crestron-style (or similar) debugger logs as an interactive timing timeline so you can spot ordering issues, race conditions, and digital pulse/glitch behavior.

The tool parses raw debug logs and generates an interactive HTML timeline using Plotly.

It supports three signal types:
- Digital: 0 / 1 (rendered as edges or step traces)
- Serial: text values (rendered as event markers)
- Analog: numeric values (rendered as event markers)

---

## Input Log Format

Each log line must follow this format:

<time>: <signal_name> -> <value>

Examples:

0 ms: tp1_main_favorites_btn -> 1
15 ms: tp1_favorite_popup -> 1
00:00:10.031: tp1_clear_annotation_btn -> 0
00:00:02.031: tp1_page_name$ -> COURTROOM A1026 - FAVORITE

### Supported time formats
- 123 ms
- 0ms
- 00:00:02.031 (HH:MM:SS.mmm)

---

## Dependencies

- Python 3.10+ recommended (Python 3.12 works very well on Windows)
- Python packages:
  - plotly
  - pandas

Install dependencies:

pip install plotly pandas

If pip is broken on Windows:

python -m pip install plotly pandas

Or using the Python launcher:

py -3.12 -m pip install plotly pandas

---

## Installation

### Option A – Clone the repository

git clone https://github.com/<YOUR_USERNAME>/timing-debug-plotter.git
cd timing-debug-plotter
pip install plotly pandas

### Option B – Download ZIP

1. Click Code → Download ZIP
2. Extract the files
3. Install dependencies:

pip install plotly pandas

---

## Basic Usage

py plot_crestron_debug_steps.py "your_log.txt"

This generates:

your_log.edges.html

Open the HTML file in Chrome or Edge.

---

## Digital Rendering Modes

### Edges mode (default, fastest)

Best for ordering and race detection.

py plot_crestron_debug_steps.py "your_log.txt" --mode edges

### Steps mode (detailed)

Shows true digital high/low duration and glitches.

py plot_crestron_debug_steps.py "your_log.txt" --mode steps

---

## Time Window Filtering (milliseconds)

py plot_crestron_debug_steps.py "your_log.txt" --tmin 10031 --tmax 21000 --mode edges

### Time axis behavior

- When --tmin or --tmax is used, time is normalized to start at 0 ms (recommended).
- This makes relative timing easier to see.

To keep absolute timestamps from the log:

py plot_crestron_debug_steps.py "your_log.txt" --tmin 10031 --tmax 21000 --mode edges --absolute-time

---

## Signal Filtering (Regex)

### Include only matching signals

py plot_crestron_debug_steps.py "your_log.txt" --only "_btn$|_fb$" --mode edges

### Exclude noisy signals

py plot_crestron_debug_steps.py "your_log.txt" --exclude "_formatted_" --mode edges

---

## Performance Controls

Limit the number of plotted signals (recommended for large logs):

py plot_crestron_debug_steps.py "your_log.txt" --max-signals 40 --mode edges

---

## Output File Name

py plot_crestron_debug_steps.py "your_log.txt" --out my_timing_view.html --mode edges

---

## Windows BAT Templates

This repository includes ready-to-use .bat helper files in the bat/ folder.

Usage:
- Place the .bat files in the same folder as plot_crestron_debug_steps.py
- Drag-and-drop a log file onto a .bat, or run:

bat\00_overview_edges.bat "C:\path\to\your_log.txt"

---

## Interpreting the Charts

### Edges mode
- Shows only transitions
- Ideal for ordering and race conditions
- Very fast, scales well to large captures

### Steps mode
- Shows signal state duration
- Ideal for pulse width, glitches, and latch behavior
- Use after filtering to a smaller signal set

---

## Troubleshooting

### Browser says “Page isn’t responding”

Use edges mode and limit signals:

py plot_crestron_debug_steps.py "your_log.txt" --mode edges --max-signals 40

---

### “No events after filtering”

Your time window likely excludes all data. Try:
- widening --tmin / --tmax
- removing filters
- running without a time window first

py plot_crestron_debug_steps.py "your_log.txt" --mode edges

---

### pip is broken on Windows

python -m pip install --upgrade pip
python -m pip install plotly pandas

Or:

py -3.12 -m pip install plotly pandas

---

## License

Choose a license for your repo (MIT recommended) and include it as LICENSE.

---

## Contributing

Pull requests are welcome.

Good future enhancements:
- automatic btn → fb latency measurement
- CSV export of timing deltas
- signal grouping by prefix
- threshold-based timing warnings