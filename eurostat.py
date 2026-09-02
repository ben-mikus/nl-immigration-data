### eurostat.py

import pandas as pd
import requests
from itertools import product


def jsonstat_to_dataframe(payload):
    dimensions = payload["id"]

    categories = {}

    for dimension in dimensions:
        index = payload["dimension"][dimension]["category"]["index"]

        # JSON-stat index can be either a dict or list
        if isinstance(index, dict):
            categories[dimension] = [
                key
                for key, position in sorted(
                    index.items(),
                    key=lambda item: item[1]
                )
            ]
        else:
            categories[dimension] = index

    combinations = list(
        product(*(categories[dim] for dim in dimensions))
    )

    df = pd.DataFrame(
        combinations,
        columns=dimensions
    )

    # Eurostat may omit missing observations from the value dictionary
    values = payload.get("value", {})

    if isinstance(values, dict):
        df["value"] = [
            values.get(str(i))
            for i in range(len(df))
        ]
    else:
        df["value"] = values

    return df


def get_eurostat(dataset_id, params):
    base_url = (
        "https://ec.europa.eu/eurostat/api/dissemination/"
        "statistics/1.0/data"
    )

    target_url = f"{base_url}/{dataset_id}"

    response = requests.get(
        target_url,
        params=params
    )
    response.raise_for_status()

    return jsonstat_to_dataframe(response.json())


def standardize_eurostat_observations(
    observations, metric_name, country_replacements, frequency="M"
):
    """Convert a Eurostat country-month metric to panel-compatible fields."""
    required_columns = {"time", "geo", "value"}
    missing_columns = required_columns.difference(observations.columns)
    if missing_columns:
        raise ValueError(
            f"Observations are missing required columns: {sorted(missing_columns)}"
        )

    periods = observations["time"].astype("string")
    countries = observations["geo"].map(country_replacements)
    unknown_countries = observations.loc[countries.isna(), "geo"].unique().tolist()
    if unknown_countries:
        raise ValueError(f"No country names found for Eurostat codes: {unknown_countries}")

    if frequency == "M":
        panel_periods = standardize_monthly_periods(periods)
    elif frequency == "Q":
        observations = observations.loc[observations.index.repeat(3)].reset_index(
            drop=True
        )
        countries = countries.loc[countries.index.repeat(3)].reset_index(drop=True)
        panel_periods = expand_quarterly_periods(periods)
    else:
        raise ValueError(f"Unsupported Eurostat frequency: {frequency}")

    return pd.DataFrame(
        {
            "Period": panel_periods,
            "Country": countries,
            metric_name: pd.to_numeric(observations["value"], errors="raise"),
        }
    )


def standardize_monthly_periods(periods):
    """Convert Eurostat monthly periods such as 2022-01 to YYYYMM strings."""
    valid_periods = periods.str.fullmatch(r"\d{4}-(0[1-9]|1[0-2])")
    if not valid_periods.fillna(False).all():
        invalid_periods = periods.loc[~valid_periods.fillna(False)].unique().tolist()
        raise ValueError(f"Invalid Eurostat monthly periods: {invalid_periods}")

    return periods.str.replace("-", "", regex=False)


def expand_quarterly_periods(periods):
    """Repeat quarterly values across their calendar-quarter months."""
    valid_periods = periods.str.fullmatch(r"\d{4}-Q[1-4]")
    if not valid_periods.fillna(False).all():
        invalid_periods = periods.loc[~valid_periods.fillna(False)].unique().tolist()
        raise ValueError(f"Invalid Eurostat quarterly periods: {invalid_periods}")

    return pd.Series(
        [
            f"{period[:4]}{month:02d}"
            for period in periods
            for month in range((int(period[-1]) - 1) * 3 + 1, int(period[-1]) * 3 + 1)
        ],
        dtype="string",
    )


country_name_replacements = {
    "NL": "Netherlands",
    "PL": "Poland",
    "BG": "Bulgaria",
    "RO": "Romania",
}

eurostat_metrics = [
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
