### cbs.py

import pandas as pd
import requests


def get_odata(target_url, params=None):
    frames = []
    while target_url:
        response = requests.get(target_url, params=params)
        response.raise_for_status()

        payload = response.json()
        frames.append(pd.DataFrame(payload["value"]))

        target_url = payload.get("@odata.nextLink")
        params = None

    return pd.concat(frames, ignore_index=True)


def standardize_monthly_period(periods):
    """Convert CBS monthly period codes such as 2022MM01 to YYYYMM strings."""
    period_values = periods.astype("string")
    matches = period_values.str.fullmatch(r"\d{4}MM(0[1-9]|1[0-2])")

    if not matches.fillna(False).all():
        invalid_periods = period_values.loc[~matches.fillna(False)].unique().tolist()
        raise ValueError(f"Invalid CBS monthly period codes: {invalid_periods}")

    return period_values.str.replace("MM", "", regex=False)


def replace_dimension_codes(values, code_table, replacements=None):
    """Replace CBS dimension identifiers with their labels from a code table."""
    required_columns = {"Identifier", "Title"}
    missing_columns = required_columns.difference(code_table.columns)
    if missing_columns:
        raise ValueError(
            f"Code table is missing required columns: {sorted(missing_columns)}"
        )

    labels = code_table.set_index("Identifier")["Title"]
    standardized_values = values.map(labels)
    unknown_codes = values.loc[standardized_values.isna()].unique().tolist()
    if unknown_codes:
        raise ValueError(f"No labels found for CBS codes: {unknown_codes}")

    if replacements:
        standardized_values = standardized_values.replace(replacements)

    return standardized_values


def standardize_immigration_observations(
    observations,
    country_codes,
    country_name_replacements=None,
    country_column="Herkomstland",
):
    """Create core monthly country-panel fields from CBS immigration observations."""
    required_columns = {"Perioden", country_column, "Value"}
    missing_columns = required_columns.difference(observations.columns)
    if missing_columns:
        raise ValueError(
            f"Observations are missing required columns: {sorted(missing_columns)}"
        )

    standardized = pd.DataFrame(
        {
            "Period": standardize_monthly_period(observations["Perioden"]),
            "Country": replace_dimension_codes(
                observations[country_column],
                country_codes,
                country_name_replacements,
            ),
            "Immigration": pd.to_numeric(observations["Value"], errors="raise"),
        }
    )

    if standardized.duplicated(["Period", "Country"]).any():
        raise ValueError("Observations contain duplicate Period/Country combinations")

    return standardized.sort_values(
        by=["Country", "Period"],
        ascending=False,
        ignore_index=True
    )


def combine_panel_sources(*sources):
    """Combine standardized panel sources, retaining values from earlier sources."""
    if not sources:
        raise ValueError("At least one standardized panel source is required")

    combined = pd.concat(sources, ignore_index=True)
    required_columns = {"Period", "Country", "Immigration"}
    missing_columns = required_columns.difference(combined.columns)
    if missing_columns:
        raise ValueError(
            f"Standardized sources are missing required columns: {sorted(missing_columns)}"
        )

    combined = combined.drop_duplicates(["Period", "Country"], keep="first")
    return combined.sort_values(["Country", "Period"], ignore_index=True)


