from pathlib import Path


DATA_DIRECTORY = Path("data")
CONJUNCTUURKLOK_FILE = Path("table-conjunctuur-indicator.csv")
PANEL_DATA_FILE = DATA_DIRECTORY / "panel_data.csv"

CBS_COUNTRY_NAME_REPLACEMENTS = {
    "Bulgarije": "Bulgaria",
    "Polen": "Poland",
    "Roemenië": "Romania",
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
                "and ("
                "Herkomstland eq 'H008718' "
                "or Herkomstland eq 'H008567' "
                "or Herkomstland eq 'H008723' "
                ")"
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
                "and ("
                "Migratieachtergrond eq 'H008718' "
                "or Migratieachtergrond eq 'H008567' "
                "or Migratieachtergrond eq 'H008723' "
                ")"
            )
        },
    },
]

EUROSTAT_COUNTRY_NAME_REPLACEMENTS = {
    "NL": "Netherlands",
    "PL": "Poland",
    "BG": "Bulgaria",
    "RO": "Romania",
}

EUROSTAT_METRICS = [
    {
        "id": "une_rt_m",
        "metric_name": "Unemployment",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "params": [
            ("freq", "M"),
            ("s_adj", "SA"),
            ("unit", "PC_ACT"),
            ("sex", "T"),
            ("age", "TOTAL"),
            ("geo", "NL"),
            ("geo", "PL"),
            ("geo", "BG"),
            ("geo", "RO"),
            ("sinceTimePeriod", "1995-01"),
            ("lang", "en"),
        ],
    },
    {
        "id": "prc_hicp_minr",
        "metric_name": "HICP-Monthly-Change",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "params": [
            ("freq", "M"),
            ("unit", "RCH_M"),
            ("coicop18", "TOTAL"),
            ("geo", "NL"),
            ("geo", "PL"),
            ("geo", "BG"),
            ("geo", "RO"),
            ("sinceTimePeriod", "1995-01"),
            ("lang", "en"),
        ],
    },
    {
        "id": "sts_inpr_m",
        "metric_name": "Industrial-Production",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "params": [
            ("freq", "M"),
            ("indic_bt", "PRD"),
            ("nace_r2", "B-D"),
            ("s_adj", "SCA"),
            ("unit", "I21"),
            ("geo", "NL"),
            ("geo", "PL"),
            ("geo", "BG"),
            ("geo", "RO"),
            ("lang", "en"),
        ],
    },
    {
        "id": "prc_hpi_q",
        "metric_name": "House-Price-Index",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "Q",
        "params": [
            ("freq", "Q"),
            ("purchase", "TOTAL"),
            ("unit", "I15_Q"),
            ("geo", "NL"),
            ("geo", "PL"),
            ("geo", "BG"),
            ("geo", "RO"),
            ("lang", "en"),
        ],
    },
    {
        "id": "jvs_q_r21",
        "metric_name": "Job-Vacancy-Rate",
        "benchmark_country": "Netherlands",
        "benchmark_label": "NL",
        "frequency": "Q",
        "params": [
            ("freq", "Q"),
            ("nace_r2_1", "A-T"),
            ("sizeclas", "TOTAL"),
            ("s_adj", "SA"),
            ("indic_em", "JVR"),
            ("geo", "NL"),
            ("geo", "PL"),
            ("geo", "BG"),
            ("geo", "RO"),
            ("lang", "en"),
        ],
    },
]
