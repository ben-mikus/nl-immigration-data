### main.py
"""Build and export the configured immigration analysis panel.

Run this module to retrieve source data, merge it, apply period bounds, and write CSV output.
"""

from cbs import (
    extract_and_standardize_immigration,
)
from config import (
    CBS_COUNTRY_NAME_REPLACEMENTS,
    CBS_TABLES,
    CONJUNCTUURKLOK_FILE,
    EUROSTAT_COUNTRY_NAME_REPLACEMENTS,
    EUROSTAT_METRICS,
    PANEL_DATA_FILE,
    PANEL_END_PERIOD,
    PANEL_START_PERIOD,
)
from dataset import ImmigrationPanel
from eurostat import (
    extract_and_standardize_metric,
)
from misc import load_conjunctuurklok


def main():
    standardized_sources = [
        extract_and_standardize_immigration(
            table,
            CBS_COUNTRY_NAME_REPLACEMENTS,
        )
        for table in CBS_TABLES
    ]
    panel = ImmigrationPanel(standardized_sources)

    for metric in EUROSTAT_METRICS:
        standardized_metric = extract_and_standardize_metric(
            metric,
            EUROSTAT_COUNTRY_NAME_REPLACEMENTS,
        )
        panel.absorb_country_metric(
            standardized_metric,
            metric["metric_name"],
            metric["benchmark_country"],
            metric["benchmark_label"],
        )

    panel.absorb_national_metric(
        load_conjunctuurklok(CONJUNCTUURKLOK_FILE),
        "CONJCLK",
    )
    panel.restrict_periods(PANEL_START_PERIOD, PANEL_END_PERIOD)
    panel.to_csv(PANEL_DATA_FILE)
    return panel


if __name__ == "__main__":
    main()
