# debug.py

import logging

import pandas as pd

from settings import DEBUG


logger = logging.getLogger("immigration_data")
logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)

if not logger.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter("[%(levelname)s] %(message)s")
    )
    logger.addHandler(handler)

logger.propagate = False


def debug(message, *args):
    """Print a debug message when debug mode is enabled."""
    logger.debug(message, *args)


def debug_frame(name, df, sample=5):
    """Inspect the structure and contents of a DataFrame."""
    if not DEBUG:
        return

    debug("=== %s ===", name)
    debug("Shape: %s", df.shape)
    debug("Columns: %s", df.columns.tolist())
    debug("Dtypes:\n%s", df.dtypes.to_string())
    debug("Missing values:\n%s", df.isna().sum().to_string())


def debug_coverage(name, df, value_column):
    """Inspect country and period coverage."""
    if not DEBUG:
        return

    coverage = (
        df.groupby("Country")
        .agg(
            start=("Period", "min"),
            end=("Period", "max"),
            rows=("Period", "size"),
            missing=(value_column, lambda x: x.isna().sum()),
        )
    )

    debug("=== %s coverage ===\n%s", name, coverage.to_string())


def debug_duplicates(name, df, keys):
    """Report duplicate keys without modifying the data."""
    if not DEBUG:
        return

    duplicates = df.loc[
        df.duplicated(keys, keep=False)
    ]

    debug(
        "%s: %d rows with duplicate keys %s",
        name,
        len(duplicates),
        keys,
    )

    if not duplicates.empty:
        debug(
            "Duplicate examples:\n%s",
            duplicates.head(10).to_string(index=False),
        )

def validate_panel(df, expected_countries):
    """Check fundamental panel assumptions in debug mode."""
    if not DEBUG:
        return

    required = {"Period", "Country", "Immigration"}
    assert required.issubset(df.columns), "Missing core columns"

    assert not df.duplicated(
        ["Period", "Country"]
    ).any(), "Duplicate country-month observations"

    assert set(df["Country"]) == set(
        expected_countries
    ), "Country coverage differs from settings"

    assert df["Immigration"].notna().all(), (
        "Missing immigration observations"
    )

    assert df["Immigration"].ge(0).all(), (
        "Negative immigration observations"
    )

    debug("Final panel validation passed")