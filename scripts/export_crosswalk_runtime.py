"""Generate the lightweight app dataset from the canonical crosswalk workbook.

Run from the repository root after changing ``crosswalk.xlsx``::

    python scripts/export_crosswalk_runtime.py

Use ``--check`` in validation or CI to fail if the committed CSV is stale.
"""

from __future__ import annotations

import argparse
import io
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SOURCE = PROJECT_ROOT / "mnp_compass" / "data" / "crosswalk.xlsx"
OUTPUT = PROJECT_ROOT / "mnp_compass" / "data" / "crosswalk.csv"
SHEET = "Crosswalk Table"
HEADER_ROW = 1
REQUIRED_COLUMNS = {
    "Short Citation",
    "Priority Tier",
    "Primary Domain",
    "Document Type",
    "Matrix Tags",
}


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Match the app's normalized, single-line column names."""
    result = df.copy()
    result.columns = [" ".join(str(column).strip().split()) for column in result.columns]
    return result


def load_source() -> pd.DataFrame:
    """Read and validate the app table from the canonical workbook."""
    df = normalize_columns(pd.read_excel(SOURCE, sheet_name=SHEET, header=HEADER_ROW))
    missing = REQUIRED_COLUMNS.difference(df.columns)
    if missing:
        names = ", ".join(sorted(missing))
        raise ValueError(f"Source workbook is missing required columns: {names}")

    # Formatting below the table can create entirely blank spreadsheet rows.
    df = df.dropna(how="all").reset_index(drop=True)
    # Excel cells occasionally contain invisible trailing spaces. They are not
    # meaningful app data and would make the generated text artifact unstable.
    return df.map(lambda value: value.rstrip() if isinstance(value, str) else value)


def render_csv(df: pd.DataFrame) -> str:
    """Return a deterministic UTF-8 CSV representation."""
    buffer = io.StringIO(newline="")
    df.to_csv(buffer, index=False, lineterminator="\n")
    return buffer.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="verify that crosswalk.csv matches crosswalk.xlsx without writing",
    )
    args = parser.parse_args()

    source = load_source()
    expected = render_csv(source)
    if args.check:
        actual = OUTPUT.read_text(encoding="utf-8") if OUTPUT.exists() else None
        if actual != expected:
            print(
                "Runtime crosswalk is missing or stale. Run "
                "`python scripts/export_crosswalk_runtime.py`."
            )
            return 1
        print(f"Runtime crosswalk is current: {OUTPUT.relative_to(PROJECT_ROOT)}")
        return 0

    OUTPUT.write_text(expected, encoding="utf-8", newline="")
    print(f"Wrote {len(source)} rows to {OUTPUT.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
