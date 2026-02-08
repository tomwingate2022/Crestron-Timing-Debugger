import re
import sys
import argparse
from pathlib import Path
import pandas as pd
import plotly.graph_objects as go

RE_MS = re.compile(r"^\s*(\d+(?:\.\d+)?)\s*ms\s*$", re.IGNORECASE)
RE_HMS = re.compile(r"^\s*(\d{1,2}):(\d{2}):(\d{2})(?:\.(\d{1,3}))?\s*$")


def parse_time_to_ms(t: str):
    if t is None:
        return None
    s = str(t).strip()
    if not s:
        return None

    # Normalize spacing quirks like "16  ms" or "0ms"
    s = re.sub(r"\s+", " ", s).replace(" ms", "ms")

    m = RE_MS.match(s)
    if m:
        return float(m.group(1))

    m = RE_HMS.match(s)
    if m:
        hh = int(m.group(1))
        mm = int(m.group(2))
        ss = int(m.group(3))
        frac = m.group(4) or "0"
        ms = int(frac.ljust(3, "0")[:3])  # pad/truncate to 3 digits
        return ((hh * 3600) + (mm * 60) + ss) * 1000 + ms

    # fallback: treat as plain number in ms
    try:
        return float(s)
    except ValueError:
        return None


def classify_value(v: str) -> str:
    """Digital if exactly 0/1; Analog if numeric-ish (allows suffix like '720d'); else Serial."""
    s = str(v).strip()
    if s in ("0", "1"):
        return "Digital"

    s2 = re.sub(r"[a-zA-Z]+\s*$", "", s)  # allow analog like "720d"
    try:
        float(s2)
        return "Analog"
    except ValueError:
        return "Serial"


def parse_log(path: Path) -> pd.DataFrame:
    """
    Expected line formats:
      0 ms: signal_name -> value
      00:00:10.031: signal_name -> value

    IMPORTANT: We split on ': ' so HH:MM:SS.xxx is captured correctly.
    """
    rows = []
    for raw in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = raw.strip()
        if not line:
            continue

        # Split time from the rest using the FIRST occurrence of ": "
        # This correctly handles times like 00:00:10.031
        time_part, sep, rest = line.partition(": ")
        if not sep:
            continue  # no delimiter

        sig_part, sep2, val_part = rest.partition(" -> ")
        if not sep2:
            continue  # no arrow delimiter

        t_ms = parse_time_to_ms(time_part)
        if t_ms is None:
            continue

        sig = sig_part.strip()
        val_raw = val_part.strip()

        typ = classify_value(val_raw)

        val_num = None
        if typ in ("Digital", "Analog"):
            s2 = re.sub(r"[a-zA-Z]+\s*$", "", val_raw)
            try:
                val_num = float(s2)
            except ValueError:
                val_num = None

        rows.append((t_ms, sig, typ, val_raw, val_num))

    df = pd.DataFrame(rows, columns=["TimeMs", "Signal", "Type", "ValueRaw", "ValueNum"])
    if df.empty:
        return df
    return df.sort_values(["TimeMs", "Signal"]).reset_index(drop=True)


