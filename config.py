### config.py
"""Define the pipeline's data sources, metrics, and output settings.

Imported by main.py to configure API requests, period limits, and file locations.
"""

from pathlib import Path


DATA_DIRECTORY = Path("data")
CONJUNCTUURKLOK_FILE = Path("table-conjunctuur-indicator.csv")
PANEL_DATA_FILE = DATA_DIRECTORY / "panel_data.csv"

PANEL_START_PERIOD = "201001"
PANEL_END_PERIOD = "202512"

CBS_COUNTRY_NAME_REPLACEMENTS = {
    "Polen": "Poland",
}

CBS_TABLES = [
    {
        "id": "85484NED",
        "country_column": "Herkomstland",
        "country_codes_endpoint": "HerkomstlandCodes",
        "country_codes_file_stem": "herkomstland_codes",
        "params": {
            "$filter": (
                "Measure eq 'M000167' "
                "and substring(Perioden,4,2) eq 'MM' "
                "and Geboorteland eq 'T001638' "
                "and Geslacht eq 'T001038' "
                "and Herkomstland eq 'H008718'"
            )
        },
    },
    {
        "id": "83518NED",
        "country_column": "Migratieachtergrond",
        "country_codes_endpoint": "MigratieachtergrondCodes",
        "country_codes_file_stem": "migratieachtergrond_codes",
        "params": {
            "$filter": (
                "Measure eq 'M000167' "
                "and substring(Perioden,4,2) eq 'MM' "
                "and Generatie eq 'T001040' "
                "and Geslacht eq 'T001038' "
                "and Migratieachtergrond eq 'H008718'"
            )
        },
    },
]

EUROSTAT_COUNTRY_NAME_REPLACEMENTS = {
    "NL": "Netherlands",
    "PL": "Poland",
}

EUROSTAT_METRICS = [
    {
        "id": "earn_mw_cur",
        "metric_name": "MINWAGE",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "S",
        "params": [
            ("freq", "S"),
            ("currency", "PPS"),
            ("geo", "NL"),
            ("geo", "PL"),
            ("lang", "en"),
        ],
    },
    {
        "id": "lc_lci_r2_q",
        "metric_name": "WAGESAL",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "Q",
        "params": [
            ("freq", "Q"),
            ("s_adj", "SCA"),
            ("unit", "I20"),
            ("nace_r2", "B-S"),
            ("lcstruct", "D11"),
            ("geo", "NL"),
            ("geo", "PL"),
            ("lang", "en"),
        ],
    },
]
