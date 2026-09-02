### cbs.py

import pandas as pd
import requests


def extract_and_standardize_immigration(
    table,
    country_name_replacements,
    output_directory,
):
    """Retrieve one configured CBS table and return standardized immigration data."""
    output_directory.mkdir(parents=True, exist_ok=True)
    table_url = f"https://datasets.cbs.nl/odata/v1/CBS/{table['id']}"
    observations = get_odata(f"{table_url}/Observations", table["params"])
    observations.to_csv(output_directory / f"{table['id']}.csv", index=False)

    country_codes = get_odata(f"{table_url}/{table['country_codes_endpoint']}")
    country_codes.to_csv(
        output_directory / f"{table['id']}_{table['country_codes_file_stem']}.csv",
        index=False,
    )

    return standardize_immigration_observations(
        observations,
        country_codes,
        country_name_replacements,
        table["country_column"],
    )


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

    return standardized.sort_values(["Country", "Period"], ignore_index=True)