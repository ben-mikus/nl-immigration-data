
from cbs import (
    extract_and_standardize_immigration,
)
from config import (
    CBS_COUNTRY_NAME_REPLACEMENTS,
    CBS_TABLES,
    CONJUNCTUURKLOK_FILE,
    DATA_DIRECTORY,
    EUROSTAT_COUNTRY_NAME_REPLACEMENTS,
    EUROSTAT_METRICS,
    PANEL_DATA_FILE,
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
            DATA_DIRECTORY,
        )
        for table in CBS_TABLES
    ]
    panel = ImmigrationPanel(standardized_sources)

    for metric in EUROSTAT_METRICS:
        standardized_metric = extract_and_standardize_metric(
            metric,
            EUROSTAT_COUNTRY_NAME_REPLACEMENTS,
            DATA_DIRECTORY,
        )
        panel.absorb_country_metric(
            standardized_metric,
            metric["metric_name"],
            metric["benchmark_country"],
            metric["benchmark_label"],
        )

    panel.absorb_national_metric(
        load_conjunctuurklok(CONJUNCTUURKLOK_FILE),
        "Conjunctuurklok",
    )
    panel.to_csv(PANEL_DATA_FILE)
    return panel


if __name__ == "__main__":
    main()
