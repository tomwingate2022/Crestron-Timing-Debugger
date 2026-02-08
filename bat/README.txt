BAT Template Pack for plot_crestron_debug_steps.py

How to use
1) Copy these .bat files into the same folder as plot_crestron_debug_steps.py
2) Drag-and-drop a debug log .txt onto any .bat file, OR run from cmd:
     00_overview_edges.bat "C:\path\to\log.txt"

Files
- 00_overview_edges.bat
  Overview, fast: --mode edges --max-signals 40

- 01_time_window_edges.bat
  Edit TMIN/TMAX at top, then run: --tmin --tmax --mode edges --max-signals 30

- 02_button_to_feedback_edges.bat
  Filter: --only "_btn$|_fb$" --mode edges

- 03_ui_page_changes_edges.bat
  Filter: --only "page_name\$|Popup" --mode edges

- 04_deep_dive_steps.bat
  Edit TMIN/TMAX at top, then run: --mode steps --max-signals 25

- 05_custom_out_edges.bat
  Example of using --out

Note
- These templates match the cheat sheet options exactly.
- If you prefer a specific Python (e.g., 3.12), change "py" to:
    py -3.12
  in each .bat.