def build_figure(df: pd.DataFrame, mode: str) -> go.Figure:
    fig = go.Figure()

    # Stable ordering by first occurrence
    sig_order = (
        df.groupby("Signal", sort=False)["TimeMs"]
        .min()
        .sort_values()
        .index
        .tolist()
    )
    lane = {s: i for i, s in enumerate(sig_order)}

    t_min = float(df["TimeMs"].min())
    t_max = float(df["TimeMs"].max())
    t_end = t_max + max(10.0, (t_max - t_min) * 0.02)

    # SERIAL markers
    df_s = df[df["Type"] == "Serial"]
    if not df_s.empty:
        fig.add_trace(go.Scatter(
            x=df_s["TimeMs"],
            y=[lane[s] for s in df_s["Signal"]],
            mode="markers",
            marker=dict(symbol="x", size=7),
            name="Serial",
            customdata=df_s[["Signal", "ValueRaw"]].to_numpy(),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Type: Serial<br>"
                "Value: %{customdata[1]}<br>"
                "Time: %{x:.3f} ms<extra></extra>"
            ),
            showlegend=True
        ))

    # ANALOG markers
    df_a = df[df["Type"] == "Analog"]
    if not df_a.empty:
        fig.add_trace(go.Scatter(
            x=df_a["TimeMs"],
            y=[lane[s] for s in df_a["Signal"]],
            mode="markers",
            marker=dict(size=6),
            name="Analog",
            customdata=df_a[["Signal", "ValueRaw"]].to_numpy(),
            hovertemplate=(
                "<b>%{customdata[0]}</b><br>"
                "Type: Analog<br>"
                "Value: %{customdata[1]}<br>"
                "Time: %{x:.3f} ms<extra></extra>"
            ),
            showlegend=True
        ))

    # DIGITAL
    df_d = df[df["Type"] == "Digital"].copy()
    if not df_d.empty:
        if mode == "edges":
            for sig, g in df_d.groupby("Signal", sort=False):
                g = g.sort_values("TimeMs")
                vals = g["ValueNum"].fillna(0).astype(int)
                prev = vals.shift(1)
                is_edge = prev.isna() | (vals != prev)
                e = g[is_edge].copy()
                if e.empty:
                    continue

                base = lane[sig]
                prev2 = prev[is_edge].fillna(vals.iloc[0]).astype(int).to_list()
                cur2 = vals[is_edge].astype(int).to_list()

                sym = []
                for p, c in zip(prev2, cur2):
                    if c > p:
                        sym.append("triangle-up")
                    elif c < p:
                        sym.append("triangle-down")
                    else:
                        sym.append("circle")

                fig.add_trace(go.Scatter(
                    x=e["TimeMs"],
                    y=[base] * len(e),
                    mode="markers",
                    marker=dict(size=9, symbol=sym),
                    name=f"{sig} (edges)",
                    customdata=[[sig, int(v)] for v in cur2],
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Type: Digital (edge)<br>"
                        "Value: %{customdata[1]}<br>"
                        "Time: %{x:.3f} ms<extra></extra>"
                    ),
                    showlegend=False
                ))
        else:
            for sig, g in df_d.groupby("Signal", sort=False):
                g = g.sort_values("TimeMs")
                base = lane[sig]
                x = g["TimeMs"].tolist()
                v = g["ValueNum"].fillna(0).astype(int).tolist()

                x2 = x + [t_end]
                v2 = v + [v[-1]]
                y2 = [base + (0.25 if vv == 1 else -0.25) for vv in v2]

                fig.add_trace(go.Scatter(
                    x=x2,
                    y=y2,
                    mode="lines",
                    line_shape="hv",
                    name=sig,
                    customdata=[[sig, vv] for vv in v2],
                    hovertemplate=(
                        "<b>%{customdata[0]}</b><br>"
                        "Type: Digital (step)<br>"
                        "Value: %{customdata[1]}<br>"
                        "Time: %{x:.3f} ms<extra></extra>"
                    ),
                    showlegend=False
                ))

    fig.update_yaxes(
        tickmode="array",
        tickvals=list(range(len(sig_order))),
        ticktext=sig_order,
        autorange="reversed",
        title="Signal",
        automargin=True
    )

    fig.update_xaxes(
        title="Time (ms)",
        showspikes=True,
        spikemode="across",
        spikesnap="cursor",
        showline=True
    )

    # More spacing between signal names
    fig.update_layout(
        title=f"Signal Timeline — mode={mode} — {len(sig_order)} signals, {len(df)} events",
        hovermode="closest",
        height=max(800, 28 * len(sig_order)),
        margin=dict(l=360, r=40, t=60, b=50),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0)
    )

    return fig


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("logfile")
    ap.add_argument("--out", default=None)
    ap.add_argument("--tmin", type=float, default=None, help="min time in ms")
    ap.add_argument("--tmax", type=float, default=None, help="max time in ms")
    ap.add_argument("--only", default=None, help="regex filter for Signal name")
    ap.add_argument("--exclude", default=None, help="regex exclude filter for Signal name")
    ap.add_argument("--max-signals", type=int, default=60, help="cap number of signals (after filtering)")
    ap.add_argument("--mode", choices=["edges", "steps"], default="edges", help="digital rendering mode")
    ap.add_argument("--absolute-time", action="store_true", help="Keep absolute time (do not normalize).")
    args = ap.parse_args()

    in_path = Path(args.logfile)
    out_path = Path(args.out) if args.out else in_path.with_suffix(f".{args.mode}.html")

    df = parse_log(in_path)
    if df.empty:
        print("No parseable rows found.")
        sys.exit(2)

    # Signal filters
    if args.only:
        df = df[df["Signal"].str.contains(args.only, regex=True, na=False)]
    if args.exclude:
        df = df[~df["Signal"].str.contains(args.exclude, regex=True, na=False)]

    # Time filters (ms)
    if args.tmin is not None:
        df = df[df["TimeMs"] >= args.tmin]
    if args.tmax is not None:
        df = df[df["TimeMs"] <= args.tmax]

    if df.empty:
        print("No events after filtering. Try widening --tmin/--tmax or removing filters.")
        sys.exit(3)

    # Cap signals
    sig_order = (
        df.groupby("Signal", sort=False)["TimeMs"]
        .min()
        .sort_values()
        .index
        .tolist()
    )
    if len(sig_order) > args.max_signals:
        keep = set(sig_order[:args.max_signals])
        df = df[df["Signal"].isin(keep)]

    # Default behavior: normalize to window start if user used a time filter
    if not args.absolute_time and (args.tmin is not None or args.tmax is not None):
        t0 = float(df["TimeMs"].min())
        df["TimeMs"] = df["TimeMs"] - t0

    fig = build_figure(df, mode=args.mode)
    fig.write_html(out_path.as_posix(), include_plotlyjs="cdn")
    print(f"Wrote: {out_path}")


if __name__ == "__main__":
    main()