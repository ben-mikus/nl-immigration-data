### config.py
"""Defines the API configuration."""


from pathlib import Path


DATA_DIRECTORY = Path("data")
CONJUNCTUURKLOK_FILE = Path("table-conjunctuur-indicator.csv")
PANEL_DATA_FILE = DATA_DIRECTORY / "panel_data.csv"

PANEL_START_PERIOD = "201001"
PANEL_END_PERIOD = "202512"

CBS_COUNTRY_NAME_REPLACEMENTS = {
    "Bulgarije": "Bulgaria",
    "Duitsland": "Germany",
    "Italië": "Italy",
    "Polen": "Poland",
    "Roemenië": "Romania",
    "Spanje": "Spain"
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
                "and (Herkomstland eq 'H008567' "
                "or Herkomstland eq 'H008592' "
                "or Herkomstland eq 'H008636' "
                "or Herkomstland eq 'H008718' "
                "or Herkomstland eq 'H008723' "
                "or Herkomstland eq 'H008749')"
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
                "and (Migratieachtergrond eq 'H008567' "
                "or Migratieachtergrond eq 'H008592' "
                "or Migratieachtergrond eq 'H008636' "
                "or Migratieachtergrond eq 'H008718' "
                "or Migratieachtergrond eq 'H008723'"
                "or Migratieachtergrond eq 'H008749' "
                ")"
            )
        },
    },
]

EUROSTAT_COUNTRY_CODES = {
    "NL": "Netherlands",
    "BG": "Bulgaria",
    "DE": "Germany",
    "IT": "Italy",
    "PL": "Poland",
    "RO": "Romania",
    "ES": "Spain"
}

EUROSTAT_METRICS = {
    "Monthly Minimum Wages": {
        "id": "earn_mw_cur",
        "metric_name": "MINWAGE",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "S",
        "params": [
            ("freq", "S"),
            ("currency", "PPS"),
            *[("geo", c) for c in
            ("NL", "BG", "PL", "RO", "DE", "IT", "ES")],
            ("lang", "en"),
        ],
    },
    "Nominal Labour Cost Index": {
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
            *[("geo", c) for c in
            ("NL", "BG", "PL", "RO", "DE", "IT", "ES")],
            ("lang", "en"),
        ],
    },
    "Unemployment Rate": {
        "id": "une_rt_m",
        "metric_name": "UNEMP",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "M",
        "params": [
            ("freq", "M"),
            ("s_adj", "SA"),
            ("age", "TOTAL"),
            ("sex", "T"),
            ("unit", "PC_ACT"),
            *[("geo", c) for c in
            ("NL", "BG", "PL", "RO", "DE", "IT", "ES")],
            ("lang", "en"),
        ],
    },

    "Job Vacancy Rate": {
        "id": "jvs_q_r21",
        "metric_name": "JOBVAC",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "Q",
        "params": [
            ("freq", "Q"),
            ("s_adj", "SA"),
            ("nace_r2_1", "B-T"),
            ("sizeclas", "TOTAL"),
            ("indic_em", "JOBRATE"),
            *[("geo", c) for c in
            ("NL", "BG", "PL", "RO", "DE", "IT", "ES")],
            ("lang", "en"),
        ],
    },

    "Consumer Price Index": {
        "id": "prc_hicp_midx",
        "metric_name": "HICP",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "M",
        "params": [
            ("freq", "M"),
            ("unit", "I15"),
            ("coicop", "CP00"),
            *[("geo", c) for c in
            ("NL", "BG", "PL", "RO", "DE", "IT", "ES")],
            ("lang", "en"),
        ],
    },

    "Real GDP Growth": {
        "id": "namq_10_gdp",
        "metric_name": "GDP",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "Q",
        "params": [
            ("freq", "Q"),
            ("s_adj", "SCA"),
            ("unit", "CLV_PCH_PRE"),
            ("na_item", "B1G"),
            *[("geo", c) for c in
            ("NL", "BG", "PL", "RO", "DE", "IT", "ES")],
            ("lang", "en"),
        ],
    },
}