def layer_country_metric(
    panel,
    metric_data,
    metric_name,
    benchmark_country,
    benchmark_label="NL",
):
    """Layer a benchmark and country-specific metric onto a country-month panel."""
    panel_required_columns = {"Period", "Country"}
    metric_required_columns = {"Period", "Country", metric_name}
    missing_panel_columns = panel_required_columns.difference(panel.columns)
    missing_metric_columns = metric_required_columns.difference(metric_data.columns)
    if missing_panel_columns:
        raise ValueError(
            f"Panel is missing required columns: {sorted(missing_panel_columns)}"
        )
    if missing_metric_columns:
        raise ValueError(
            f"Metric data is missing required columns: {sorted(missing_metric_columns)}"
        )
    if metric_data.duplicated(["Period", "Country"]).any():
        raise ValueError("Metric data contains duplicate Period/Country combinations")

    benchmark_column = f"{benchmark_label}-{metric_name}"
    country_column = f"Country-{metric_name}"
    difference_column = f"Diff-{metric_name}"

    benchmark_metric = metric_data.loc[
        metric_data["Country"].eq(benchmark_country),
        ["Period", metric_name],
    ].rename(columns={metric_name: benchmark_column})
    country_metric = metric_data.loc[
        ~metric_data["Country"].eq(benchmark_country),
        ["Period", "Country", metric_name],
    ].rename(columns={metric_name: country_column})

    layered = panel.merge(country_metric, on=["Period", "Country"], how="left")
    layered = layered.merge(benchmark_metric, on="Period", how="left")
    layered[difference_column] = (
        layered[country_column] - layered[benchmark_column]
    )
    return layered


def standardize_conjunctuurklok(observations):
    """Convert Conjunctuurklok CSV values to monthly panel fields."""
    required_columns = {"Periode", "Cyclus"}
    missing_columns = required_columns.difference(observations.columns)
    if missing_columns:
        raise ValueError(
            f"Conjunctuurklok data is missing required columns: {sorted(missing_columns)}"
        )

    values = pd.to_numeric(
        observations["Cyclus"].astype("string").str.replace(",", ".", regex=False),
        errors="coerce",
    )
    data_rows = observations.loc[values.notna()].copy()
    values = values.loc[values.notna()]
    periods = data_rows["Periode"].astype("string").str.strip()

    dutch_months = {
        "januari": "01",
        "februari": "02",
        "maart": "03",
        "april": "04",
        "mei": "05",
        "juni": "06",
        "juli": "07",
        "augustus": "08",
        "september": "09",
        "oktober": "10",
        "november": "11",
        "december": "12",
    }
    english_months = {
        "Jan": "01",
        "Feb": "02",
        "Mar": "03",
        "Apr": "04",
        "May": "05",
        "Jun": "06",
        "Jul": "07",
        "Aug": "08",
        "Sep": "09",
        "Oct": "10",
        "Nov": "11",
        "Dec": "12",
    }

    full_months = periods.str.extract(
        r"^(?P<month>[a-z]+) (?P<year>\d{4})$", expand=True
    )
    abbreviated_months = periods.str.extract(
        r"^(?P<month>[A-Z][a-z]{2})-(?P<year>\d{2})$", expand=True
    )
    standardized_periods = (
        full_months["year"] + full_months["month"].map(dutch_months)
    ).fillna(
        "20" + abbreviated_months["year"] + abbreviated_months["month"].map(english_months)
    )

    if standardized_periods.isna().any():
        invalid_periods = periods.loc[standardized_periods.isna()].unique().tolist()
        raise ValueError(f"Invalid Conjunctuurklok periods: {invalid_periods}")

    return pd.DataFrame(
        {
            "Period": standardized_periods,
            "Conjunctuurklok": values,
        }
    )


def layer_national_metric(panel, metric_data, metric_name, country_label="NL"):
    """Layer a monthly national metric onto each matching country-panel row."""
    panel_required_columns = {"Period", "Country"}
    metric_required_columns = {"Period", metric_name}
    missing_panel_columns = panel_required_columns.difference(panel.columns)
    missing_metric_columns = metric_required_columns.difference(metric_data.columns)
    if missing_panel_columns:
        raise ValueError(
            f"Panel is missing required columns: {sorted(missing_panel_columns)}"
        )
    if missing_metric_columns:
        raise ValueError(
            f"Metric data is missing required columns: {sorted(missing_metric_columns)}"
        )
    if metric_data.duplicated(["Period"]).any():
        raise ValueError("National metric data contains duplicate periods")

    return panel.merge(
        metric_data.rename(columns={metric_name: f"{country_label}-{metric_name}"}),
        on="Period",
        how="left",
    )