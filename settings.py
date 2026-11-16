### settings.py
"""Used by the user to define the contents of the dataset."""


DEBUG = True

FEATURE_ENGINEERING = True

FEATURE_PERIODS = {
    "UNEMP": 12,
    "WAGESAL": 12,
    "HICP": 12,
}

COUNTRIES = [
    "Bulgaria",
    "Germany",
    "Italy",
    "Poland",
    "Romania",
    "Spain"
]

CONJUNCTUURKLOK = True

METRICS = [
    "Monthly Minimum Wages",
    "Nominal Labour Cost Index",
    "Unemployment Rate",
    "Consumer Price Index",
    "Real GDP Growth",
]