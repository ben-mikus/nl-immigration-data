
# features.py

import numpy as np
import pandas as pd

from settings import FEATURE_PERIODS
from debug import debug


def difference(data, column, months):
    """Absolute change within each country over N calendar months."""
    return data.groupby("Country")[column].diff(months)


def percentage_change(data, column, months):
    """Percentage change within each country over N calendar months."""
    return (
        data.groupby("Country")[column]
        .pct_change(months, fill_method=None) * 100
    )


def engineer_features(data):
    """Add economic features to the assembled country-month panel."""

    data = data.copy()
    data = data.sort_values(["Country", "Period"]).reset_index(drop=True)

    debug("=== Engineering Economic Features ===")

    # Unemployment
    if {"Country-UNEMP", "NL-UNEMP"} <= set(data.columns):
        data["UNEMP-GAP"] = data["Country-UNEMP"] - data["NL-UNEMP"]

        months = FEATURE_PERIODS["UNEMP"]

        data["UNEMP-CHANGE"] = difference(
            data, "Country-UNEMP", months
        )
        data["NL-UNEMP-CHANGE"] = difference(
            data, "NL-UNEMP", months
        )

    # Job vacancies
    if {"Country-JOBVAC", "NL-JOBVAC"} <= set(data.columns):
        data["JOBVAC-GAP"] = (
            data["NL-JOBVAC"] - data["Country-JOBVAC"]
        )

    # Wages and salaries
    if {"Country-WAGESAL", "NL-WAGESAL"} <= set(data.columns):
        months = FEATURE_PERIODS["WAGESAL"]

        data["WAGESAL-GROWTH"] = percentage_change(
            data, "Country-WAGESAL", months
        )
        data["NL-WAGESAL-GROWTH"] = percentage_change(
            data, "NL-WAGESAL", months
        )

    # Inflation
    if {"Country-HICP", "NL-HICP"} <= set(data.columns):
        months = FEATURE_PERIODS["HICP"]

        data["Country-INFLATION"] = percentage_change(
            data, "Country-HICP", months
        )
        data["NL-INFLATION"] = percentage_change(
            data, "NL-HICP", months
        )
        data["HICP-GAP"] = (
            data["Country-INFLATION"] - data["NL-INFLATION"]
        )

    # Minimum wages
    if {"Country-MINWAGE", "NL-MINWAGE"} <= set(data.columns):
        data["MINWAGE-RATIO"] = (
            data["NL-MINWAGE"]
            / data["Country-MINWAGE"].replace(0, np.nan)
        )

    # GDP: already a quarter-on-quarter growth percentage
    if {"Country-GDP", "NL-GDP"} <= set(data.columns):
        data["GDP-GROWTH-GAP"] = (
            data["NL-GDP"] - data["Country-GDP"]
        )

    debug(
        "Engineered feature columns: %s",
        sorted(set(data.columns) - {
            "Period", "Country", "Immigration"
        }),
    )

    return data
