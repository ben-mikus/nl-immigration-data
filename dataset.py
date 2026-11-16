### dataset.py
"""Assemble, filter, and export the immigration analysis panel.

Used by main.py to merge immigration observations with configured economic metrics.
"""

import re

import pandas as pd

from features import engineer_features
from debug import (
    debug,
    debug_frame,
    debug_coverage,
    debug_duplicates,
)



class ImmigrationPanel:
    """Assemble immigration observations and related monthly metrics."""

    def __init__(self, sources):
        
        if not sources:
            raise ValueError("At least one standardized panel source is required")

        combined = pd.concat(sources, ignore_index=True)

        debug_duplicates(
            "Combined CBS observations",
            combined,
            ["Period", "Country"],
        )

        if len(sources) > 1:
            labeled = pd.concat(
                [
                    source.assign(Source=f"CBS source {i + 1}")
                    for i, source in enumerate(sources)
                ],
                ignore_index=True,
            )

            comparison = (
                labeled.groupby(["Period", "Country"])
                .agg(
                    source_count=("Source", "nunique"),
                    distinct_values=("Immigration", "nunique"),
                    minimum=("Immigration", "min"),
                    maximum=("Immigration", "max"),
                )
                .reset_index()
            )

            overlap = comparison.loc[
                comparison["source_count"] > 1
            ]

            disagreements = overlap.loc[
                overlap["distinct_values"] > 1
            ]

            debug("Overlapping CBS country-months: %d", len(overlap))
            debug("Disagreeing CBS country-months: %d", len(disagreements))

            if not disagreements.empty:
                debug(
                    "CBS disagreements:\n%s",
                    disagreements.head(20).to_string(index=False),
                )

        required_columns = {"Period", "Country", "Immigration"}
        missing_columns = required_columns.difference(combined.columns)
        if missing_columns:
            raise ValueError(
                f"Standardized sources are missing required columns: {sorted(missing_columns)}"
            )

        self.data = combined.drop_duplicates(["Period", "Country"], keep="first")
        self.data = self.data.sort_values(["Country", "Period"], ignore_index=True)

    def absorb_country_metric(
        self,
        metric_data,
        metric_name,
        benchmark_country,
        benchmark_label="NL",
    ):
        """Add country and benchmark metric fields."""
        required_columns = {"Period", "Country", metric_name}
        missing_columns = required_columns.difference(metric_data.columns)
        if missing_columns:
            raise ValueError(
                f"Metric data is missing required columns: {sorted(missing_columns)}"
            )
        if metric_data.duplicated(["Period", "Country"]).any():
            raise ValueError("Metric data contains duplicate Period/Country combinations")

        benchmark_column = f"{benchmark_label}-{metric_name}"
        country_column = f"Country-{metric_name}"

        benchmark_metric = metric_data.loc[
            metric_data["Country"].eq(benchmark_country),
            ["Period", metric_name],
        ].rename(columns={metric_name: benchmark_column})

        debug(
            "%s Dutch benchmark observations: %d",
            metric_name,
            len(benchmark_metric),
        )

        debug(
            "%s benchmark missing values: %d",
            metric_name,
            benchmark_metric[benchmark_column].isna().sum(),
        )

        debug_duplicates(
            f"{metric_name} Dutch benchmark",
            benchmark_metric,
            ["Period"],
        )

        country_metric = metric_data.loc[
            ~metric_data["Country"].eq(benchmark_country),
            ["Period", "Country", metric_name],
        ].rename(columns={metric_name: country_column})

        debug("=== Merging %s ===", metric_name)
        debug("Panel rows before merge: %d", len(self.data))

        debug_duplicates(
            f"{metric_name} source",
            metric_data,
            ["Period", "Country"],
        )

        self.data = self.data.merge(
            country_metric,
            on=["Period", "Country"],
            how="left",
        )
        self.data = self.data.merge(benchmark_metric, on="Period", how="left")

        debug("Panel rows after merge: %d", len(self.data))

        debug(
            "%s missing country values: %d",
            metric_name,
            self.data[country_column].isna().sum(),
        )

        debug(
            "%s missing benchmark values: %d",
            metric_name,
            self.data[benchmark_column].isna().sum(),
        )

        debug_coverage(
            f"{metric_name} merged country values",
            self.data,
            country_column,
        )

    def absorb_national_metric(self, metric_data, metric_name, country_label="NL"):
        """Add a national monthly metric to every matching country-panel row."""
        required_columns = {"Period", metric_name}
        missing_columns = required_columns.difference(metric_data.columns)
        if missing_columns:
            raise ValueError(
                f"Metric data is missing required columns: {sorted(missing_columns)}"
            )
        if metric_data.duplicated(["Period"]).any():
            raise ValueError("National metric data contains duplicate periods")

        self.data = self.data.merge(
            metric_data.rename(columns={metric_name: f"{country_label}-{metric_name}"}),
            on="Period",
            how="left",
        )

    def engineer_features(self):
        """Apply configured economic feature transformations."""
        self.data = engineer_features(self.data)

    def restrict_periods(self, start_period=None, end_period=None):
        """Keep observations within inclusive YYYYMM period bounds."""
        for bound_name, period in (
            ("start_period", start_period),
            ("end_period", end_period),
        ):
            if period is not None and (
                not isinstance(period, str)
                or not re.fullmatch(r"\d{4}(0[1-9]|1[0-2])", period)
            ):
                raise ValueError(
                    f"{bound_name} must be a YYYYMM string with a valid month"
                )

        if start_period and end_period and start_period > end_period:
            raise ValueError("start_period must not be later than end_period")

        periods = self.data["Period"].astype("string")
        within_bounds = pd.Series(True, index=self.data.index)
        if start_period:
            within_bounds &= periods >= start_period
        if end_period:
            within_bounds &= periods <= end_period

        self.data = self.data.loc[within_bounds].reset_index(drop=True)

        debug(
            "Filtered period range: %s to %s",
            self.data["Period"].min(),
            self.data["Period"].max(),
        )

        debug("Rows remaining: %d", len(self.data))

    def restrict_countries(self, countries):
        """Keep observations for the specified countries only."""

        debug(
            "Countries before restriction: %s",
            sorted(self.data["Country"].unique().tolist()),
        )

        debug("Requested countries: %s", countries)

        self.data = (
            self.data.loc[self.data["Country"].isin(countries)]
            .reset_index(drop=True)
        )

        debug(
            "Countries after restriction: %s",
            sorted(self.data["Country"].unique().tolist()),
        )

        debug("Rows remaining: %d", len(self.data))

    def to_csv(self, output_file):
        """Write the assembled panel without its DataFrame index."""
        output_file.parent.mkdir(parents=True, exist_ok=True)
        self.data.to_csv(output_file, index=False)
