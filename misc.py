import pandas as pd


def load_conjunctuurklok(source_file):
    """Load and standardize local Conjunctuurklok observations."""
    return standardize_conjunctuurklok(pd.read_csv(source_file))


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
        "20" + abbreviated_months["year"]
        + abbreviated_months["month"].map(english_months)
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
